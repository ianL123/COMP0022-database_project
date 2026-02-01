import csv

input_file = '../ml-latest/movies.csv'
output_file = '../ml-latest/movie_genres.csv'

def process_genres():
    print(f"Opening {input_file}...")
    
    with open(input_file, mode='r', encoding='utf-8') as fin:
        # Use csv.reader to handle the quoted titles correctly
        reader = csv.DictReader(fin)
        
        with open(output_file, mode='w', encoding='utf-8', newline='') as fout:
            writer = csv.writer(fout)
            # Write header for our new CSV
            writer.writerow(['movieId', 'genre'])
            
            count = 0
            for row in reader:
                movie_id = row['movieId']
                genres_str = row['genres']
                
                # Skip the placeholder
                if genres_str == '(no genres listed)':
                    continue
                
                # Split by pipe and write a row for each individual genre
                genre_list = genres_str.split('|')
                for genre in genre_list:
                    writer.writerow([movie_id, genre])
                
                count += 1
                if count % 10000 == 0:
                    print(f"Processed {count} movies...")

    print(f"Successfully created {output_file}")

if __name__ == "__main__":
    process_genres()