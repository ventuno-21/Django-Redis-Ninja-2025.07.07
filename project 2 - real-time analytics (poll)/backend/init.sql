-- Create all tables
CREATE TABLE app_polls_poll (
    id SERIAL PRIMARY KEY,
    question VARCHAR(255) NOT NULL UNIQUE,
    text JSONB NOT NULL ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    expire_at TIMESTAMPTZ
);


-- Load data into tables
COPY app_polls_poll (id, question, text,is_active,expire_at)
FROM '/data/polls.csv'
DELIMITER ','
DELIMITER ','
CSV HEADER;


-- Reset the id sequence correctly
SELECT setval("app_polls_poll_id_seq", (SELECT MAX(id) FROM app_polls_poll))