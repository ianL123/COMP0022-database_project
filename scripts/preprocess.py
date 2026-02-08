import csv
import math
import os
from collections import defaultdict

# --- Configuration ---
DATA_DIR = '../ml-latest'
INPUT_MOVIES = os.path.join(DATA_DIR, 'movies.csv')
INPUT_RATINGS = os.path.join(DATA_DIR, 'ratings.csv')
INPUT_OTHERS = os.path.join(DATA_DIR, 'others.csv')

# Output Files
OUTPUT_AVG_RATINGS = os.path.join(DATA_DIR, 'average_ratings.csv')
OUTPUT_GENRE_STATS = os.path.join(DATA_DIR, 'genre_stats_summary.csv')
OUTPUT_MOVIE_GENRES = os.path.join(DATA_DIR, 'movie_genres.csv')
OUTPUT_DIRECTORS = os.path.join(DATA_DIR, 'movie_directors.csv')
OUTPUT_CAST = os.path.join(DATA_DIR, 'movie_cast.csv')
OUTPUT_REGIONS = os.path.join(DATA_DIR, 'movie_regions.csv')
OUTPUT_GENRE_AFFINITY = os.path.join(DATA_DIR, 'genre_affinity.csv')

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
    """
    Script 2 logic: Advanced analytics for EXACT genre combinations.
    Keeps 'Action|Sci-Fi' as a single category for the dashboard.
    """
    print("3. Generating advanced genre analytics for combinations (Marmite Score, etc.)...")
    
    # Map MovieID to the RAW genre string
    movie_to_genre_combo = {}
    with open(INPUT_MOVIES, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            # We do NOT split or explode here. We keep the raw string.
            if row['genres'] != '(no genres listed)':
                movie_to_genre_combo[row['movieId']] = row['genres']

    # genre_combo -> [sum, count, sum_sq, count_1s, count_2s, count_3s, count_4s, count_5s]
    stats = defaultdict(lambda: [0.0, 0, 0.0, 0, 0, 0, 0, 0])
    global_sum, global_count = 0.0, 0

    with open(INPUT_RATINGS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid, rating = row['movieId'], float(row['rating'])
            
            # Get the full combination string (e.g., "Adventure|Children|Fantasy")
            genre_str = movie_to_genre_combo.get(mid)
            if genre_str:
                global_sum += rating
                global_count += 1
                
                s = stats[genre_str]
                # Aggregate metrics for this specific combo
                s[0] += rating          # sum
                s[1] += 1               # count
                s[2] += rating**2       # sum_sq
                
                # Star level mapping
                r_int = int(round(rating))
                if 1 <= r_int <= 5:
                    s[r_int + 2] += 1
    
    global_avg = global_sum / global_count if global_count > 0 else 3.53

    with open(OUTPUT_GENRE_STATS, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'genres', 'avg_score', 'std_dev', 'total_votes', 
            'sentiment_gap', 'marmite_score', 
            'count_1s', 'count_2s', 'count_3s', 'count_4s', 'count_5s'
        ])
        
        for genres, data in stats.items():
            t_sum, count, sum_sq = data[0], data[1], data[2]
            c1, c2, c3, c4, c5 = data[3], data[4], data[5], data[6], data[7]
            
            # We keep your threshold of 1000 votes for the report
            if count > 1000:
                avg = t_sum / count
                # Population Standard Deviation
                variance = max(0, (sum_sq / count) - (avg ** 2))
                std_dev = math.sqrt(variance)
                
                # Marmite Score: % of extreme opinions (1 and 5 stars)
                marmite = round(((c1 + c5) / count) * 100, 2)
                
                writer.writerow([
                    genres, round(avg, 4), round(std_dev, 4), count, 
                    round(avg - global_avg, 4), marmite,
                    c1, c2, c3, c4, c5
                ])
    print(f"   - Success: Created {OUTPUT_GENRE_STATS}")

def process_others_metadata():
    """Script 4 logic: Explodes others.csv into normalized directors, cast, and regions tables."""
    print(f"4. Exploding metadata from {INPUT_OTHERS}...")

    if not os.path.exists(INPUT_OTHERS):
        print(f"   - Warning: {INPUT_OTHERS} not found. Skipping.")
        return

    with open(INPUT_OTHERS, mode='r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        
        with open(OUTPUT_DIRECTORS, 'w', encoding='utf-8', newline='') as f_dir, \
             open(OUTPUT_CAST, 'w', encoding='utf-8', newline='') as f_cast, \
             open(OUTPUT_REGIONS, 'w', encoding='utf-8', newline='') as f_reg:
            
            w_dir = csv.writer(f_dir)
            w_cast = csv.writer(f_cast)
            w_reg = csv.writer(f_reg)
            
            # Write Headers
            w_dir.writerow(['movieId', 'director'])
            w_cast.writerow(['movieId', 'actor'])
            w_reg.writerow(['movieId', 'region'])

            for row in reader:
                mid = row['movieId']
                
                # Normalize Directors
                if row['directors']:
                    for d in row['directors'].split('|'):
                        if d.strip(): w_dir.writerow([mid, d.strip()])
                
                # Normalize Cast
                if row['topCast']:
                    for c in row['topCast'].split('|'):
                        if c.strip(): w_cast.writerow([mid, c.strip()])
                
                # Normalize Regions
                if row['regions']:
                    for r in row['regions'].split('|'):
                        if r.strip(): w_reg.writerow([mid, r.strip()])
                        
    print(f"   - Success: Created normalized metadata CSVs.")

def process_genre_affinity():
    print(f"4. Calculating Normalized Genre Affinity...")
    
    movie_genres = {}
    with open(INPUT_MOVIES, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['genres'] != '(no genres listed)':
                movie_genres[row['movieId']] = row['genres'].split('|')

    user_to_genres = defaultdict(set)
    genre_totals = defaultdict(int) # Unique users per genre

    with open(INPUT_RATINGS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if float(row['rating']) >= 4.0:
                m_id, u_id = row['movieId'], row['userId']
                if m_id in movie_genres:
                    for g in movie_genres[m_id]:
                        user_to_genres[u_id].add(g)

    # Calculate total unique lovers for each genre (denominator part 1)
    for genres in user_to_genres.values():
        for g in genres:
            genre_totals[g] += 1

    # Count intersections
    affinity_counts = defaultdict(int)
    for genres in user_to_genres.values():
        sorted_genres = sorted(list(genres))
        for i in range(len(sorted_genres)):
            for j in range(i + 1, len(sorted_genres)):
                pair = (sorted_genres[i], sorted_genres[j])
                affinity_counts[pair] += 1

    # Write Results with Normalized Score
    with open(OUTPUT_GENRE_AFFINITY, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target', 'value', 'score'])
        for (g1, g2), count in affinity_counts.items():
            # Jaccard Score = Intersection / Union
            # Union(A,B) = Total(A) + Total(B) - Intersection(A,B)
            union = genre_totals[g1] + genre_totals[g2] - count
            score = count / union if union > 0 else 0
            
            if count > 5:
                writer.writerow([g1, g2, count, round(score, 4)])
    print(f"   - Success: Created {OUTPUT_GENRE_AFFINITY}")

if __name__ == "__main__":
    print("--- Starting Unified Pipeline ---")
    process_movie_genres()
    process_average_ratings()
    process_advanced_genre_stats()
    process_others_metadata()
    process_genre_affinity()
    print("--- All Tasks Complete ---")