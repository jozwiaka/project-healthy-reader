-- CREATE TABLE user_recommendations (
--     user_id INTEGER,
--     isbn VARCHAR(20),
--     score FLOAT,
--     PRIMARY KEY (user_id, isbn)
-- );

-- CREATE TABLE book_similarities (
--     isbn_source VARCHAR(20),
--     isbn_similar VARCHAR(20),
--     score FLOAT,
--     PRIMARY KEY (isbn_source, isbn_similar)
-- );

CREATE TABLE user_recommendations (
    user_id INT,
    recommended_isbns TEXT[]
);

CREATE TABLE book_similarities (
    isbn TEXT,
    similar_isbns TEXT[]
);

