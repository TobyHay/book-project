INSERT INTO author (author_name, author_url, author_image_url, date_added) VALUES
('J.R.R. Tolkien', 'https://www.goodreads.com/author/show/656983', 'https://images.gr-assets.com/authors/1648968349p5/656983.jpg', '2025-04-16 16:42:01.818719'),
('J.K. Rowling', 'https://www.goodreads.com/author/show/1077326', 'https://images.gr-assets.com/authors/1596216614p5/1077326.jpg', '2025-04-16 16:42:29.346177');

INSERT INTO book (author_id, book_title, year_published, big_image_url, small_image_url, book_url_path, date_added) VALUES
(1, 'The Hunger Games', 2008, 'https://images.gr-assets.com/books/1447303603l/2767052.jpg', 'https://images.gr-assets.com/books/1447303603s/2767052.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(1, 'Catching Fire', 2009, 'https://images.gr-assets.com/books/1447303603l/6148028.jpg', 'https://images.gr-assets.com/books/1447303603s/6148028.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(1, 'Mockingjay', 2010, 'https://images.gr-assets.com/books/1447303603l/7260188.jpg', 'https://images.gr-assets.com/books/1447303603s/7260188.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(2, 'The Hobbit', 1937, 'https://images.gr-assets.com/books/1372847500l/5907.jpg', 'https://images.gr-assets.com/books/1372847500s/5907.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(2, 'The Fellowship of the Ring', 1954, 'https://images.gr-assets.com/books/1298411339l/34.jpg', 'https://images.gr-assets.com/books/1298411339s/34.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(2, 'The Two Towers', 1954, 'https://images.gr-assets.com/books/1546071216l/15241.jpg', 'https://images.gr-assets.com/books/1546071216s/15241.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(2, 'The Return of the King', 1955, 'https://images.gr-assets.com/books/1546071337l/18512.jpg', 'https://images.gr-assets.com/books/1546071337s/18512.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(3, 'Harry Potter and the Philosophers Stone', 1997, 'https://images.gr-assets.com/books/1474154022l/3.jpg', 'https://images.gr-assets.com/books/1474154022s/3.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(3, 'Harry Potter and the Chamber of Secrets', 1998, 'https://images.gr-assets.com/books/1474169725l/15881.jpg', 'https://images.gr-assets.com/books/1474169725s/15881.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00'),
(3, 'Harry Potter and the Prisoner of Azkaban', 1999, 'https://images.gr-assets.com/books/1630547330l/5.jpg', 'https://images.gr-assets.com/books/1630547330s/5.jpg', 'https://www.goodreads.com/author/show/153394', '2025-04-08 10:00:00');



INSERT INTO author_measurement (rating_count, average_rating, date_recorded, author_id, shelved_count, review_count) VALUES
-- Day 1
(1450000, 4.37, '2025-04-09 10:00:00.000', 1, 480000, 128000),
(2150000, 4.48, '2025-04-09 10:00:00.000', 2, 760000, 195000),
(2850000, 4.55, '2025-04-09 10:00:00.000', 3, 940000, 320000),
-- Day 2
(1450500, 4.37, '2025-04-10 10:00:00.000', 1, 480300, 128050),
(2150700, 4.48, '2025-04-10 10:00:00.000', 2, 760400, 195100),
(2851200, 4.55, '2025-04-10 10:00:00.000', 3, 940500, 320200),
-- Day 3
(1451100, 4.37, '2025-04-11 10:00:00.000', 1, 480600, 128100),
(2151400, 4.48, '2025-04-11 10:00:00.000', 2, 760800, 195200),
(2852400, 4.55, '2025-04-11 10:00:00.000', 3, 941000, 320400),
-- Day 4
(1451600, 4.37, '2025-04-12 10:00:00.000', 1, 480900, 128150),
(2152100, 4.48, '2025-04-12 10:00:00.000', 2, 761200, 195300),
(2853600, 4.55, '2025-04-12 10:00:00.000', 3, 941500, 320600),
-- Day 5
(1452100, 4.37, '2025-04-13 10:00:00.000', 1, 481200, 128200),
(2152800, 4.48, '2025-04-13 10:00:00.000', 2, 761600, 195400),
(2854800, 4.55, '2025-04-13 10:00:00.000', 3, 942000, 320800),
-- Day 6
(1452600, 4.37, '2025-04-14 10:00:00.000', 1, 481500, 128250),
(2153500, 4.48, '2025-04-14 10:00:00.000', 2, 762000, 195500),
(2856000, 4.55, '2025-04-14 10:00:00.000', 3, 942500, 321000),
-- Day 7
(1453100, 4.37, '2025-04-15 10:00:00.000', 1, 481800, 128300),
(2154200, 4.48, '2025-04-15 10:00:00.000', 2, 762400, 195600),
(2857200, 4.55, '2025-04-15 10:00:00.000', 3, 943000, 321200);



INSERT INTO book_measurement (rating_count, average_rating, date_recorded, book_id, book_price, review_count) VALUES
-- Day 1
(1200000, 4.34, '2025-04-09 10:00:00.000', 1, 14.99, 110000),
(950000, 4.32, '2025-04-09 10:00:00.000', 2, 15.99, 92000),
(870000, 4.20, '2025-04-09 10:00:00.000', 3, 16.99, 85000),
(1500000, 4.27, '2025-04-09 10:00:00.000', 4, 10.99, 200000),
(1400000, 4.37, '2025-04-09 10:00:00.000', 5, 12.99, 185000),
(1350000, 4.41, '2025-04-09 10:00:00.000', 6, 12.99, 172000),
(1320000, 4.44, '2025-04-09 10:00:00.000', 7, 13.99, 169000),
(2300000, 4.47, '2025-04-09 10:00:00.000', 8, 9.99, 410000),
(2100000, 4.42, '2025-04-09 10:00:00.000', 9, 10.99, 385000),
(2050000, 4.55, '2025-04-09 10:00:00.000', 10, 11.99, 400000),
-- Day 2
(1200500, 4.34, '2025-04-10 10:00:00.000', 1, 14.99, 110050),
(950400, 4.32, '2025-04-10 10:00:00.000', 2, 15.99, 92040),
(870300, 4.20, '2025-04-10 10:00:00.000', 3, 16.99, 85030),
(1500500, 4.27, '2025-04-10 10:00:00.000', 4, 10.99, 200100),
(1400500, 4.37, '2025-04-10 10:00:00.000', 5, 12.99, 185100),
(1350600, 4.41, '2025-04-10 10:00:00.000', 6, 12.99, 172060),
(1320700, 4.44, '2025-04-10 10:00:00.000', 7, 13.99, 169070),
(2301000, 4.47, '2025-04-10 10:00:00.000', 8, 9.99, 410200),
(2100500, 4.42, '2025-04-10 10:00:00.000', 9, 10.99, 385100),
(2050800, 4.55, '2025-04-10 10:00:00.000', 10, 11.99, 400200);
