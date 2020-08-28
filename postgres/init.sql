CREATE TABLE tv_show (
    tv_show_id serial PRIMARY KEY,
    thetvdb_id integer UNIQUE,
    title text,
    slug text
);

CREATE TABLE subscription (
    subscription_id serial PRIMARY KEY,
    discord_id bigint,
    tv_show_id int references tv_show(tv_show_id)
);