CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT);

CREATE TABLE ingredients (id SERIAL PRIMARY KEY, name TEXT);

CREATE TABLE recipes (id SERIAL PRIMARY KEY, name TEXT UNIQUE, ingredients TEXT);

CREATE TABLE reviews (id SERIAL PRIMARY KEY, content TEXT, user_id INTEGER REFERENCES users, sent_at TIMESTAMP);

