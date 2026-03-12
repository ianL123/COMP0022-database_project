SET FOREIGN_KEY_CHECKS = 0;

USE my_project_db;

-- ==========================================
-- 1. Setup Logging & Clean Slate
-- ==========================================
DROP TABLE IF EXISTS init_run_log;
CREATE TABLE init_run_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stage VARCHAR(64) NOT NULL,
    ran_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO init_run_log(stage) VALUES ('started');

-- ==========================================
-- 2. Schema Definition
-- ==========================================

CREATE TABLE IF NOT EXISTS movies (
    movieId INT,
    title VARCHAR(255) NOT NULL,
    runtimeMinutes INT,
    PRIMARY KEY (movieId)
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS movie_genres (
    movieId INT,
    genre VARCHAR(100) NOT NULL,
    PRIMARY KEY (movieId, genre)
);

CREATE TABLE IF NOT EXISTS movie_posters (
    movieId INT PRIMARY KEY,
    poster_url VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS movie_descriptions (
    movieId INT PRIMARY KEY,
    description TEXT NOT NULL
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS tags (
    userId INT NOT NULL,
    movieId INT NOT NULL,
    tag VARCHAR(255) NOT NULL,
    timestamp BIGINT NOT NULL,
    PRIMARY KEY (userId, movieId, tag)
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS average_ratings (
    movieId INT PRIMARY KEY,
    avg_rating DECIMAL(3,2) NOT NULL,
    count INT NOT NULL
);

CREATE TABLE IF NOT EXISTS genre_stats_summary (
    genre_combination VARCHAR(100) PRIMARY KEY,
    num_movies INT,
    avg_score DECIMAL(5,4),
    std_dev DECIMAL(5,4),
    total_votes INT,
    sentiment_gap DECIMAL(5,4),
    marmite_score DECIMAL(5,2),
    count_1s INT, count_2s INT, count_3s INT, count_4s INT, count_5s INT
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
    region VARCHAR(50) NOT NULL,
    PRIMARY KEY (movieId, region)
);

CREATE TABLE IF NOT EXISTS genre_affinity (
    source VARCHAR(100),
    target VARCHAR(100),
    value INT,
    score DECIMAL(5,4),
    PRIMARY KEY (source, target)
);

CREATE TABLE IF NOT EXISTS personality_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    userId VARCHAR(64) NOT NULL UNIQUE,
    openness DECIMAL(5,2),
    agreeableness DECIMAL(5,2),
    emotional_stability DECIMAL(5,2),
    conscientiousness DECIMAL(5,2),
    extraversion DECIMAL(5,2),
    assigned_metric VARCHAR(50),
    assigned_condition VARCHAR(50),
    is_personalized INT,
    enjoy_watching INT
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS personality_ratings (
    userId VARCHAR(64) NOT NULL,
    movieId INT NOT NULL,
    rating DECIMAL(3,1) NOT NULL,
    tstamp DATETIME,
    PRIMARY KEY (userId, movieId) 
) CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_folders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    folder_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_folder_per_user (user_id, folder_name)
);

CREATE TABLE IF NOT EXISTS folder_contents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    folder_id INT NOT NULL,
    movie_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (folder_id) REFERENCES user_folders(id) ON DELETE CASCADE,
    UNIQUE KEY unique_movie_in_folder (folder_id, movie_id)
);

-- Track which users have access to which folders
CREATE TABLE IF NOT EXISTS folder_shares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    folder_id INT NOT NULL,
    shared_with_user_id INT NOT NULL,
    UNIQUE KEY unique_share (folder_id, shared_with_user_id),
    FOREIGN KEY (folder_id) REFERENCES user_folders(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Store comments on folders
CREATE TABLE IF NOT EXISTS folder_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    folder_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (folder_id) REFERENCES user_folders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS heatmap_cache (
    cache_key VARCHAR(64) PRIMARY KEY,
    payload JSON NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO init_run_log(stage) VALUES ('tables_created');

-- ==========================================
-- 3. High-Speed Data Loading
-- ==========================================

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/average_ratings.csv' 
IGNORE INTO TABLE average_ratings FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
INSERT INTO init_run_log(stage) VALUES ('average_ratings_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movies.csv' 
IGNORE INTO TABLE movies FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS
(movieId, title, @runtimeMinutes)
SET runtimeMinutes = NULLIF(TRIM(@runtimeMinutes), '');
INSERT INTO init_run_log(stage) VALUES ('movies_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movie_posters.csv'
IGNORE INTO TABLE movie_posters
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movieId, poster_url);
INSERT INTO init_run_log(stage) VALUES ('movie_posters_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movie_descriptions.csv'
IGNORE INTO TABLE movie_descriptions
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movieId, description);
INSERT INTO init_run_log(stage) VALUES ('movie_descriptions_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/tags.csv' 
IGNORE INTO TABLE tags FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
INSERT INTO init_run_log(stage) VALUES ('tags_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movie_genres.csv' 
IGNORE INTO TABLE movie_genres FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
INSERT INTO init_run_log(stage) VALUES ('movie_genres_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/genre_stats_summary.csv' 
IGNORE INTO TABLE genre_stats_summary FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
INSERT INTO init_run_log(stage) VALUES ('genre_stats_summary_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movie_directors.csv' 
IGNORE INTO TABLE movie_directors FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
INSERT INTO init_run_log(stage) VALUES ('movie_directors_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movie_cast.csv' 
IGNORE INTO TABLE movie_cast FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
INSERT INTO init_run_log(stage) VALUES ('movie_cast_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/movie_regions.csv' 
IGNORE INTO TABLE movie_regions FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
INSERT INTO init_run_log(stage) VALUES ('movie_regions_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/ml-latest/genre_affinity.csv' 
IGNORE INTO TABLE genre_affinity FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
INSERT INTO init_run_log(stage) VALUES ('genre_affinity_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/personality-isf2018/personality-data.csv'
IGNORE INTO TABLE personality_data FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS
(@u, @o, @a, @es, @c, @ex, @am, @ac, @junk1,@junk2,@junk3,@junk4,@junk5,@junk6,@junk7,@junk8,@junk9,@junk10,@junk11,@junk12,@junk13,@junk14,@junk15,@junk16,@junk17,@junk18,@junk19,@junk20,@junk21,@junk22,@junk23,@junk24, @ip, @ew)
SET userId = TRIM(@u), openness = NULLIF(TRIM(@o),''), agreeableness = NULLIF(TRIM(@a),''), emotional_stability = NULLIF(TRIM(@es),''), conscientiousness = NULLIF(TRIM(@c),''), extraversion = NULLIF(TRIM(@ex),''), assigned_metric = NULLIF(TRIM(@am),''), assigned_condition = NULLIF(TRIM(@ac),''), is_personalized = NULLIF(TRIM(@ip),''), enjoy_watching = NULLIF(TRIM(@ew),'');
INSERT INTO init_run_log(stage) VALUES ('personality_data_loaded');

LOAD DATA INFILE '/var/lib/mysql-files/personality-isf2018/ratings.csv'
IGNORE INTO TABLE personality_ratings FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS
(@u, @m, @r, @t)
SET userId = TRIM(@u), movieId = @m, rating = @r, tstamp = FROM_UNIXTIME(@t);
INSERT INTO init_run_log(stage) VALUES ('personality_ratings_loaded');

INSERT INTO init_run_log(stage) VALUES ('ALL DATA LOADED');

-- ==========================================
-- 4. Indexing & Relationships
-- ==========================================

CREATE INDEX idx_movie_title ON movies(title);
CREATE INDEX idx_avg_rating ON average_ratings(avg_rating);
CREATE INDEX idx_director_name ON movie_directors(director);
CREATE INDEX idx_actor_name ON movie_cast(actor);
CREATE INDEX idx_pd_user ON personality_data(userId);
CREATE INDEX idx_pr_user_movie ON personality_ratings(userId, movieId);

-- ==========================================
-- 5. Foreign Keys Definitions
-- ==========================================

ALTER TABLE movie_genres 
    ADD CONSTRAINT fk_mg_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE average_ratings 
    ADD CONSTRAINT fk_ar_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE movie_directors 
    ADD CONSTRAINT fk_md_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE movie_cast 
    ADD CONSTRAINT fk_mc_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE movie_regions 
    ADD CONSTRAINT fk_mreg_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE tags 
    ADD CONSTRAINT fk_tags_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE movie_posters
    ADD CONSTRAINT fk_mp_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE movie_descriptions
    ADD CONSTRAINT fk_mdesc_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE personality_ratings 
    ADD CONSTRAINT fk_pr_movie FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE;

ALTER TABLE personality_ratings 
    ADD CONSTRAINT fk_pr_user FOREIGN KEY (userId) REFERENCES personality_data(userId) ON DELETE CASCADE;

INSERT INTO init_run_log(stage) VALUES ('finished');

SET FOREIGN_KEY_CHECKS = 1;