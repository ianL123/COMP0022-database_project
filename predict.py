from sqlalchemy import text
import re

def get_prediction(db_session, form_data):
    p_genre = form_data.get('genre', '').strip()
    p_director = form_data.get('director', '').strip()
    p_actors = form_data.get('actors', '').strip()
    p_tags = form_data.get('tags', '').strip()
    p_runtime = form_data.get('runtime', '').strip()

    WEIGHTS = {
        'director': 5.0,
        'actor': 2.0,
        'genre': 3.0,
        'tag': 5.0,
        'runtime': 1.0
    }

    genre_list = [g.strip() for g in p_genre.split(',') if g.strip()]
    actor_list = [a.strip() for a in p_actors.split(',') if a.strip()]
    tag_list = [t.strip() for t in p_tags.split(',') if t.strip()]

    selects = []
    params = {}

    def build_strict_regex(term, mode='name'):
        clean_term = re.escape(term)
        if mode == 'name':
            return f"(^|[^a-zA-Z0-9]){clean_term}([^a-zA-Z0-9]|$)"
        elif mode == 'tag':
            return f"(^|[ ,(:?]){clean_term}([ ,):?]|$)"

    # A. Director
    if p_director:
        selects.append(
            f"SELECT movieId, {WEIGHTS['director']} AS score "
            f"FROM movie_directors "
            f"WHERE director REGEXP :director_regex"
        )
        params['director_regex'] = build_strict_regex(p_director, 'name')

    # B. Actors
    for i, actor in enumerate(actor_list):
        key = f"actor_{i}"
        selects.append(
            f"SELECT movieId, {WEIGHTS['actor']} AS score "
            f"FROM movie_cast "
            f"WHERE actor REGEXP :{key}"
        )
        params[key] = build_strict_regex(actor, 'name')

    # C. Genres
    for i, genre in enumerate(genre_list):
        key = f"genre_{i}"
        # genre 表里每行就是一个 genre，不需要再写 (\\||$) 这种边界
        selects.append(
            f"SELECT movieId, {WEIGHTS['genre']} AS score "
            f"FROM movie_genres "
            f"WHERE genre = :{key}"
        )
        params[key] = genre

    # D. Tags (DISTINCT 去重保持不变)
    if tag_list:
        tag_conditions = []
        for i, tag in enumerate(tag_list):
            key = f"tag_rx_{i}"
            tag_conditions.append(f"tag REGEXP :{key}")
            params[key] = build_strict_regex(tag, 'tag')

        combined_condition = " OR ".join(tag_conditions)

        sql_tags = f"""
            SELECT DISTINCT movieId, {WEIGHTS['tag']} AS score
            FROM tags
            WHERE {combined_condition}
        """
        selects.append(sql_tags)

    # E. Runtime bucket: 改查 movie_runtimes
    if p_runtime:
        try:
            rt = int(p_runtime)
            if rt < 90:
                rt_bucket = 'Short'
            elif 90 <= rt <= 120:
                rt_bucket = 'Standard'
            elif 120 < rt <= 150:
                rt_bucket = 'Long'
            else:
                rt_bucket = 'Epic'

            sql_runtime = f"""
                SELECT movieId, {WEIGHTS['runtime']} AS score
                FROM movie_runtimes
                WHERE (
                    CASE
                        WHEN runtimeMinutes < 90 THEN 'Short'
                        WHEN runtimeMinutes BETWEEN 90 AND 120 THEN 'Standard'
                        WHEN runtimeMinutes BETWEEN 121 AND 150 THEN 'Long'
                        ELSE 'Epic'
                    END
                ) = :rt_bucket
            """
            selects.append(sql_runtime)
            params['rt_bucket'] = rt_bucket
        except ValueError:
            pass

    if not selects:
        return {'error': 'Please enter at least one criteria to generate a prediction.'}

    full_sql = " UNION ALL ".join(selects)

    # 最终展示：title 来自 movie_titles
    # genres / directors 用 GROUP_CONCAT 拼回去
    final_query = f"""
        WITH matching_scores AS (
            {full_sql}
        ),
        similar_movies AS (
            SELECT
                ms.movieId,
                SUM(ms.score) AS total_similarity
            FROM matching_scores ms
            GROUP BY ms.movieId
            HAVING total_similarity > 0
            ORDER BY total_similarity DESC
            LIMIT 20
        ),
        agg_genres AS (
            SELECT movieId, GROUP_CONCAT(genre ORDER BY genre SEPARATOR '|') AS genres
            FROM movie_genres
            GROUP BY movieId
        ),
        agg_directors AS (
            SELECT movieId, GROUP_CONCAT(director ORDER BY director SEPARATOR ', ') AS directors
            FROM movie_directors
            GROUP BY movieId
        )
        SELECT
            t.title,
            COALESCE(g.genres, '') AS genres,
            r.avg_rating,
            sm.total_similarity,
            COALESCE(d.directors, '') AS directors
        FROM similar_movies sm
        JOIN movie_titles t ON sm.movieId = t.movieId
        LEFT JOIN average_ratings r ON sm.movieId = r.movieId
        LEFT JOIN agg_genres g ON sm.movieId = g.movieId
        LEFT JOIN agg_directors d ON sm.movieId = d.movieId
        WHERE r.avg_rating IS NOT NULL
        ORDER BY sm.total_similarity DESC
    """

    try:
        results = db_session.execute(text(final_query), params).fetchall()

        if not results:
            return {'error': 'No similar movies found based on your criteria.'}

        numerator = 0.0
        denominator = 0.0
        similar_list = []

        for row in results:
            weight = float(row.total_similarity)
            rating = float(row.avg_rating)

            numerator += rating * weight
            denominator += weight

            similar_list.append({
                'title': row.title,
                'similarity': weight,
                'rating': rating,
                'genres': row.genres,
                'director': row.directors if row.directors else 'Unknown'
            })

        predicted_score = numerator / denominator if denominator > 0 else 0.0

        num_matches = len(results)
        avg_similarity = denominator / num_matches if num_matches > 0 else 0.0

        if avg_similarity >= 4.0:
            confidence_level = "High"
        elif avg_similarity >= 2.0:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

        return {
            'predicted_score': round(predicted_score, 2),
            'confidence': confidence_level,
            'similar_movies': similar_list,
            'match_count': len(similar_list)
        }

    except Exception as e:
        print(f"Prediction Algo Error: {e}")
        return {'error': 'Database query failed.'}
