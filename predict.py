from sqlalchemy import text

def get_prediction(db_session, form_data):
    """
    基于 Nearest Neighbor 算法预测评分并推荐相似电影。
    
    逻辑：
    1. 获取用户输入的新电影特征 (Director, Actor, Genre, Tag, Runtime)。
    2. 在数据库中查找匹配这些特征的旧电影，并根据匹配程度打分 (Similarity Score)。
    3. 聚合匹配分数，找出最相似的 Top 20 电影。
    4. 计算这 Top 20 电影的加权平均分作为预测结果。
    """
    
    # --- 1. 获取输入 ---
    p_genre = form_data.get('genre', '').strip()  # 获取原始字符串
    p_director = form_data.get('director', '').strip()
    p_actors = form_data.get('actors', '').strip()
    p_tags = form_data.get('tags', '').strip()
    p_runtime = form_data.get('runtime', '').strip()

    # 权重定义 (Heuristic Weights)
    WEIGHTS = {
        'director': 5.0,  
        'actor': 3.0,     
        'genre': 2.0,     # 每个匹配的类型都加分
        'tag': 1.0,       
        'runtime': 1.0    
    }

    # 处理列表输入 (逗号分隔)
    genre_list = [g.strip() for g in p_genre.split(',') if g.strip()]
    actor_list = [a.strip() for a in p_actors.split(',') if a.strip()]
    tag_list = [t.strip() for t in p_tags.split(',') if t.strip()]

    # --- 2. 构建 SQL 查询 (Feature Matching) ---
    selects = []
    params = {}

    # A. 导演匹配
    if p_director:
        selects.append(f"SELECT movieId, {WEIGHTS['director']} as score FROM others WHERE directors LIKE :director")
        params['director'] = f"%{p_director}%"

    # B. 演员匹配
    for i, actor in enumerate(actor_list):
        key = f"actor_{i}"
        selects.append(f"SELECT movieId, {WEIGHTS['actor']} as score FROM others WHERE topCast LIKE :{key}")
        params[key] = f"%{actor}%"

    # C. 类型匹配 (Genre Match) - [已修改为精确匹配]
    for i, genre in enumerate(genre_list):
        key = f"genre_{i}"
        # 使用 REGEXP (正则表达式) 进行精确单词匹配
        # 逻辑：匹配 "Action" 本身，或者 "Action|..."，或者 "...|Action"
        # 这样既能保证必须是这个词 (一模一样)，又不会漏掉多类型的电影
        selects.append(f"SELECT movieId, {WEIGHTS['genre']} as score FROM movies WHERE genres REGEXP :{key}")
        # 正则表达式：(^|\|)词(\||$)
        # 注意：Python 字符串里 | 需要转义，所以写成 \\|
        params[key] = f"(^|\\|){genre}(\\||$)"

    # D. 标签匹配
    for i, tag in enumerate(tag_list):
        key = f"tag_{i}"
        selects.append(f"SELECT movieId, {WEIGHTS['tag']} as score FROM tags WHERE tag LIKE :{key}")
        params[key] = f"%{tag}%"

    # E. 时长匹配
    if p_runtime:
        try:
            rt = int(p_runtime)
            if rt < 90: rt_bucket = 'Short'
            elif 90 <= rt <= 120: rt_bucket = 'Standard'
            elif 120 < rt <= 150: rt_bucket = 'Long'
            else: rt_bucket = 'Epic'
            
            sql_runtime = f"""
                SELECT movieId, {WEIGHTS['runtime']} as score 
                FROM others 
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

    # 如果用户没有输入任何有效条件
    if not selects:
        return {'error': 'Please enter at least one criteria (Genre, Director, Actor, etc.) to generate a prediction.'}

# --- 3. 组合最终查询 ---
    full_sql = " UNION ALL ".join(selects)

    final_query = f"""
        WITH matching_scores AS (
            {full_sql}
        ),
        similar_movies AS (
            SELECT 
                ms.movieId,
                SUM(ms.score) as total_similarity
            FROM matching_scores ms
            GROUP BY ms.movieId
            HAVING total_similarity > 0
            ORDER BY total_similarity DESC
            LIMIT 20
        )
        SELECT 
            m.title,
            m.genres,
            r.avg_rating,
            sm.total_similarity,
            o.directors,
            o.topCast
        FROM similar_movies sm
        JOIN movies m ON sm.movieId = m.movieId
        LEFT JOIN average_ratings r ON sm.movieId = r.movieId
        LEFT JOIN others o ON sm.movieId = o.movieId
        WHERE r.avg_rating IS NOT NULL
        ORDER BY sm.total_similarity DESC
    """

    try:
        results = db_session.execute(text(final_query), params).fetchall()

        if not results:
            return {'error': 'No similar movies found based on your criteria.'}

        # --- 4. 计算预测分 ---
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

        predicted_score = numerator / denominator if denominator > 0 else 0

        confidence_level = "Low"
        if denominator > 50: confidence_level = "High"
        elif denominator > 20: confidence_level = "Medium"

        return {
            'predicted_score': round(predicted_score, 2),
            'confidence': confidence_level,
            'similar_movies': similar_list,
            'match_count': len(similar_list)
        }

    except Exception as e:
        print(f"Prediction Algo Error: {e}")
        return {'error': 'Database query failed.'}