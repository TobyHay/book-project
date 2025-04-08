
CREATE TABLE "user" (
    user_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_email VARCHAR NOT NULL,
    username VARCHAR,
    date_subscribed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE author (
    author_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR NOT NULL,
    author_url VARCHAR NOT NULL
);

CREATE TABLE author_assignment (
    author_assignment_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    author_id INT NOT NULL,
    user_id INT NOT NULL,
    CONSTRAINT fk_author_id FOREIGN KEY (author_id) REFERENCES author (author_id),
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE TABLE author_measurement (
    author_measurement_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    rating_count INT,
    average_rating FLOAT,
    date_recorded DATETIME DEFAULT CURRENT_TIMESTAMP,
    author_id INT NOT NULL,
    shelved_count INT,
    review_count INT,
    CONSTRAINT fk_author_id FOREIGN KEY (author_id) REFERENCES author(author_id)
);


CREATE TABLE book (
    book_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    author_id INT NOT NULL,
    title VARCHAR NOT NULL,
    release_date DATE,
    image_url VARCHAR,
    CONSTRAINT fk_author_id FOREIGN KEY (author_id) REFERENCES author (author_id)
);

CREATE TABLE book_measurement (
    book_measurement_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    rating_count INT,
    average_rating FLOAT,
    date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    book_id INT,
    price FLOAT,
    review_count INT,
    CONSTRAINT fk_book_id FOREIGN KEY (book_id) REFERENCES book (book_id)
);