CREATE TABLE tv_show (
    tv_show_id serial PRIMARY KEY,
    thetvdb_id integer UNIQUE,
    title text
);

CREATE TABLE member (
    member_id serial PRIMARY KEY,
    discord_id bigint UNIQUE
);