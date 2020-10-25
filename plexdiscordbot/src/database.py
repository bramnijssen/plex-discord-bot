from discord.ext.commands import Bot
import plex
import psycopg2 as psql
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictCursor
import logging
from time import sleep
from os import getenv

conn: connection
cur: cursor


def init():
    while True:
        try:
            global conn
            conn = psql.connect(dbname=getenv("POSTGRES_DB"), user=getenv("POSTGRES_USER"),
                                password=getenv("POSTGRES_PASSWORD"), host="postgres")
            logging.info("DB connected")
            break
        except psql.OperationalError:
            logging.info("Waiting 5 seconds for DB reconnect...")
            sleep(5)

    global cur
    cur = conn.cursor(cursor_factory=DictCursor)

    # If tv_show table empty (i.e. first boot), update db
    cur.execute("""
        SELECT COUNT(*)
        FROM tv_show
        LIMIT 1;
    """)

    if cur.fetchone()[0] == 0:
        update_db()


def update_db():
    logging.info("Updating DB...")

    # Insert tv shows
    tv_shows = plex.get_all_tv_shows()

    for show in tv_shows:
        key = show.ratingKey
        title = show.title

        cur.execute("""
            INSERT INTO tv_show (plex_key, title)
            VALUES (%s, %s);
        """, (key, title))

    conn.commit()


def get_all_tv_shows():
    cur.execute("""
        SELECT title
        FROM tv_show;
    """)

    return cur.fetchall()


def search_tv_show(search):
    cur.execute("""
        SELECT *
        FROM tv_show
        WHERE title ILIKE %s;
    """, (f"%{search}%",))

    return cur.fetchall()


def subscribe(discord_id, tv_show_id):
    cur.execute("""
        INSERT INTO subscription (discord_id, tv_show_id)
        VALUES (%s, %s);
    """, (discord_id, tv_show_id))

    conn.commit()


def is_subscribed(discord_id, tv_show_id):
    cur.execute("""
        SELECT COUNT(*)
        FROM subscription
        WHERE discord_id = %s
        AND tv_show_id = %s
        LIMIT 1;
    """, (discord_id, tv_show_id))

    return cur.fetchone()[0] == 1


def unsubscribe(discord_id, tv_show_id):
    cur.execute("""
        DELETE FROM subscription
        WHERE discord_id = %s
        AND tv_show_id = %s;
    """, (discord_id, tv_show_id))

    conn.commit()


def get_subscriptions(discord_id):
    cur.execute("""
        SELECT t.title
        FROM tv_show t
        INNER JOIN subscription s ON t.tv_show_id = s.tv_show_id
        WHERE s.discord_id = %s
    """, (discord_id,))

    return cur.fetchall()


def delete_subscriptions(discord_id):
    cur.execute("""
        DELETE FROM subscription
        WHERE discord_id = %s;
    """, (discord_id,))


def get_subscriptions_for_tv_show(key):
    cur.execute("""
        SELECT *
        FROM subscription 
        WHERE tv_show_id = (
            SELECT tv_show_id
            FROM tv_show
            WHERE plex_key = %s
        );
    """, (key,))

    return cur.fetchall()
