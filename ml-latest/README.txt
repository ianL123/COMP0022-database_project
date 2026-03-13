Data Sources
===============

This dataset (ml-latest) describes 5-star rating and free-text tagging activity from [MovieLens](http://movielens.org), a movie recommendation service. It contains 33832162 ratings and 2328315 tag applications across 86537 movies. These data were created by 330975 users between January 09, 1995 and July 20, 2023. This dataset was generated on July 20, 2023.

Users were selected at random for inclusion. All selected users had rated at least 1 movies. No demographic information is included. Each user is represented by an id, and no other information is provided.

The data are contained in the files `genome-scores.csv`, `genome-tags.csv`, `links.csv`, `movies.csv`, `ratings.csv` and `tags.csv`. More details about the contents and use of all these files follows.

This is a *development* dataset. As such, it may change over time and is not an appropriate dataset for shared research results. See available *benchmark* datasets if that is your intent.

This and other GroupLens data sets are publicly available for download at <http://grouplens.org/datasets/>.

Additional metadata was collected from several external sources to enrich the dataset with information such as actors, directors, runtime, region, posters, and movie descriptions.


External Metadata Sources
-------------------------

1. IMDb Official Datasets

Source:
https://datasets.imdbws.com/

The following metadata fields were extracted and cleaned from the IMDb official datasets:

- movie_cast.csv
- movie_directors.csv
- movie_regions.csv
- runtimeMinutes used in movies.csv

These datasets were processed to extract and normalize relevant information such as:

movieId, actor  
movieId, director  
movieId, region  
runtimeMinutes

The extracted data was cleaned and mapped to the MovieLens movie identifiers.


2. OMDb API (Poster Data)

Source:
https://www.omdbapi.com/

Movie poster URLs were retrieved using IMDb IDs through the OMDb API.  
After retrieval, the data was cleaned and stored in the following dataset:

movie_posters.csv

Fields:

movieId, poster_url


3. IMDb Web Scraping (Movie Descriptions)

Source:
https://www.imdb.com/

Movie descriptions were collected by retrieving the description section from IMDb movie pages using IMDb IDs.

The extracted text descriptions were cleaned and stored in:

movie_descriptions.csv

Fields:

movieId, description


Usage License
=============

Neither the University of Minnesota nor any of the researchers involved can guarantee the correctness of the data, its suitability for any particular purpose, or the validity of results based on the use of the data set. The data set may be used for any research purposes under the following conditions:

* The user may not state or imply any endorsement from the University of Minnesota or the GroupLens Research Group.
* The user must acknowledge the use of the data set in publications resulting from the use of the data set (see below for citation information).
* The user may redistribute the data set, including transformations, so long as it is distributed under these same license conditions.
* The user may not use this information for any commercial or revenue-bearing purposes without first obtaining permission from a faculty member of the GroupLens Research Project at the University of Minnesota.
* The executable software scripts are provided "as is" without warranty of any kind, either expressed or implied, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. The entire risk as to the quality and performance of them is with you. Should the program prove defective, you assume the cost of all necessary servicing, repair or correction.

In no event shall the University of Minnesota, its affiliates or employees be liable to you for any damages arising out of the use or inability to use these programs (including but not limited to loss of data or data being rendered inaccurate).

If you have any further questions or comments, please email <grouplens-info@umn.edu>


Citation
========

To acknowledge use of the dataset in publications, please cite the following paper:

> F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19. <https://doi.org/10.1145/2827872>


Further Information About GroupLens
===================================

GroupLens is a research group in the Department of Computer Science and Engineering at the University of Minnesota. Since its inception in 1992, GroupLens's research projects have explored a variety of fields including:

* recommender systems
* online communities
* mobile and ubiquitious technologies
* digital libraries
* local geographic information systems

GroupLens Research operates a movie recommender based on collaborative filtering, MovieLens, which is the source of these data. We encourage you to visit <http://movielens.org> to try it out! If you have exciting ideas for experimental work to conduct on MovieLens, send us an email at <grouplens-info@cs.umn.edu> - we are always interested in working with external collaborators.


Content and Use of Files
========================

Formatting and Encoding
-----------------------

The dataset files are written as [comma-separated values](http://en.wikipedia.org/wiki/Comma-separated_values) files with a single header row. Columns that contain commas (`,`) are escaped using double-quotes (`"`). These files are encoded as UTF-8. If accented characters in movie titles or tag values (e.g. Misérables, Les (1995)) display incorrectly, make sure that any program reading the data, such as a text editor, terminal, or script, is configured for UTF-8.


User Ids
--------

MovieLens users were selected at random for inclusion. Their ids have been anonymized. User ids are consistent between `ratings.csv` and `tags.csv` (i.e., the same id refers to the same user across the two files).


Movie Ids
---------

Only movies with at least one rating or tag are included in the dataset. These movie ids are consistent with those used on the MovieLens web site (e.g., id `1` corresponds to the URL <https://movielens.org/movies/1>). Movie ids are consistent between `ratings.csv`, `tags.csv`, `movies.csv`, and `links.csv` (i.e., the same id refers to the same movie across these four data files).


Ratings Data File Structure (ratings.csv)
-----------------------------------------

All ratings are contained in the file `ratings.csv`. Each line of this file after the header row represents one rating of one movie by one user, and has the following format:

    userId,movieId,rating,timestamp

The lines within this file are ordered first by userId, then, within user, by movieId.

Ratings are made on a 5-star scale, with half-star increments (0.5 stars - 5.0 stars).

Timestamps represent seconds since midnight Coordinated Universal Time (UTC) of January 1, 1970.


Tags Data File Structure (tags.csv)
-----------------------------------

All tags are contained in the file `tags.csv`. Each line of this file after the header row represents one tag applied to one movie by one user, and has the following format:

    userId,movieId,tag,timestamp

The lines within this file are ordered first by userId, then, within user, by movieId.

Tags are user-generated metadata about movies. Each tag is typically a single word or short phrase. The meaning, value, and purpose of a particular tag is determined by each user.

Timestamps represent seconds since midnight Coordinated Universal Time (UTC) of January 1, 1970.


Movies Data File Structure
--------------------------

movies.csv

Movie titles are entered manually or imported from <https://www.themoviedb.org/>, and include the year of release in parentheses. Errors and inconsistencies may exist in these titles.

Columns:
movieId, title, runtimeMinutes

Description:
Basic movie information. The title column contains both the movie title and the release year.


movie_genres.csv

Columns:
movieId, genre

Description:
Mapping between movies and their genres.

Genres are a pipe-separated list, and are selected from the following:

* Action
* Adventure
* Animation
* Children's
* Comedy
* Crime
* Documentary
* Drama
* Fantasy
* Film-Noir
* Horror
* Musical
* Mystery
* Romance
* Sci-Fi
* Thriller
* War
* Western
* (no genres listed)

movie_cast.csv  
Columns:
movieId, actor

Description:
List of actors appearing in each movie.


movie_directors.csv  
Columns:
movieId, director

Description:
Directors associated with each movie.


movie_regions.csv  
Columns:
movieId, region

Description:
Production region or country for each movie.


movie_posters.csv  
Columns:
movieId, poster_url

Description:
URL of the movie poster image used in the dashboard.


movie_descriptions.csv  
Columns:
movieId, description

Description:
Textual description or plot summary of each movie.



User Interaction Data
---------------------

tags.csv  
Columns:
userId, movieId, tag, timestamp

Description:
User generated tags describing movie attributes.



Analytical / Derived Data
-------------------------

The following datasets are generated through preprocessing and analysis to support reporting and prediction features.


average_ratings.csv  
Columns:
movieId, avg_rating, count

Description:
Average rating and number of ratings for each movie.


genre_affinity.csv  
Columns:
source, target, value, score

Description:
Relationship scores between genres derived from rating behaviour.


genre_stats_summary.csv  
Columns:
genres  
num_movies  
avg_score  
std_dev  
total_votes  
sentiment_gap  
marmite_score  
count_1s  
count_2s  
count_3s  
count_4s  
count_5s  

Description:
Statistical summary describing genre popularity, rating distribution, and genre polarisation metrics.



Cross-Validation
----------------

Prior versions of the MovieLens dataset included either pre-computed cross-folds or scripts to perform this computation. We no longer bundle either of these features with the dataset, since most modern toolkits provide this as a built-in feature. If you wish to learn about standard approaches to cross-fold computation in the context of recommender systems evaluation, see [LensKit](http://lenskit.org) for tools, documentation, and open-source code examples.


Data Processing Pipeline
===========================

The data used in this project is generated through a multi stage pipeline that combines MovieLens data with external movie metadata.

Step 1. MovieLens Dataset Import  
The MovieLens dataset provides the base movie identifiers, user ratings, and tags.

Step 2. External Metadata Collection  
Additional metadata is collected from external sources:

- IMDb official datasets for runtime, actors, directors, and region
- OMDb API for poster URLs
- IMDb webpages for movie descriptions

Step 3. Data Cleaning and Matching  
Collected data is cleaned and normalized.  
IMDb identifiers are used to match external metadata to the MovieLens movie IDs.

Step 4. Dataset Construction  
The cleaned datasets are exported into structured CSV tables used by the database.

Step 5. Analytical Dataset Generation  
Additional datasets such as genre statistics and rating summaries are computed to support reporting and predictive features within the application.