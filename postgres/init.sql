CREATE TABLE tv_show (
    tv_show_id serial PRIMARY KEY,
    thetvdb_id integer UNIQUE,
    title text,
    slug text
);

CREATE TABLE member (
    member_id serial PRIMARY KEY,
    discord_id bigint UNIQUE
);

CREATE TABLE subscription (
    subscription_id serial PRIMARY KEY,
    member_id int references member(member_id),
    tv_show_id int references tv_show(tv_show_id)
);