import plex
import sqlite3
import logging
from os import path

conn: sqlite3.Connection
cur: sqlite3.Cursor


def init():
    db = 'db/db.db'
    exists = path.exists(db)

    global conn
    # Enable autocommit
    conn = sqlite3.connect(db, isolation_level=None)

    global cur
    cur = conn.cursor()

    if not exists:
        cur.executescript(open('db/init.sql').read())
        update_db()


def update_db():
    logging.info("Updating DB...")

    # Insert tv shows
    tv_shows = plex.get_all_tv_shows()

    for show in tv_shows:
        key = show.ratingKey
        title = show.title

        cur.execute("INSERT INTO tv_show VALUES (?, ?)", (key, title))


def get_all_tv_shows():
    cur.execute("SELECT * FROM tv_show")

    return cur.fetchall()


def get_tv_show(tv_show_id):
    cur.execute("SELECT * FROM tv_show WHERE tv_show_id = ?", (tv_show_id,))

    return cur.fetchone()


def search_tv_show(search):
    cur.execute("SELECT * FROM tv_show WHERE title LIKE ?", (f"%{search}%",))

    return cur.fetchall()


def add_tv_show(tv_show_id, title):
    cur.execute("INSERT INTO tv_show VALUES (?, ?)", (tv_show_id, title))


def delete_tv_show(tv_show_id):
    cur.execute("DELETE FROM tv_show WHERE tv_show_id = ?", (tv_show_id,))


def subscribe(discord_id, tv_show_id):
    cur.execute("INSERT INTO subscription VALUES (?, ?)", (discord_id, tv_show_id))


def is_subscribed(discord_id, tv_show_id):
    cur.execute("SELECT * FROM subscription WHERE discord_id = ? AND tv_show_id = ? LIMIT 1", (discord_id, tv_show_id))

    return cur.rowcount == 1


def unsubscribe(discord_id, tv_show_id):
    cur.execute("DELETE FROM subscription WHERE discord_id = ? AND tv_show_id = ?", (discord_id, tv_show_id))


def get_subscriptions(discord_id):
    cur.execute("SELECT * FROM tv_show t INNER JOIN subscription s ON t.tv_show_id = s.tv_show_id "
                "WHERE s.discord_id = ?", (discord_id,))

    return cur.fetchall()


def get_subscriptions_via_key(tv_show_id):
    cur.execute("SELECT * FROM subscription WHERE tv_show_id = ?", (tv_show_id,))

    return cur.fetchall()


def delete_subscriptions(discord_id):
    cur.execute("DELETE FROM subscription WHERE discord_id = ?", (discord_id,))
