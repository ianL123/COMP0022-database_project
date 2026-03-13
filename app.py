from flask import Flask, render_template, request, jsonify, session
from sqlalchemy import text
import os
import analytics
import predict as predict_algo
from user_system import user_system
from extensions import db

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')

PEPPER = os.environ.get('SECURITY_PEPPER', 'a-very-safe-fallback')

# Register the blueprint
app.register_blueprint(user_system)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Attach the db to the app
db.init_app(app)

@app.context_processor
def inject_globals():
    path = request.path
    active_map = {
        "/": "index",
        "/task2": "task2",
        "/task3": "task3",
        "/predict": "predict",
        "/task5_heatmap": "task5_heatmap",
    }
    return {
        "is_logged_in": ('user_id' in session),
        "current_user": session.get("username"),
        "active_page": active_map.get(path, "")
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    def get_input_list(input_str):
        if not input_str:
            return []
        return [p.strip() for p in input_str.split('|') if p.strip()]

    results = []
    alerts = []

    inputs = request.values if request.method == 'POST' else {}

    # Core inputs
    f_title = inputs.get('title', '').strip()
    f_tag = inputs.get('tag', '').strip()
    f_year_start = inputs.get('year_start', '').strip()
    f_year_end = inputs.get('year_end', '').strip()

    # Advanced inputs
    f_director = inputs.get('director', '').strip()
    f_actor = inputs.get('actor', '').strip()
    f_runtime = inputs.get('runtime', '').strip()

    # Multiple inputs
    f_genre_raw = get_input_list(inputs.get('genre', ''))
    f_region_raw = get_input_list(inputs.get('region', ''))

    base_sql = """
        SELECT
            t.movieId,
            t.title,
            COALESCE(g.genres, '') AS genres,
            CASE
                WHEN TRIM(t.title) REGEXP '[(][0-9]{4}[)]$'
                THEN CAST(SUBSTRING(TRIM(t.title), -5, 4) AS UNSIGNED)
                ELSE NULL
            END AS release_year,
            r.avg_rating,
            r.count AS vote_count,
            COALESCE(d.directors, '') AS directors,
            COALESCE(c.topCast, '') AS topCast,
            t.runtimeMinutes
        FROM movies t
        LEFT JOIN average_ratings r ON t.movieId = r.movieId
        LEFT JOIN (
            SELECT movieId, GROUP_CONCAT(genre ORDER BY genre SEPARATOR '|') AS genres
            FROM movie_genres GROUP BY movieId
        ) g ON t.movieId = g.movieId
        LEFT JOIN (
            SELECT movieId, GROUP_CONCAT(director ORDER BY director SEPARATOR ', ') AS directors
            FROM movie_directors GROUP BY movieId
        ) d ON t.movieId = d.movieId
        LEFT JOIN (
            SELECT movieId, GROUP_CONCAT(actor ORDER BY actor SEPARATOR ', ') AS topCast
            FROM movie_cast GROUP BY movieId
        ) c ON t.movieId = c.movieId
    """

    where_parts = ["""
        WHERE t.title LIKE :title
        AND (
          :year_start = '' OR
          (
            TRIM(t.title) REGEXP '[(][0-9]{4}[)]$'
            AND CAST(SUBSTRING(TRIM(t.title), -5, 4) AS UNSIGNED) >= CAST(:year_start AS UNSIGNED)
          )
        )
        AND (
          :year_end = '' OR
          (
            TRIM(t.title) REGEXP '[(][0-9]{4}[)]$'
            AND CAST(SUBSTRING(TRIM(t.title), -5, 4) AS UNSIGNED) <= CAST(:year_end AS UNSIGNED)
          )
        )
        AND (:director = '' OR EXISTS (
            SELECT 1 FROM movie_directors md
            WHERE md.movieId = t.movieId AND md.director LIKE :director
        ))
        AND (:actor = '' OR EXISTS (
            SELECT 1 FROM movie_cast mc
            WHERE mc.movieId = t.movieId AND mc.actor LIKE :actor
        ))
        AND (:runtime = '' OR t.runtimeMinutes >= :runtime)
    """]

    params = {
        'title': f'%{f_title}%',
        'tag': f'%{f_tag}%',
        'year_start': f_year_start,
        'year_end': f_year_end,
        'director': f'%{f_director}%',
        'actor': f'%{f_actor}%',
        'runtime': f_runtime,
    }

    # Genre fuzzy search: every entered genre must be matched
    for i, genre in enumerate(f_genre_raw):
        key = f'genre_{i}'
        where_parts.append(f"""
        AND EXISTS (
            SELECT 1
            FROM movie_genres mg
            WHERE mg.movieId = t.movieId
              AND mg.genre LIKE :{key}
        )
        """)
        params[key] = f'%{genre}%'

    # Region fuzzy search: every entered region must be matched
    for i, region in enumerate(f_region_raw):
        key = f'region_{i}'
        where_parts.append(f"""
        AND EXISTS (
            SELECT 1
            FROM movie_regions mr
            WHERE mr.movieId = t.movieId
              AND mr.region LIKE :{key}
        )
        """)
        params[key] = f'%{region}%'

    if f_tag:
        where_parts.append("""
        AND EXISTS (
            SELECT 1 FROM tags tg
            WHERE tg.movieId = t.movieId AND tg.tag LIKE :tag
        )
        """)

    order_by = "ORDER BY r.count DESC"
    sql = " ".join([base_sql] + where_parts + [order_by, "LIMIT 50"])

    try:
        results = db.session.execute(text(sql), params).fetchall()
        if results and any(row.directors is None for row in results):
            alerts.append("Some movies are missing extended metadata from the 'others' database.")
    except Exception as e:
        print(f"Database Error: {e}")
        alerts.append("Search unavailable - please check your database connection.")

    user_folders = []
    if 'user_id' in session:
        folder_sql = text("SELECT id, folder_name FROM user_folders WHERE user_id = :u")
        user_folders = db.session.execute(folder_sql, {'u': session['user_id']}).fetchall()

    saved_movie_ids = set()

    if 'user_id' in session:
        folder_sql = text("SELECT id, folder_name FROM user_folders WHERE user_id = :u")
        user_folders = db.session.execute(folder_sql, {'u': session['user_id']}).fetchall()
        saved_sql = text("""
            SELECT DISTINCT fc.movie_id
            FROM folder_contents fc
            JOIN user_folders uf ON uf.id = fc.folder_id
            WHERE uf.user_id = :u
        """)
        rows = db.session.execute(saved_sql, {'u': session['user_id']}).fetchall()
        saved_movie_ids = {r[0] for r in rows}

    return render_template(
        'index.html',
        results=results,
        alerts=alerts,
        inputs=inputs,
        folders=user_folders,
        saved_movie_ids=saved_movie_ids
    )

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    try:
        sql = text("""
            SELECT
                t.movieId,
                t.title,
                t.runtimeMinutes,
                CASE
                    WHEN TRIM(t.title) REGEXP '[(][0-9]{4}[)]$'
                    THEN CAST(SUBSTRING(TRIM(t.title), -5, 4) AS UNSIGNED)
                    ELSE NULL
                END AS release_year,
                r.avg_rating,
                r.count AS vote_count,
                COALESCE(mp.poster_url, '') AS poster_url,
                COALESCE(g.genres, '') AS genres,
                COALESCE(d.directors, '') AS directors,
                COALESCE(c.topCast, '') AS topCast,
                COALESCE(md.description, '') AS description
            FROM movies t
            LEFT JOIN average_ratings r ON t.movieId = r.movieId
            LEFT JOIN movie_posters mp ON t.movieId = mp.movieId
            LEFT JOIN movie_descriptions md ON t.movieId = md.movieId
            LEFT JOIN (
                SELECT movieId, GROUP_CONCAT(genre ORDER BY genre SEPARATOR '|') AS genres
                FROM movie_genres
                GROUP BY movieId
            ) g ON t.movieId = g.movieId
            LEFT JOIN (
                SELECT movieId, GROUP_CONCAT(director ORDER BY director SEPARATOR ', ') AS directors
                FROM movie_directors
                GROUP BY movieId
            ) d ON t.movieId = d.movieId
            LEFT JOIN (
                SELECT movieId, GROUP_CONCAT(actor ORDER BY actor SEPARATOR ', ') AS topCast
                FROM movie_cast
                GROUP BY movieId
            ) c ON t.movieId = c.movieId
            WHERE t.movieId = :movie_id
            LIMIT 1
        """)

        movie = db.session.execute(sql, {"movie_id": movie_id}).mappings().fetchone()
        print("movie =", movie)

        if not movie:
            return "Movie not found", 404

        return render_template("movie_detail.html", movie=movie)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<pre>{e}</pre>", 500

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

# === Task 3: Audience Affinity (Chord Diagram) ===
@app.route('/task3')
def task3():
    """
    Calculates genre correlation based on high user ratings.
    """
    # This calls the algorithm that creates the source/target matrix
    chord_data = analytics.get_genre_chord_data(db.session)
    
    return render_template('task3.html', chord_data=chord_data)

# === Task 4: Prediction Route ===
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    Handles both GET and POST requests for the prediction page.
    """
    prediction_result = None

    form_data = {
        "genre": "",
        "director": "",
        "actors": "",
        "runtime": "",
        "tags": ""
    }

    if request.method == 'POST':
        form_data = {
            "genre": request.form.get("genre", ""),
            "director": request.form.get("director", ""),
            "actors": request.form.get("actors", ""),
            "runtime": request.form.get("runtime", ""),
            "tags": request.form.get("tags", "")
        }

        prediction_result = predict_algo.get_prediction(db.session, form_data)

    return render_template('predict.html', prediction=prediction_result, form_data=form_data)

# === Task 5: Personality Traits ===
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
    app.run(host='0.0.0.0', port=5000)