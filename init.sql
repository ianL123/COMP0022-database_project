USE my_project_db;

-- 1. Setup Logging
DROP TABLE IF EXISTS init_run_log;
CREATE TABLE init_run_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  stage VARCHAR(64) NOT NULL,
  ran_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO init_run_log(stage) VALUES ('started');

-- 2. Create the Parent/Master table first
CREATE TABLE IF NOT EXISTS movie_titles (
    movieId INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4;

-- 3. Create all other tables
CREATE TABLE IF NOT EXISTS average_ratings (
    movieId INT PRIMARY KEY,
    avg_rating DECIMAL(3,2) NOT NULL,
    count INT NOT NULL
);

CREATE TABLE IF NOT EXISTS genre_affinity (
    source VARCHAR(50),
    target VARCHAR(50),
    value INT,
    score DECIMAL(5,4),
    PRIMARY KEY (source, target)
);

CREATE TABLE IF NOT EXISTS genre_stats_summary (
    genre VARCHAR(100) PRIMARY KEY,
    avg_score DECIMAL(5,4),
    std_dev DECIMAL(5,4),
    total_votes INT,
    sentiment_gap DECIMAL(5,4),
    marmite_score DECIMAL(5,2),
    count_1s INT, count_2s INT, count_3s INT, count_4s INT, count_5s INT
);

CREATE TABLE IF NOT EXISTS links (
    movieId INT PRIMARY KEY,
    imdbId VARCHAR(20) NOT NULL,
    tmdbId VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS movie_casts (
    movieId INT NOT NULL,
    actor VARCHAR(100) NOT NULL,
    PRIMARY KEY (movieId, actor)
);

CREATE TABLE IF NOT EXISTS movie_directors (
    movieId INT NOT NULL,
    director VARCHAR(100) NOT NULL,
    PRIMARY KEY (movieId, director)
);

CREATE TABLE IF NOT EXISTS movie_genres (
    movieId INT NOT NULL,
    genre VARCHAR(100) NOT NULL,
    PRIMARY KEY (movieId, genre)
);

CREATE TABLE IF NOT EXISTS movie_regions (
    movieId INT NOT NULL,
    region VARCHAR(50) NOT NULL,
    PRIMARY KEY (movieId, region)
);

CREATE TABLE IF NOT EXISTS movie_runtimes (
    movieId INT PRIMARY KEY,
    runtimeMinutes INT
);

CREATE TABLE IF NOT EXISTS tags (
    userId INT NOT NULL,
    movieId INT NOT NULL,
    tag VARCHAR(255) NOT NULL,
    timestamp BIGINT NOT NULL,
    PRIMARY KEY (userId, movieId, tag)
) CHARACTER SET utf8mb4;

INSERT INTO init_run_log(stage) VALUES ('tables_created');

-- 4. Data Loading
-- Note: Using \r\n for line endings is safer for files created on Windows/Excel
LOAD DATA INFILE '/var/lib/mysql-files/movie_titles.csv' 
INTO TABLE movie_titles 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/average_ratings.csv' 
INTO TABLE average_ratings 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/genre_affinity.csv' 
INTO TABLE genre_affinity 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/genre_stats_summary.csv' 
INTO TABLE genre_stats_summary 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/links.csv' 
INTO TABLE links 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_casts.csv' 
INTO TABLE movie_casts 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_directors.csv' 
INTO TABLE movie_directors 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_genres.csv' 
INTO TABLE movie_genres 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_regions.csv' 
INTO TABLE movie_regions 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_runtimes.csv' 
INTO TABLE movie_runtimes 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/tags.csv' 
INTO TABLE tags 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- Speed up Title searches
CREATE INDEX idx_movie_title ON movie_titles(title);

-- Speed up the "Top Rated" sorting
CREATE INDEX idx_avg_rating ON average_ratings(avg_rating);

-- Specific index for actors and directors
CREATE INDEX idx_director_name ON movie_directors(director);
CREATE INDEX idx_actor_name ON movie_casts(actor);
CREATE INDEX idx_region_code ON movie_regions(region);

-- Create Foreign Keys

-- Linking metadata tables to the main title index
ALTER TABLE average_ratings
ADD CONSTRAINT fk_ratings_movie
FOREIGN KEY (movieId)
REFERENCES movie_titles(movieId);

ALTER TABLE links
ADD CONSTRAINT fk_links_movie
FOREIGN KEY (movieId)
REFERENCES movie_titles(movieId);

ALTER TABLE movie_runtimes
ADD CONSTRAINT fk_runtimes_movie
FOREIGN KEY (movieId)
REFERENCES movie_titles(movieId);

-- Linking relationship (junction) tables
ALTER TABLE movie_casts
ADD CONSTRAINT fk_casts_movie
FOREIGN KEY (movieId)
REFERENCES movie_titles(movieId);

ALTER TABLE movie_directors
ADD CONSTRAINT fk_directors_movie
FOREIGN KEY (movieId)
REFERENCES movie_titles(movieId);

ALTER TABLE movie_genres
ADD CONSTRAINT fk_genres_movie
FOREIGN KEY (movieId)
REFERENCES movie_titles(movieId);

ALTER TABLE movie_regions
ADD CONSTRAINT fk_regions_movie
FOREIGN KEY (movieId)
REFERENCES movie_titles(movieId);

ALTER TABLE tags
ADD CONSTRAINT fk_tags_movie
FOREIGN KEY (movieId)
REFERENCES movie_titles(movieId);

INSERT INTO init_run_log(stage) VALUES ('finished');