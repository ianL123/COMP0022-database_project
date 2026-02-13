from sqlalchemy import text
import json

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
    
def build_personality_genre_heatmap(db_session, top_n: int = 15):
    sql = text(f"""
    WITH top_genres AS (
      SELECT mg.genre AS genre, COUNT(*) AS cnt
      FROM personality_ratings pr
      JOIN movie_genres mg ON mg.movieId = pr.movieId
      GROUP BY mg.genre
      ORDER BY cnt DESC
      LIMIT {top_n}
    ),
    base AS (
      SELECT
        mg.genre AS genre,
        pr.rating AS rating,
        pd.openness AS openness,
        pd.agreeableness AS agreeableness,
        pd.emotional_stability AS emotional_stability,
        pd.conscientiousness AS conscientiousness,
        pd.extraversion AS extraversion
      FROM personality_ratings pr
      JOIN personality_data pd ON pd.userId = pr.userId
      JOIN movie_genres mg ON mg.movieId = pr.movieId
      JOIN top_genres tg ON tg.genre = mg.genre
      WHERE pr.rating IS NOT NULL
    ),
    longform AS (
      SELECT genre, rating, 'openness' AS trait, openness AS x FROM base WHERE openness IS NOT NULL
      UNION ALL
      SELECT genre, rating, 'agreeableness' AS trait, agreeableness AS x FROM base WHERE agreeableness IS NOT NULL
      UNION ALL
      SELECT genre, rating, 'emotional_stability' AS trait, emotional_stability AS x FROM base WHERE emotional_stability IS NOT NULL
      UNION ALL
      SELECT genre, rating, 'conscientiousness' AS trait, conscientiousness AS x FROM base WHERE conscientiousness IS NOT NULL
      UNION ALL
      SELECT genre, rating, 'extraversion' AS trait, extraversion AS x FROM base WHERE extraversion IS NOT NULL
    )
    SELECT
      genre,
      trait,
      COUNT(*) AS n,
      CASE
        WHEN
          (COUNT(*) * SUM(x*x) - POW(SUM(x), 2)) = 0
          OR (COUNT(*) * SUM(rating*rating) - POW(SUM(rating), 2)) = 0
        THEN NULL
        ELSE
          (COUNT(*) * SUM(x*rating) - SUM(x)*SUM(rating))
          / SQRT(
              (COUNT(*) * SUM(x*x) - POW(SUM(x), 2))
              * (COUNT(*) * SUM(rating*rating) - POW(SUM(rating), 2))
            )
      END AS corr
    FROM longform
    GROUP BY genre, trait
    ORDER BY trait, genre;
    """)

    rows = db_session.execute(sql).mappings().all()

    traits = ["openness", "agreeableness", "emotional_stability", "conscientiousness", "extraversion"]

    genres_sql = text(f"""
      SELECT mg.genre AS genre, COUNT(*) AS cnt
      FROM personality_ratings pr
      JOIN movie_genres mg ON mg.movieId = pr.movieId
      GROUP BY mg.genre
      ORDER BY cnt DESC
      LIMIT {top_n}
    """)
    genres = [r["genre"] for r in db_session.execute(genres_sql).mappings().all()]

    z = [[None for _ in genres] for _ in traits]
    nmat = [[0 for _ in genres] for _ in traits]

    trait_index = {t: i for i, t in enumerate(traits)}
    genre_index = {g: j for j, g in enumerate(genres)}

    for r in rows:
        ti = trait_index.get(r["trait"])
        gj = genre_index.get(r["genre"])
        if ti is None or gj is None:
            continue
        z[ti][gj] = None if r["corr"] is None else float(r["corr"])
        nmat[ti][gj] = int(r["n"])

    return {"traits": traits, "genres": genres, "z": z, "n": nmat}

def save_heatmap_cache(db_session, cache_key: str, payload: dict):
    db_session.execute(
        text("""
            INSERT INTO heatmap_cache (cache_key, payload)
            VALUES (:k, CAST(:p AS JSON))
            ON DUPLICATE KEY UPDATE payload = CAST(:p AS JSON), updated_at = CURRENT_TIMESTAMP
        """),
        {"k": cache_key, "p": json.dumps(payload)}
    )
    db_session.commit()

def load_heatmap_cache(db_session, cache_key: str):
    row = db_session.execute(
        text("SELECT payload FROM heatmap_cache WHERE cache_key = :k"),
        {"k": cache_key}
    ).mappings().first()
    if not row:
        return None
    payload = row["payload"]
    if isinstance(payload, (str, bytes)):
        return json.loads(payload)
    return payload