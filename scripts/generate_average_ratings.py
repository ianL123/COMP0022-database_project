import csv

input_file = '../ml-latest/ratings.csv'
output_file = '../ml-latest/average_ratings.csv'

# Dictionary to store {movieId: [sum_of_ratings, count]}
movie_stats = {}

# Read and aggregate the data
with open(input_file, mode='r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        movie_id = row['movieId']
        rating = float(row['rating'])
        
        if movie_id not in movie_stats:
            movie_stats[movie_id] = [0.0, 0]
        
        movie_stats[movie_id][0] += rating
        movie_stats[movie_id][1] += 1

# Calculate averages and write to the output file
with open(output_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['movieId', 'avg_rating', 'count'])
    
    # Sort movieIds numerically for the output
    sorted_ids = sorted(movie_stats.keys(), key=int)
    
    for m_id in sorted_ids:
        total_rating, count = movie_stats[m_id]
        avg_rating = total_rating / count
        writer.writerow([m_id, avg_rating, count])

print(f"Successfully created {output_file}")