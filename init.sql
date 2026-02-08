USE my_project_db;

-- 1. Setup Logging
DROP TABLE IF EXISTS init_run_log;
CREATE TABLE init_run_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  stage VARCHAR(64) NOT NULL,
  ran_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO init_run_log(stage) VALUES ('started');

-- 2. Schema Definition
-- We remove PRIMARY KEY constraints from ratings/tags to allow multiple entries per movie
CREATE TABLE IF NOT EXISTS movies (
    movieId INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genres VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS movie_genres (
    movieId INT NOT NULL,
    genre VARCHAR(100) NOT NULL,
    PRIMARY KEY (movieId, genre)
);

CREATE TABLE IF NOT EXISTS links (
    movieId INT PRIMARY KEY,
    imdbId VARCHAR(20) NOT NULL,
    tmdbId VARCHAR(20) -- Changed to VARCHAR to prevent failure on empty CSV cells
);

CREATE TABLE IF NOT EXISTS tags (
    userId INT NOT NULL,
    movieId INT NOT NULL,
    tag VARCHAR(255) NOT NULL,
    timestamp BIGINT NOT NULL
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS average_ratings (
    movieId INT NOT NULL,
    avg_rating DECIMAL(3,2) NOT NULL,
    count INT NOT NULL
);

CREATE TABLE IF NOT EXISTS genre_stats_summary (
    genre VARCHAR(100) PRIMARY KEY,
    avg_score DECIMAL(5,4),
    std_dev DECIMAL(5,4),
    total_votes INT,
    sentiment_gap DECIMAL(5,4),  -- NEW
    marmite_score DECIMAL(5,2),  -- NEW
    count_1s INT,
    count_2s INT,
    count_3s INT,
    count_4s INT,
    count_5s INT
);

CREATE TABLE IF NOT EXISTS others (
    movieId INT PRIMARY KEY,
    runtimeMinutes INT,
    directors VARCHAR(100),
    topCast VARCHAR(255),
    regions VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS genre_affinity (
    source VARCHAR(50),
    target VARCHAR(50),
    value INT,
    score DECIMAL(5,4)
);

INSERT INTO init_run_log(stage) VALUES ('tables_created');

-- 3. Data Loading
-- Note: Using \r\n for line endings is safer for files created on Windows/Excel
LOAD DATA INFILE '/var/lib/mysql-files/average_ratings.csv' 
IGNORE INTO TABLE average_ratings
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movies.csv' 
IGNORE INTO TABLE movies 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/links.csv' 
IGNORE INTO TABLE links 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/tags.csv' 
IGNORE INTO TABLE tags 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_genres.csv' 
IGNORE INTO TABLE movie_genres 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/genre_stats_summary.csv' 
IGNORE INTO TABLE genre_stats_summary
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/others.csv' 
IGNORE INTO TABLE others
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/genre_affinity.csv' 
INTO TABLE genre_affinity 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- Speed up Title searches
CREATE INDEX idx_movie_title ON movies(title);
-- Speed up the "Top Rated" sorting on the home page
CREATE INDEX idx_avg_rating ON average_ratings(avg_rating);

CREATE INDEX idx_others_movieid ON others(movieId);

INSERT INTO init_run_log(stage) VALUES ('finished');