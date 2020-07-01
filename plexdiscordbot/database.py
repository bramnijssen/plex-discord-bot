import os
import sqlite3
import plex
import re
import logging

cur: sqlite3.Cursor


async def init():
    await plex.init()

    db = "db.db"
    exists = os.path.isfile(db)
    conn = sqlite3.connect(db)

    global cur
    cur = conn.cursor()

    if not exists:
        cur.execute("""
            CREATE TABLE tv_show (
                tv_show_id INTEGER PRIMARY KEY AUTOINCREMENT,
                thetvdb_id INTEGER,
                title TEXT
            )
        """)

        tv_shows = await plex.get_all_tv_shows()

        for show in tv_shows:
            id = re.findall(r"\d+", show.guid)[0]
            title = show.title

            cur.execute("""
                INSERT INTO tv_show (thetvdb_id, title)
                VALUES (?, ?)
            """, (id, title))

        conn.commit()
