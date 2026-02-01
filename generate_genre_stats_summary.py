import csv
import math
from collections import defaultdict

input_file_movies = './ml-latest/movies.csv'
input_file_ratings = './ml-latest/ratings.csv'
output_file = './ml-latest/genre_stats_summary.csv'

def run_preprocessor():
    # 1. Map MovieID to Genres
    movie_to_genres = {}
    with open(input_file_movies, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['genres'] != '(no genres listed)':
                movie_to_genres[row['movieId']] = row['genres'].split('|')

    # 2. Accumulate Stats
    # genre -> [sum, count, sum_sq, count_1_star, count_5_star]
    stats = defaultdict(lambda: [0.0, 0, 0.0, 0, 0])
    global_sum = 0.0
    global_count = 0

    print("Processing ratings (calculating extremes and global norms)...")
    with open(input_file_ratings, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = row['movieId']
            if mid in movie_to_genres:
                rating = float(row['rating'])
                
                # Global tracking for sentiment gap
                global_sum += rating
                global_count += 1
                
                for g in movie_to_genres[mid]:
                    s = stats[g]
                    s[0] += rating          # sum
                    s[1] += 1               # count
                    s[2] += rating**2       # sum of squares for stddev
                    
                    # Track extremes for polarization ("Little middle ground")
                    if rating <= 1.0:
                        s[3] += 1
                    elif rating >= 5.0:
                        s[4] += 1
    
    global_avg = global_sum / global_count if global_count > 0 else 3.53
    print(f"Global Average Rating: {round(global_avg, 4)}")

    # 3. Write Summary CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # We add business-focused columns here
        writer.writerow(['genre', 'avg_score', 'std_dev', 'total_votes', 'sentiment_gap', 'marmite_score'])
        
        for genre, (total_sum, count, sum_sq, low, high) in stats.items():
            if count > 1000: # Ensure statistical significance
                avg = total_sum / count
                variance = (sum_sq / count) - (avg ** 2)
                std_dev = math.sqrt(max(0, variance))
                
                # New Metrics
                sentiment_gap = avg - global_avg
                # Marmite Score: % of ratings that are 1 or 5 stars
                marmite_score = ((low + high) / count) * 100 
                
                writer.writerow([
                    genre, 
                    round(avg, 4), 
                    round(std_dev, 4), 
                    count, 
                    round(sentiment_gap, 4), 
                    round(marmite_score, 2)
                ])

    print(f"Success! Created {output_file} with advanced analytics.")

if __name__ == "__main__":
    run_preprocessor()