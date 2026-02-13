from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import check_password_hash
import os
import analytics
import predict as predict_algo

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')

PEPPER = os.environ.get('SECURITY_PEPPER')

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    alerts = []
    
    # 1. Check if user is logged in
    # This determines if the template shows the "+" button and "Sign In" button
    is_logged_in = 'user_id' in session 

    # 2. Use request.values to handle both GET (initial load) and POST (search button)
    inputs = request.values if request.method == 'POST' else {}

    # Core inputs
    f_title = inputs.get('title', '').strip()
    f_genre = inputs.get('genre', '').strip()
    f_tag = inputs.get('tag', '').strip()
    f_year_start = inputs.get('year_start', '').strip()
    f_year_end = inputs.get('year_end', '').strip()

    # Advanced inputs
    f_director = inputs.get('director', '').strip()
    f_actor = inputs.get('actor', '').strip()
    f_runtime = inputs.get('runtime', '').strip()
    f_region = inputs.get('region', '').strip()

    base_sql = """
        SELECT
            t.movieId,
            t.title,
            COALESCE(g.genres, '') AS genres,
            SUBSTRING(t.title, -5, 4) AS release_year,
            r.avg_rating,
            r.count AS vote_count,
            COALESCE(d.directors, '') AS directors,
            COALESCE(c.topCast, '') AS topCast,
            rt.runtimeMinutes,
            COALESCE(reg.regions, '') AS regions
        FROM movie_titles t
        LEFT JOIN average_ratings r
            ON t.movieId = r.movieId
        LEFT JOIN movie_runtimes rt
            ON t.movieId = rt.movieId
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
        LEFT JOIN (
            SELECT movieId, GROUP_CONCAT(region ORDER BY region SEPARATOR ', ') AS regions
            FROM movie_regions
            GROUP BY movieId
        ) reg ON t.movieId = reg.movieId
    """

    tag_filter = ""
    if f_tag:
        tag_filter = """
            AND EXISTS (
                SELECT 1 FROM tags tg
                WHERE tg.movieId = t.movieId AND tg.tag LIKE :tag
            )
        """

    where_clause = """
        WHERE t.title LIKE :title
        AND (:year_start = '' OR SUBSTRING(t.title, -5, 4) >= :year_start)
        AND (:year_end = '' OR SUBSTRING(t.title, -5, 4) <= :year_end)

        AND (:genre = '' OR EXISTS (
            SELECT 1 FROM movie_genres mg
            WHERE mg.movieId = t.movieId AND mg.genre LIKE :genre
        ))

        AND (:director = '' OR EXISTS (
            SELECT 1 FROM movie_directors md
            WHERE md.movieId = t.movieId AND md.director LIKE :director
        ))

        AND (:actor = '' OR EXISTS (
            SELECT 1 FROM movie_cast mc
            WHERE mc.movieId = t.movieId AND mc.actor LIKE :actor
        ))

        AND (:runtime = '' OR rt.runtimeMinutes >= :runtime)

        AND (:region = '' OR EXISTS (
            SELECT 1 FROM movie_regions mr
            WHERE mr.movieId = t.movieId AND mr.region LIKE :region
        ))
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
        # Logic check: if search returned results but metadata (directors) is missing
        if results and any(row.directors is None for row in results):
            alerts.append("Some movies are missing extended metadata from the 'others' database.")
    except Exception as e:
        print(f"Database Error: {e}")
        alerts.append("Search unavailable - please check your database connection.")

    user_folders = []
    if is_logged_in:
        folder_sql = text("SELECT id, folder_name FROM user_folders WHERE user_id = :u")
        user_folders = db.session.execute(folder_sql, {'u': session['user_id']}).fetchall()

    # 3. Pass is_logged_in to the template
    return render_template('index.html', 
        results=results, 
        alerts=alerts, 
        inputs=inputs, 
        is_logged_in=is_logged_in,
        folders=user_folders
    )

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

# === Task 6: Curated Colletion Planner ===

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 1. Fetch user from the database
        user_query = text("SELECT id, username, password FROM users WHERE username = :username")
        user = db.session.execute(user_query, {'username': username}).fetchone()

        if user:
            # 2. Add the Pepper to the user's input password
            peppered_input = password.strip() + PEPPER.strip()
            print(f"DEBUG: Input Password: {password}")
            print(f"DEBUG: Pepper being used: {PEPPER}")
            print(f"DEBUG: Combined String: {peppered_input}")
            print(f"DEBUG: Hashed string: {user.password.strip()}")
            
            # 3. Securely check the hash
            # check_password_hash handles the salt extraction automatically
            if check_password_hash(user.password.strip(), peppered_input):
                print("MATCH")
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
        
        # If user doesn't exist or hash doesn't match
        flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/create_folder', methods=['POST'])
def create_folder():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('folder_name', '').strip()
    user_id = session['user_id']
    
    if name:
        try:
            sql = text("INSERT INTO user_folders (user_id, folder_name) VALUES (:u, :n)")
            db.session.execute(sql, {'u': user_id, 'n': name})
            db.session.commit()
            flash(f'List "{name}" created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error creating list. Name might be too long.', 'danger')
    
    # This sends the user back to the search page with their inputs preserved
    return redirect(request.referrer or url_for('index'))

@app.route('/add_to_folder', methods=['POST'])
def add_to_folder():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    folder_id = request.form.get('folder_id')
    movie_id = request.form.get('movie_id')
    
    # Ensure this folder belongs to the logged-in user
    check_sql = text("SELECT id FROM user_folders WHERE id = :f AND user_id = :u")
    owner = db.session.execute(check_sql, {'f': folder_id, 'u': session['user_id']}).fetchone()
    
    if owner:
        insert_sql = text("INSERT IGNORE INTO folder_contents (folder_id, movie_id) VALUES (:f, :m)")
        db.session.execute(insert_sql, {'f': folder_id, 'm': movie_id})
        db.session.commit()
        flash("Added to list!", "success")
        
    return redirect(request.referrer or url_for('index'))

@app.route('/delete_from_folder', methods=['POST'])
def delete_from_folder():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    movie_id = request.form.get('movie_id')
    folder_id = request.form.get('folder_id')
    
    # Verify ownership before deleting
    sql = text("""
        DELETE fc FROM folder_contents fc
        JOIN user_folders uf ON fc.folder_id = uf.id
        WHERE fc.movie_id = :m AND fc.folder_id = :f AND uf.user_id = :u
    """)
    
    try:
        db.session.execute(sql, {'m': movie_id, 'f': folder_id, 'u': session['user_id']})
        db.session.commit()
        flash("Movie removed from list.", "info")
    except Exception as e:
        db.session.rollback()
        flash("Error removing movie.", "danger")
        
    return redirect(url_for('mylist'))

@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    folder_id = request.form.get('folder_id')
    
    # Since we used ON DELETE CASCADE in SQL, 
    # deleting the folder automatically removes its contents.
    sql = text("DELETE FROM user_folders WHERE id = :f AND user_id = :u")
    
    try:
        db.session.execute(sql, {'f': folder_id, 'u': session['user_id']})
        db.session.commit()
        flash("List deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting list.", "danger")
        
    return redirect(url_for('mylist'))

@app.route('/mylist')
def mylist():
    if 'user_id' not in session:
        flash("Please sign in to view your lists.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # 1. Fetch all folders belonging to this user
    folders_query = text("SELECT id, folder_name FROM user_folders WHERE user_id = :u")
    folders = db.session.execute(folders_query, {'u': user_id}).fetchall()

    # 2. Fetch all movies in those folders with metadata
    # We join folder_contents with movies and average_ratings
    items_query = text("""
        SELECT 
            fc.folder_id,
            m.movieId,
            m.title,
            r.avg_rating
        FROM folder_contents fc
        JOIN movie_titles m ON fc.movie_id = m.movieId
        JOIN average_ratings r ON m.movieId = r.movieId
        JOIN user_folders uf ON fc.folder_id = uf.id
        WHERE uf.user_id = :u
    """)
    items = db.session.execute(items_query, {'u': user_id}).fetchall()

    # Organize items by folder_id for easier looping in the template
    organized_data = {f.id: [] for f in folders}
    for item in items:
        organized_data[item.folder_id].append(item)

    return render_template('mylist.html', folders=folders, organized_data=organized_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
