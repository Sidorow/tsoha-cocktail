CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, is_admin BOOLEAN);

CREATE TABLE recipe_ingredient (id SERIAL PRIMARY KEY, ingredient_id INTEGER REFERENCES ingredient(id), recipe_id INTEGER REFERENCES recipes(id), amount INTEGER);

CREATE TABLE ingredients (id SERIAL PRIMARY KEY, name TEXT UNIQUE, is_alc BOOLEAN);

CREATE TABLE recipes (id SERIAL PRIMARY KEY, name TEXT UNIQUE, description TEXT);

CREATE TABLE reviews (id SERIAL PRIMARY KEY, content TEXT, user_id INTEGER REFERENCES users(id), recipe_id INTEGER REFERENCES recipes(id), rating INTEGER, sent_at TIMESTAMP);

