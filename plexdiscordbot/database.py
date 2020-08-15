from discord.ext.commands import Bot
import plex
import psycopg2 as psql
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictCursor
import logging
from time import sleep
import os
import re
import thetvdb

conn: connection
cur: cursor


async def init(bot):
    while True:
        try:
            global conn
            conn = psql.connect(dbname=os.environ.get("POSTGRES_DB"), user=os.environ.get("POSTGRES_USER"),
                                password=os.environ.get("POSTGRES_PASSWORD"), host="postgres")
            logging.info("DB connected")
            break
        except psql.OperationalError:
            logging.info("Waiting 5 seconds for DB reconnect...")
            sleep(5)

    global cur
    cur = conn.cursor(cursor_factory=DictCursor)

    # If member table empty (i.e. first boot), update db
    cur.execute("""
        SELECT COUNT(*)
        FROM member
        LIMIT 1;
    """)

    if cur.fetchone()[0] == 0:
        await update_db(bot)


async def update_db(bot: Bot):
    logging.info("Updating DB...")

    # Insert tv shows
    tv_shows = await plex.get_all_tv_shows()

    for show in tv_shows:
        # Extract TheTVDB id from show guid
        thetvdb_id = re.findall(r"\d+", show.guid)[0]
        title = show.title

        # Get slug from TheTVDB     
        slug = thetvdb.get_series(thetvdb_id)["slug"]

        cur.execute("""
            INSERT INTO tv_show (thetvdb_id, title, slug)
            VALUES (%s, %s, %s);
        """, (thetvdb_id, title, slug))

    # Insert guild members
    for guild in bot.guilds:
        for member in guild.members:
            # Do not add bot id
            if member.id != bot.user.id:
                cur.execute("""
                    INSERT INTO member (discord_id)
                    VALUES (%s);
                """, (member.id,))

    conn.commit()


def get_all_tv_shows():
    cur.execute("""
        SELECT *
        FROM tv_show;
    """)

    return cur.fetchall()


def insert_member(discord_id):
    cur.execute("""
        INSERT INTO member (discord_id)
        VALUES (%s);
    """, (discord_id,))
    conn.commit()


def delete_member(discord_id):
    cur.execute("""
        DELETE FROM member
        WHERE discord_id = (%s);
    """, (discord_id,))
    conn.commit()


def search_tv_show(search):
    cur.execute("""
        SELECT *
        FROM tv_show
        WHERE title ILIKE %s;
    """, (f"%{search}%",))

    return cur.fetchall()


def get_member_id(discord_id):
    cur.execute("""
        SELECT member_id
        FROM member
        WHERE discord_id = (%s);
    """, (discord_id,))

    return cur.fetchone()[0]


def subscribe(member_id, tv_show_id):
    cur.execute("""
        INSERT INTO subscription (member_id, tv_show_id)
        VALUES (%s, %s);
    """, (member_id, tv_show_id))
    conn.commit()


def is_subscribed(member_id, tv_show_id):
    cur.execute("""
        SELECT COUNT(*)
        FROM subscription
        WHERE member_id = %s
        AND tv_show_id = %s
        LIMIT 1;
    """, (member_id, tv_show_id))

    return cur.fetchone()[0] == 1
