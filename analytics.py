from sqlalchemy import text

def get_genre_popularity(db_session):
    # Changed 'genres' to 'genre' to match your DESCRIBE output
    sql = """
        SELECT 
            genre, 
            avg_score, 
            total_votes,
            sentiment_gap
        FROM genre_stats_summary
        WHERE total_votes > 10000
        ORDER BY avg_score DESC
        LIMIT 20
    """
    try:
        return db_session.execute(text(sql)).fetchall()
    except Exception as e:
        print(f"Error in popularity report: {e}")
        return []

def get_genre_polarization(db_session):
    # Changed 'genres' to 'genre'
    sql = """
        SELECT 
            genre, 
            std_dev, 
            marmite_score,
            avg_score, 
            total_votes
        FROM genre_stats_summary
        WHERE total_votes > 10000
        ORDER BY std_dev DESC
        LIMIT 20
    """
    try:
        return db_session.execute(text(sql)).fetchall()
    except Exception as e:
        print(f"Error in polarization report: {e}")
        return []