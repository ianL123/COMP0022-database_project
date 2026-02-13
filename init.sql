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
CREATE TABLE IF NOT EXISTS movie_titles (
    movieId INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    PRIMARY KEY (movieId, title)
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

CREATE TABLE IF NOT EXISTS movie_directors (
    movieId INT NOT NULL,
    director VARCHAR(100) NOT NULL,
    PRIMARY KEY (movieId, director)
);

CREATE TABLE IF NOT EXISTS movie_cast (
    movieId INT NOT NULL,
    actor VARCHAR(100) NOT NULL,
    PRIMARY KEY (movieId, actor)
);

CREATE TABLE IF NOT EXISTS movie_regions (
    movieId INT NOT NULL,
    region VARCHAR(50) NOT NULL, -- Region codes usually short
    PRIMARY KEY (movieId, region)
);

CREATE TABLE IF NOT EXISTS movie_runtimes (
    movieId INT NOT NULL,
    runtimeMinutes INT,
    PRIMARY KEY (movieId, runtimeMinutes)
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
LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/average_ratings.csv' 
IGNORE INTO TABLE average_ratings
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_titles.csv' 
IGNORE INTO TABLE movie_titles
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS
(movieId, title);

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/links.csv' 
IGNORE INTO TABLE links 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/tags.csv' 
IGNORE INTO TABLE tags 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movie_genres.csv' 
IGNORE INTO TABLE movie_genres 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/genre_stats_summary.csv' 
IGNORE INTO TABLE genre_stats_summary
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_directors.csv' 
IGNORE INTO TABLE movie_directors
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_casts.csv' 
IGNORE INTO TABLE movie_cast
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movie_regions.csv' 
IGNORE INTO TABLE movie_regions
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/movie_runtimes.csv' 
IGNORE INTO TABLE movie_runtimes
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/genre_affinity.csv' 
INTO TABLE genre_affinity 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- Speed up Title searches
CREATE INDEX idx_movie_title ON movie_titles(title);
-- Speed up the "Top Rated" sorting on the home page
CREATE INDEX idx_avg_rating ON average_ratings(avg_rating);

CREATE INDEX idx_others_movieid ON others(movieId);

CREATE INDEX idx_director_name ON movie_directors(director);
CREATE INDEX idx_actor_name ON movie_cast(actor);
CREATE INDEX idx_region_code ON movie_regions(region);
CREATE INDEX idx_runtimes ON movie_runtimes(runtimeMinutes);

-- =========================
-- Personality dataset tables
-- =========================

DROP TABLE IF EXISTS personality_data;
CREATE TABLE personality_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    userId VARCHAR(64) NOT NULL,
    openness DECIMAL(5,2),
    agreeableness DECIMAL(5,2),
    emotional_stability DECIMAL(5,2),
    conscientiousness DECIMAL(5,2),
    extraversion DECIMAL(5,2),
    assigned_metric VARCHAR(50),
    assigned_condition VARCHAR(50),
    is_personalized INT,
    enjoy_watching INT,
    INDEX idx_pd_user (userId)
) CHARACTER SET utf8mb4;


DROP TABLE IF EXISTS personality_ratings;
CREATE TABLE personality_ratings (
    userId VARCHAR(64) NOT NULL,
    movieId INT NOT NULL,
    rating DECIMAL(3,1) NOT NULL,
    tstamp DATETIME,
    INDEX idx_pr_movie (movieId),
    INDEX idx_pr_user (userId)
) CHARACTER SET utf8mb4;

INSERT INTO init_run_log(stage) VALUES ('tables_created_personality');

-- Load personality-data.csv (ignore trailing columns)
LOAD DATA INFILE '/var/lib/mysql-files/personality-isf2018/personality-data.csv'
INTO TABLE personality_data
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    @userId,
    @openness,
    @agreeableness,
    @emotional_stability,
    @conscientiousness,
    @extraversion,
    @assigned_metric,
    @assigned_condition,
    -- ignore the rest columns until last two (we will just swallow all remaining)
    @c1,@c2,@c3,@c4,@c5,@c6,@c7,@c8,@c9,@c10,@c11,@c12,@c13,@c14,@c15,@c16,@c17,@c18,@c19,@c20,@c21,@c22,@c23,@c24,
    @is_personalized,
    @enjoy_watching
)
SET
    userId = TRIM(@userId),
    openness = NULLIF(TRIM(@openness),''),
    agreeableness = NULLIF(TRIM(@agreeableness),''),
    emotional_stability = NULLIF(TRIM(@emotional_stability),''),
    conscientiousness = NULLIF(TRIM(@conscientiousness),''),
    extraversion = NULLIF(TRIM(@extraversion),''),
    assigned_metric = NULLIF(TRIM(@assigned_metric),''),
    assigned_condition = NULLIF(TRIM(@assigned_condition),''),
    is_personalized = NULLIF(TRIM(@is_personalized),''),
    enjoy_watching = NULLIF(TRIM(@enjoy_watching),'');

LOAD DATA INFILE '/var/lib/mysql-files/personality-isf2018/ratings.csv'
INTO TABLE personality_ratings
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS

(@userId, @movieId, @rating, @tstamp)
SET
    userId = TRIM(@userId),
    movieId = NULLIF(TRIM(@movieId),''),
    rating = NULLIF(TRIM(@rating),''),
    tstamp = NULLIF(TRIM(@tstamp),'');

CREATE INDEX idx_mg_genre ON movie_genres(genre);
CREATE INDEX idx_mg_movie ON movie_genres(movieId);

CREATE TABLE IF NOT EXISTS heatmap_cache (
    cache_key VARCHAR(64) PRIMARY KEY,
    payload JSON NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_pr_user ON personality_ratings(userId);
CREATE INDEX idx_pr_movie ON personality_ratings(movieId);
CREATE INDEX idx_mg_movie ON movie_genres(movieId);
CREATE INDEX idx_pd_user ON personality_data(userId);

INSERT INTO init_run_log(stage) VALUES ('Task 5 finished');

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

LOAD DATA INFILE '/var/lib/mysql-files/user-system/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- 1. Create the master table for lists
CREATE TABLE IF NOT EXISTS user_folders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    folder_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 2. Update the watchlist to reference a specific folder
CREATE TABLE IF NOT EXISTS folder_contents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    folder_id INT NOT NULL,
    movie_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (folder_id) REFERENCES user_folders(id) ON DELETE CASCADE,
    UNIQUE KEY unique_movie_in_folder (folder_id, movie_id)
);

ALTER TABLE folder_contents
ADD CONSTRAINT fk_folder_id
FOREIGN KEY (folder_id) REFERENCES user_folders(id)
ON DELETE CASCADE;

INSERT INTO init_run_log(stage) VALUES ('finished');
