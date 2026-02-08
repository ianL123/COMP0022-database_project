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
    
def get_genre_chord_data(session):
    """
    Fetches pre-calculated genre correlations from the cache table.
    'value' controls ribbon thickness (total users).
    'score' controls ribbon color depth (relative affinity/Jaccard index).
    """
    # We now fetch the 'score' column added during preprocessing
    sql = """
        SELECT source, target, value, score 
        FROM genre_affinity 
        ORDER BY score DESC
    """
    try:
        rows = session.execute(text(sql)).fetchall()
        
        chord_data = []
        for row in rows:
            chord_data.append({
                "source": row[0],
                "target": row[1],
                "value": int(row[2]),     # Used for matrix thickness
                "score": float(row[3])    # Used for heatmap color scale
            })
        return chord_data
    except Exception as e:
        # If the container just restarted, the table might not be ready yet
        print(f"Error fetching chord data: {e}")
        return []