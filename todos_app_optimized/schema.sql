-- DROP DATABASE IF EXISTS todos;
-- CREATE DATABASE todos;

DROP TABLE IF EXISTS lists CASCADE;
CREATE TABLE lists (
    id serial PRIMARY KEY,
    title text NOT NULL UNIQUE
);

DROP TABLE IF EXISTS todos CASCADE;
CREATE TABLE todos (
    id serial PRIMARY KEY,
    title text NOT NULL,
    is_completed boolean NOT NULL DEFAULT false,
    list_id integer NOT NULL REFERENCES lists (id) ON DELETE CASCADE
);