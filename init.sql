-- Create Tables with NOT NULL to ensure we don't allow empty entries
CREATE TABLE IF NOT EXISTS movies (
    movieId INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genres VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS links (
    movieId INT PRIMARY KEY,
    imdbId VARCHAR(20) NOT NULL,
    tmdbId INT NOT NULL  -- If this is empty in CSV, the row will be skipped
);

CREATE TABLE IF NOT EXISTS ratings (
    userId INT NOT NULL,
    movieId INT NOT NULL,
    rating DECIMAL(3,1) NOT NULL,
    timestamp BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    userId INT NOT NULL,
    movieId INT NOT NULL,
    tag VARCHAR(255) NOT NULL,
    timestamp BIGINT NOT NULL
) CHARACTER SET utf8mb4;

-- TRUNCATE to ensure a clean start
TRUNCATE TABLE movies;
TRUNCATE TABLE links;
TRUNCATE TABLE ratings;
TRUNCATE TABLE tags;

-- The 'IGNORE' keyword here tells MySQL: 
-- "If a row causes an error (like a missing tmdbId), skip it and move to the next row."
LOAD DATA INFILE '/var/lib/mysql-files/movies.csv' 
IGNORE INTO TABLE movies 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/links.csv' 
IGNORE INTO TABLE links 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/ratings.csv' 
IGNORE INTO TABLE ratings 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/tags.csv' 
IGNORE INTO TABLE tags 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;