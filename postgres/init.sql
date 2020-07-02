CREATE TABLE tv_show (
    tv_show_id serial PRIMARY KEY,
    thetvdb_id integer UNIQUE,
    title text
)