from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import analytics
import predict as predict_algo

app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db:3306/my_project_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    alerts = []

    # Get Core inputs
    f_title = request.form.get('title', '').strip()
    f_genre = request.form.get('genre', '').strip()
    f_tag = request.form.get('tag', '').strip()
    f_year_start = request.form.get('year_start', '').strip()
    f_year_end = request.form.get('year_end', '').strip()

    # Get Advanced inputs
    f_director = request.form.get('director', '').strip()
    f_actor = request.form.get('actor', '').strip()
    f_runtime = request.form.get('runtime', '').strip()
    f_region = request.form.get('region', '').strip()

    base_sql = """
        SELECT 
            m.movieId,
            m.title, 
            m.genres,
            SUBSTRING(m.title, -5, 4) AS release_year,
            r.avg_rating,
            r.count as vote_count,
            o.directors,
            o.topCast,
            o.runtimeMinutes,
            o.regions
        FROM movies m
        INNER JOIN average_ratings r ON m.movieId = r.movieId
        LEFT JOIN others o ON m.movieId = o.movieId
    """
    
    tag_filter = ""
    if f_tag:
        tag_filter = " AND EXISTS (SELECT 1 FROM tags t WHERE t.movieId = m.movieId AND t.tag LIKE :tag)"

    where_clause = """
        WHERE m.title LIKE :title
        AND m.genres LIKE :genre
        AND (:year_start = '' OR SUBSTRING(m.title, -5, 4) >= :year_start)
        AND (:year_end = '' OR SUBSTRING(m.title, -5, 4) <= :year_end)
        AND (:director = '' OR o.directors LIKE :director)
        AND (:actor = '' OR o.topCast LIKE :actor)
        AND (:runtime = '' OR o.runtimeMinutes >= :runtime)
        AND (:region = '' OR o.regions LIKE :region)
    """

    order_by = "ORDER BY r.count DESC"
    sql = f"{base_sql} {where_clause} {tag_filter} {order_by} LIMIT 50"
    
    params = {
        'title': f'%{f_title}%',
        'genre': f'%{f_genre}%',
        'tag': f'%{f_tag}%',
        'year_start': f_year_start,
        'year_end': f_year_end,
        'director': f'%{f_director}%',
        'actor': f'%{f_actor}%',
        'runtime': f_runtime,
        'region': f'%{f_region}%'
    }

    try:
        results = db.session.execute(text(sql), params).fetchall()
        if results and any(row.directors is None for row in results):
            alerts.append("Some movies are missing extended metadata.")
    except Exception as e:
        print(f"Database Error: {e}")
        alerts.append("Query error - Check database connection.")

    return render_template('index.html', results=results, alerts=alerts, inputs=request.form)

# === Task 2: Analytics Reports Route ===
@app.route('/task2')
def task2():
    """
    Displays the analysis reports for Popularity and Polarization.
    """
    popularity_data = analytics.get_genre_popularity(db.session)
    polarization_data = analytics.get_genre_polarization(db.session)
    
    return render_template('task2.html', 
                           popularity=popularity_data, 
                           polarization=polarization_data)

# === Task 4: Prediction Route ===
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    处理电影评分预测请求。
    GET: 显示空表单。
    POST: 接收表单数据，调用 predict_algo 计算，返回结果，并回填表单。
    """
    prediction_result = None

    # 关键：准备一个可回填的 dict（GET 也要传给模板）
    form_data = {
        "genre": "",
        "director": "",
        "actors": "",
        "runtime": "",
        "tags": ""
    }

    if request.method == 'POST':
        # 关键：把 request.form 转成普通 dict，避免 ImmutableMultiDict 的坑
        form_data = {
            "genre": request.form.get("genre", ""),
            "director": request.form.get("director", ""),
            "actors": request.form.get("actors", ""),
            "runtime": request.form.get("runtime", ""),
            "tags": request.form.get("tags", "")
        }

        prediction_result = predict_algo.get_prediction(db.session, form_data)

    return render_template('predict.html', prediction=prediction_result, form_data=form_data)


# === Task 3: Audience Affinity (Chord Diagram) ===
@app.route('/task3')
def task3():
    """
    Calculates genre correlation based on high user ratings.
    """
    # This calls the algorithm that creates the source/target matrix
    chord_data = analytics.get_genre_chord_data(db.session)
    
    return render_template('task3.html', chord_data=chord_data)

@app.route('/task5_heatmap')
def task5_heatmap():
    return render_template('task5_heatmap.html')

@app.route('/api/task5_heatmap')
def api_task5_heatmap():
    ensure_heatmap_cache()
    data = analytics.load_heatmap_cache(db.session, HEATMAP_CACHE_KEY)
    return jsonify(data)

HEATMAP_CACHE_KEY = "task5_top15"
_heatmap_ready = False

def ensure_heatmap_cache():
    global _heatmap_ready
    if _heatmap_ready:
        return

    cached = analytics.load_heatmap_cache(db.session, HEATMAP_CACHE_KEY)
    if cached is not None:
        _heatmap_ready = True
        return

    payload = analytics.build_personality_genre_heatmap(db.session, top_n=15)
    analytics.save_heatmap_cache(db.session, HEATMAP_CACHE_KEY, payload)
    _heatmap_ready = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
