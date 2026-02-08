import csv
from collections import defaultdict

def fast_preprocess(movies_file, ratings_file, output_file):
    # 1. First Pass: Map Movie IDs to Genres (O(M))
    # We need this to know what genre a rating belongs to
    movie_genres = {}
    print("Mapping movie genres...")
    with open(movies_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # We split the piped string into a list
            movie_genres[row['movieId']] = row['genres'].split('|')

    # 2. Second Pass: Group Genres by User (O(R))
    # We only care about high ratings (>= 4.0)
    user_to_genres = defaultdict(set)
    print("Grouping user interests...")
    with open(ratings_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if float(row['rating']) >= 4.0:
                m_id = row['movieId']
                u_id = row['userId']
                if m_id in movie_genres:
                    # Add all genres of this movie to the user's "Liked Set"
                    for g in movie_genres[m_id]:
                        user_to_genres[u_id].add(g)

    # 3. Third Pass: Count Co-occurrences (O(U * G^2))
    # Since G (number of genres) is small (~20), G^2 is tiny.
    affinity_counts = defaultdict(int)
    print("Calculating correlations...")
    for genres in user_to_genres.values():
        sorted_genres = sorted(list(genres))
        # Compare every pair of genres this specific user likes
        for i in range(len(sorted_genres)):
            for j in range(i + 1, len(sorted_genres)):
                pair = (sorted_genres[i], sorted_genres[j])
                affinity_counts[pair] += 1

    # 4. Final Pass: Write to CSV
    print(f"Writing results to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target', 'value'])
        for (g1, g2), count in affinity_counts.items():
            if count > 5: # Filter out very weak correlations (noise)
                writer.writerow([g1, g2, count])

if __name__ == "__main__":
    # Ensure these filenames match your actual files
    fast_preprocess('../ml-latest/movies.csv', '../ml-latest/ratings.csv', 'genre_affinity.csv')
    print("Done!")