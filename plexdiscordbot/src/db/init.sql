CREATE TABLE tv_show (
    tv_show_id INTEGER PRIMARY KEY,
    title TEXT
);

CREATE TABLE subscription (
    discord_id INTEGER,
    tv_show_id INTEGER REFERENCES tv_show(tv_show_id),
    PRIMARY KEY (discord_id, tv_show_id)
);