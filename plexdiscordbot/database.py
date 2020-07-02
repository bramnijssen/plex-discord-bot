import plex
import psycopg2 as psql
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictCursor
import os
import re
import logging

conn: connection
cur: cursor


async def init():
    await plex.init()

    global conn
    conn = psql.connect(dbname=os.environ.get("POSTGRES_DB"), user=os.environ.get("POSTGRES_USER"), password=os.environ.get("POSTGRES_PASSWORD"), host="postgres")

    global cur
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
        SELECT COUNT(*)
        FROM tv_show
        LIMIT 1;
    """)

    if cur.fetchone()[0] == 0:
        tv_shows = await plex.get_all_tv_shows()

        for show in tv_shows:
            thetvdb_id = re.findall(r"\d+", show.guid)[0]
            title = show.title

            cur.execute("""
                INSERT INTO tv_show (thetvdb_id, title)
                VALUES (%s, %s)
            """, (thetvdb_id, title))

        conn.commit()
