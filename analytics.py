from sqlalchemy import text

def get_genre_popularity(db_session):
    """
    Task 2 Report A: Genre Popularity Analysis
    Calculates the average rating for each genre combination to identify high-performing categories.
    """
    sql = """
        SELECT 
            m.genres, 
            AVG(r.rating) as avg_score, 
            COUNT(r.rating) as total_votes
        FROM movies m
        JOIN ratings r ON m.movieId = r.movieId
        GROUP BY m.genres
        -- Filter out genres with too few votes to avoid statistical bias (e.g., 1 vote of 5.0)
        HAVING total_votes > 5 
        ORDER BY avg_score DESC
        LIMIT 20
    """
    try:
        return db_session.execute(text(sql)).fetchall()
    except Exception as e:
        print(f"Error in popularity report: {e}")
        return []

def get_genre_polarization(db_session):
    """
    Task 2 Report B: Genre Polarisation Analysis
    Calculates the Standard Deviation (STDDEV) of ratings. 
    A higher standard deviation indicates a wider spread of opinion (Love it vs. Hate it).
    """
    sql = """
        SELECT 
            m.genres, 
            STDDEV(r.rating) as std_dev, 
            AVG(r.rating) as avg_score,
            COUNT(r.rating) as total_votes
        FROM movies m
        JOIN ratings r ON m.movieId = r.movieId
        GROUP BY m.genres
        -- Filter out genres with too few votes
        HAVING total_votes > 5
        ORDER BY std_dev DESC
        LIMIT 20
    """
    try:
        return db_session.execute(text(sql)).fetchall()
    except Exception as e:
        print(f"Error in polarization report: {e}")
        return []