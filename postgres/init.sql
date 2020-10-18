CREATE TABLE tv_show (
    tv_show_id serial PRIMARY KEY,
    plex_key int UNIQUE,
    title text
);

CREATE TABLE subscription (
    subscription_id serial PRIMARY KEY,
    discord_id bigint,
    tv_show_id int references tv_show(tv_show_id)
);