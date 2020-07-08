from discord.ext.commands import Bot
import plex
import psycopg2 as psql
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictCursor
import logging
from time import sleep
import os
import re

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
    # Insert tv shows
    tv_shows = await plex.get_all_tv_shows()

    for show in tv_shows:
        # Extract TheTVDB id from show guid
        thetvdb_id = re.findall(r"\d+", show.guid)[0]
        title = show.title

        cur.execute("""
            INSERT INTO tv_show (thetvdb_id, title)
            VALUES (%s, %s);
        """, (thetvdb_id, title))

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


def member_exists(discord_id):
    cur.execute("""
        SELECT COUNT(*)
        FROM member
        WHERE discord_id = (%s);
    """, (discord_id,))

    return cur.fetchone()[0] == 1


def insert_member(member):
    cur.execute("""
        INSERT INTO member (discord_id)
        VALUES (%s);
    """, (member.id,))
    conn.commit()
