import csv
import math
import os
from collections import defaultdict

# --- Configuration ---
DATA_DIR = '../ml-latest'
INPUT_MOVIES = os.path.join(DATA_DIR, 'movies.csv')
INPUT_RATINGS = os.path.join(DATA_DIR, 'ratings.csv')

# Output Files
OUTPUT_AVG_RATINGS = os.path.join(DATA_DIR, 'average_ratings.csv')
OUTPUT_GENRE_STATS = os.path.join(DATA_DIR, 'genre_stats_summary.csv')
OUTPUT_MOVIE_GENRES = os.path.join(DATA_DIR, 'movie_genres.csv')

def process_movie_genres():
    """Script 3 logic: Explodes movies.csv into a long-form movieId-genre mapping."""
    print(f"1. Exploding genres from {INPUT_MOVIES}...")
    
    with open(INPUT_MOVIES, mode='r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        with open(OUTPUT_MOVIE_GENRES, mode='w', encoding='utf-8', newline='') as fout:
            writer = csv.writer(fout)
            writer.writerow(['movieId', 'genre'])
            
            for row in reader:
                if row['genres'] == '(no genres listed)':
                    continue
                for genre in row['genres'].split('|'):
                    writer.writerow([row['movieId'], genre])
    print(f"   - Success: Created {OUTPUT_MOVIE_GENRES}")

def process_average_ratings():
    """Script 1 logic: Aggregates ratings.csv to find mean score per movie."""
    print(f"2. Calculating average ratings from {INPUT_RATINGS}...")
    
    movie_stats = {} # {movieId: [sum_of_ratings, count]}
    with open(INPUT_RATINGS, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            m_id, rating = row['movieId'], float(row['rating'])
            if m_id not in movie_stats:
                movie_stats[m_id] = [0.0, 0]
            movie_stats[m_id][0] += rating
            movie_stats[m_id][1] += 1

    with open(OUTPUT_AVG_RATINGS, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['movieId', 'avg_rating', 'count'])
        for m_id in sorted(movie_stats.keys(), key=int):
            total, count = movie_stats[m_id]
            writer.writerow([m_id, total / count, count])
    print(f"   - Success: Created {OUTPUT_AVG_RATINGS}")

def process_advanced_genre_stats():
    """Script 2 logic: Advanced analytics combining movies and ratings."""
    print("3. Generating advanced genre analytics (Marmite Score, etc.)...")
    
    # Map MovieID to Genres
    movie_to_genres = {}
    with open(INPUT_MOVIES, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['genres'] != '(no genres listed)':
                movie_to_genres[row['movieId']] = row['genres'].split('|')

    # genre -> [sum, count, sum_sq, count_1s, count_2s, count_3s, count_4s, count_5s]
    # We use 8 indices now to track the total sum, total count, sum of squares, and each star level.
    stats = defaultdict(lambda: [0.0, 0, 0.0, 0, 0, 0, 0, 0])
    global_sum, global_count = 0.0, 0

    with open(INPUT_RATINGS, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            mid, rating = row['movieId'], float(row['rating'])
            if mid in movie_to_genres:
                global_sum += rating
                global_count += 1
                for g in movie_to_genres[mid]:
                    s = stats[g]
                    s[0], s[1], s[2] = s[0]+rating, s[1]+1, s[2]+(rating**2)
                    
                    # Track individual star counts (rounding in case of 0.5 ratings)
                    r_int = int(round(rating))
                    if 1 <= r_int <= 5:
                        s[r_int + 2] += 1 # Indices 3, 4, 5, 6, 7 represent 1*, 2*, 3*, 4*, 5*
    
    global_avg = global_sum / global_count if global_count > 0 else 3.53

    with open(OUTPUT_GENRE_STATS, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Updated header with specific star count columns
        writer.writerow([
            'genre', 'avg_score', 'std_dev', 'total_votes', 
            'sentiment_gap', 'marmite_score', 
            'count_1s', 'count_2s', 'count_3s', 'count_4s', 'count_5s'
        ])
        
        for genre, data in stats.items():
            t_sum, count, sum_sq = data[0], data[1], data[2]
            c1, c2, c3, c4, c5 = data[3], data[4], data[5], data[6], data[7]
            
            if count > 1000:
                avg = t_sum / count
                std_dev = math.sqrt(max(0, (sum_sq / count) - (avg ** 2)))
                # Marmite Score remains (1* + 5*) / total
                marmite = round(((c1 + c5) / count) * 100, 2)
                
                writer.writerow([
                    genre, round(avg, 4), round(std_dev, 4), count, 
                    round(avg - global_avg, 4), marmite,
                    c1, c2, c3, c4, c5
                ])
    print(f"   - Success: Created {OUTPUT_GENRE_STATS}")

if __name__ == "__main__":
    print("--- Starting Unified Pipeline ---")
    process_movie_genres()
    process_average_ratings()
    process_advanced_genre_stats()
    print("--- All Tasks Complete ---")