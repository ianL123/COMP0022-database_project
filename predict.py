from sqlalchemy import text
import re

def get_prediction(db_session, form_data):
    """
    基于 Nearest Neighbor 算法预测评分并推荐相似电影。
    
    【优化更新】：
    1. 使用 REGEXP 实现精确的“单词匹配”，避免 "o" 匹配 "Tom"。
    2. 标签 (Tags) 匹配逻辑改为 DISTINCT，防止同一部电影因命中多个标签导致分数爆炸。
    3. 支持复杂的标签分隔符 (冒号、括号、问号等)。
    """
    
    # --- 1. 获取输入 ---
    p_genre = form_data.get('genre', '').strip()
    p_director = form_data.get('director', '').strip()
    p_actors = form_data.get('actors', '').strip()
    p_tags = form_data.get('tags', '').strip()
    p_runtime = form_data.get('runtime', '').strip()

    # 权重定义 (Heuristic Weights)
    WEIGHTS = {
        'director': 5.0,  
        'actor': 2.0,     
        'genre': 3.0,     
        'tag': 5.0,       
        'runtime': 1.0    
    }

    # 处理列表输入
    genre_list = [g.strip() for g in p_genre.split(',') if g.strip()]
    actor_list = [a.strip() for a in p_actors.split(',') if a.strip()]
    tag_list = [t.strip() for t in p_tags.split(',') if t.strip()]

    selects = []
    params = {}

    # === 辅助函数：生成精确匹配的正则字符串 ===
    def build_strict_regex(term, mode='name'):
        # 转义特殊字符，防止用户输入导致正则报错
        clean_term = re.escape(term)
        
        if mode == 'name':
            # 名字匹配：前后必须是字符串边界，或者非字母数字字符
            # 这样 'o' 不会匹配 'Tom'，但 'Nolan' 会匹配 'Christopher Nolan'
            return f"(^|[^a-zA-Z0-9]){clean_term}([^a-zA-Z0-9]|$)"
            
        elif mode == 'tag':
            # 标签匹配：根据你的要求，分隔符可以是 逗号, 空格, 左括号(, 右括号), 冒号:, 问号?
            # 这里的正则逻辑是：
            # 前面是：开头 OR 分隔符
            # 后面是：结尾 OR 分隔符
            # [ ,(:?] 表示字符集合
            return f"(^|[ ,(:?]){clean_term}([ ,):?]|$)"

    # ---------------------------------------------------------
    # A. 导演匹配 (精确匹配)
    # ---------------------------------------------------------
    if p_director:
        # 使用 REGEXP
        selects.append(f"SELECT movieId, {WEIGHTS['director']} as score FROM others WHERE directors REGEXP :director_regex")
        params['director_regex'] = build_strict_regex(p_director, 'name')

    # ---------------------------------------------------------
    # B. 演员匹配 (精确匹配)
    # ---------------------------------------------------------
    for i, actor in enumerate(actor_list):
        key = f"actor_{i}"
        selects.append(f"SELECT movieId, {WEIGHTS['actor']} as score FROM others WHERE topCast REGEXP :{key}")
        params[key] = build_strict_regex(actor, 'name')

    # ---------------------------------------------------------
    # C. 类型匹配 (精确匹配)
    # ---------------------------------------------------------
    for i, genre in enumerate(genre_list):
        key = f"genre_{i}"
        # 使用正则确保匹配 "Action" 而不是 "Reaction"
        # 这里的边界通常是 | (竖线) 或者字符串起止
        selects.append(f"SELECT movieId, {WEIGHTS['genre']} as score FROM movies WHERE genres REGEXP :{key}")
        params[key] = f"(^|\\|){re.escape(genre)}(\\||$)"

    # ---------------------------------------------------------
    # D. 标签匹配 (去重 & 复杂分隔符匹配) - [核心修改点]
    # ---------------------------------------------------------
    if tag_list:
        # 我们不使用循环生成多个 SELECT (这会导致分数叠加)
        # 而是生成一个大的 OR 查询，并使用 DISTINCT 确保每部电影只加一次分
        
        tag_conditions = []
        for i, tag in enumerate(tag_list):
            key = f"tag_rx_{i}"
            # 构造针对该 tag 的正则条件
            tag_conditions.append(f"tag REGEXP :{key}")
            params[key] = build_strict_regex(tag, 'tag')
        
        # 用 OR 连接所有标签条件
        combined_condition = " OR ".join(tag_conditions)
        
        # 使用 SELECT DISTINCT ! 
        # 这样无论电影匹配了多少个标签，或者同一个标签出现了多少次，只返回一行，只加一次分
        sql_tags = f"""
            SELECT DISTINCT movieId, {WEIGHTS['tag']} as score 
            FROM tags 
            WHERE {combined_condition}
        """
        selects.append(sql_tags)

    # ---------------------------------------------------------
    # E. 时长匹配 (保持不变)
    # ---------------------------------------------------------
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

    # --- 兜底逻辑 ---
    if not selects:
        return {'error': 'Please enter at least one criteria to generate a prediction.'}

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
        
        num_matches = len(results)
        avg_similarity = denominator / num_matches if num_matches > 0 else 0
        confidence_level = "Low"
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