--DROP TABLE IF EXISTS user;
--DROP TABLE IF EXISTS post;
--
--CREATE TABLE user (
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    username TEXT UNIQUE NOT NULL,
--    password TEXT NOT NULL
--);
--
--CREATE TABLE post (
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    author_id INTEGER NOT NULL,
--    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--    title TEXT NOT NULL,
--    body TEXT NOT NULL,
--    FOREIGN KEY (author_id) REFERENCES user (id)
--);
--

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS tokens;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    location_id TEXT,
    location_brand TEXT,
    location_address TEXT,
    access_token TEXT DEFAULT 'default',
    access_timestamp FLOAT DEFAULT 0,
    refresh_token TEXT DEFAULT 'default',
    refresh_timestamp FLOAT DEFAULT 0
);


CREATE TABLE tokens (
    token_type TEXT UNIQUE NOT NULL,
    token TEXT UNIQUE NOT NULL,
    timestamp  INTEGER NOT NULL
);

INSERT INTO tokens VALUES ('client', 'client-token', 0);
INSERT INTO tokens VALUES ('customer', 'customer-token', 0);
