import plex
import psycopg2 as psql
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictCursor
import os
import re

conn: connection
cur: cursor


async def init():
    # Init Plex 
    await plex.init()

    # Bind db connection to var
    global conn
    conn = psql.connect(dbname=os.environ.get("POSTGRES_DB"), user=os.environ.get("POSTGRES_USER"), password=os.environ.get("POSTGRES_PASSWORD"), host="postgres")

    # Bind dict cursor to var
    global cur
    cur = conn.cursor(cursor_factory=DictCursor)

    # If tv_show table empty (i.e. first boot), add all tv shows to db
    cur.execute("""
        SELECT COUNT(*)
        FROM tv_show
        LIMIT 1;
    """)

    if cur.fetchone()[0] == 0:
        await update_db()


async def update_db():
    tv_shows = await plex.get_all_tv_shows()

    for show in tv_shows:
        # Extract TheTVDB id from show guid
        thetvdb_id = re.findall(r"\d+", show.guid)[0]
        title = show.title

        cur.execute("""
            INSERT INTO tv_show (thetvdb_id, title)
            VALUES (%s, %s);
        """, (thetvdb_id, title))

    conn.commit()


async def get_all_tv_shows():
    cur.execute("""
        SELECT *
        FROM tv_show;
    """)

    return cur.fetchall()
