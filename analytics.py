from sqlalchemy import text

def get_genre_popularity(db_session):
    """
    Task 2 Report A: Genre Popularity Analysis
    Ranked by Sentiment Gap to show which genres consistently 
    outperform the global average rating.
    """
    sql = """
        SELECT 
            genre, 
            avg_score, 
            sentiment_gap, 
            total_votes
        FROM genre_stats_summary
        ORDER BY sentiment_gap DESC
        LIMIT 20
    """
    try:
        # Returns: (Genre, Avg, Gap from Mean, Volume)
        return db_session.execute(text(sql)).fetchall()
    except Exception as e:
        print(f"Error in popularity report: {e}")
        return []

def get_genre_polarization(db_session):
    """
    Task 2 Report B: Genre Polarisation Analysis
    Ranked by Marmite Score to show genres with the most 
    extreme 'Love it or Hate it' ratings.
    """
    sql = """
        SELECT 
            genre, 
            marmite_score, 
            (count_1s * 100.0 / total_votes) as pct_1s,
            (count_5s * 100.0 / total_votes) as pct_5s,
            std_dev, 
            total_votes
        FROM genre_stats_summary
        ORDER BY marmite_score DESC
        LIMIT 20
    """
    try:
        # Returns: (genre, marmite, pct_1s, pct_2s, pct_3s, pct_4s, pct_5s, std_dev, total_votes)
        return db_session.execute(text(sql)).fetchall()
    except Exception as e:
        print(f"Error in polarization report: {e}")
        return []