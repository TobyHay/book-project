DROP TABLE IF EXISTS author_assignment, author_measurement, book_measurement, book, author, publisher;

CREATE TABLE publisher (
    publisher_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    publisher_email VARCHAR NOT NULL,
    publisher_name VARCHAR,
    date_subscribed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE author (
    author_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    author_name VARCHAR NOT NULL,
    author_url VARCHAR NOT NULL,
    author_image_url VARCHAR,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE author_assignment (
    author_assignment_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    author_id INT NOT NULL,
    publisher_id SMALLINT NOT NULL,
    CONSTRAINT fk_author_id FOREIGN KEY (author_id) REFERENCES author (author_id),
    CONSTRAINT fk_publisher_id FOREIGN KEY (publisher_id) REFERENCES publisher (publisher_id)
);

CREATE TABLE author_measurement (
    author_measurement_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    rating_count INT,
    average_rating FLOAT,
    date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author_id INT NOT NULL,
    shelved_count INT,
    review_count INT,
    CONSTRAINT fk_author_id FOREIGN KEY (author_id) REFERENCES author(author_id)
);


CREATE TABLE book (
    book_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    author_id INT NOT NULL,
    book_title VARCHAR NOT NULL,
    year_published SMALLINT,
    big_image_url VARCHAR,
    small_image_url VARCHAR,
    book_url_path VARCHAR NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_author_id FOREIGN KEY (author_id) REFERENCES author (author_id)
);

CREATE TABLE book_measurement (
    book_measurement_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    rating_count INT,
    average_rating FLOAT,
    date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    book_id INT,
    book_price FLOAT,
    review_count INT,
    CONSTRAINT fk_book_id FOREIGN KEY (book_id) REFERENCES book (book_id)
);

INSERT INTO author (author_name, author_url, author_image_url)
VALUES ("Suzanne Collins", "https://www.goodreads.com/author/show/153394.Suzanne_Collins", "https://images.gr-assets.com/authors/1630199330p5/153394.jpg");

INSERT INTO publisher (publisher_email, publisher_name)
VALUES ("trainee.toby.hayman@sigmalabs.co.uk", "Sigma Labs Publishing LTD");
