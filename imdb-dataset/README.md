# IMDb Movies Dataset (Processed)

This dataset is a processed and consolidated movie table derived from the **IMDb public datasets**.  
It is designed for use in a database coursework project focusing on data modeling, querying, and dashboard-style exploration.

Each row represents **one movie** uniquely identified by its IMDb title identifier (`tconst`).

---

## File Description

### `big_movies.csv`

A single, denormalized table created by merging multiple IMDb source files after cleaning and filtering.

**Schema:**
tconst,
primaryTitle,
startYear,
runtimeMinutes,
genres,
averageRating,
numVotes,
directors,
topCast


---

## Column Descriptions

- **tconst**  
  IMDb unique identifier for the movie (e.g. `tt0114709`).

- **primaryTitle**  
  Official primary title of the movie.

- **startYear**  
  Release year of the movie.  
  May be `NULL` if missing in the source data.

- **runtimeMinutes**  
  Runtime of the movie in minutes.  
  May be `NULL` if unavailable.

- **genres**  
  Pipe-separated list of genres as provided by IMDb  
  (e.g. `Adventure|Animation|Comedy`).

- **averageRating**  
  Average IMDb user rating for the movie.

- **numVotes**  
  Number of user votes contributing to the IMDb rating.

- **directors**  
  Pipe-separated list of director names.  
  Limited to the first few directors per movie to avoid duplication.

- **topCast**  
  Pipe-separated list of leading actors and actresses.  
  Ordered by billing order and limited to the top cast members.

---

## Data Sources

The dataset is derived from the following **IMDb public datasets**:

- `title.basics.tsv`
- `title.ratings.tsv`
- `title.crew.tsv`
- `title.principals.tsv`
- `name.basics.tsv`

All source files were converted from TSV to CSV and then processed using custom ETL scripts.

---

## Data Processing Steps

1. Converted IMDb TSV files to CSV format.
2. Filtered records to include movies only (`titleType = movie`).
3. Removed adult titles.
4. Merged ratings, directors, and cast information using `tconst` as the primary key.
5. Aggregated directors and cast into pipe-separated fields to ensure one row per movie.
6. Exported the final consolidated table as `big_movies.csv`.

---

## Notes and Limitations

- Box office revenue and awards information are not included, as they are not available in the IMDb public datasets.
- IMDb user ratings and vote counts are used as proxies for popularity and audience reception.
- Some fields may contain missing values due to incomplete source data.
- The dataset is intended for educational use only.

---

## Intended Use

This dataset is suitable for:
- SQL-based filtering and sorting
- Movie browsing dashboards
- Analysis by year, genre, rating, director, or cast
- Demonstrating database schema design and ETL pipelines
