from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
import os
import analytics
import predict as predict_algo

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')

PEPPER = os.environ.get('SECURITY_PEPPER', 'a-very-safe-fallback')

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    results = []
    alerts = []
    
    # 1. Check if user is logged in
    # This determines if the template shows the "+" button and "Sign In" button
    # is_logged_in = 'user_id' in session 
    # not needed anymore since we have inject_auth_state, but we can still use it in the backend logic if needed

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
            CASE
                WHEN TRIM(t.title) REGEXP '[(][0-9]{4}[)]$'
                THEN CAST(SUBSTRING(TRIM(t.title), -5, 4) AS UNSIGNED)
                ELSE NULL
            END AS release_year,
            r.avg_rating,
            r.count AS vote_count,
            COALESCE(d.directors, '') AS directors,
            COALESCE(c.topCast, '') AS topCast,  -- This is what we will display
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

        AND (:runtime = '' OR t.runtimeMinutes >= :runtime)

        AND (:region = '' OR EXISTS (
            SELECT 1 FROM movie_regions mr
            WHERE mr.movieId = t.movieId AND mr.region LIKE :region
        ))
    """


    order_by = "ORDER BY r.count DESC"
    sql = " ".join([base_sql, where_clause, tag_filter, order_by, "LIMIT 50"])
    
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
        print(f"Database Error")
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

    # 3. Pass is_logged_in to the template
    return render_template(
        'index.html', 
        results=results, 
        alerts=alerts, 
        inputs=inputs, 
        folders=user_folders,
        saved_movie_ids=saved_movie_ids  # new
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
            
            # 3. Securely check the hash
            # check_password_hash handles the salt extraction automatically
            if check_password_hash(user.password.strip(), peppered_input):
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
        
        # If user doesn't exist or hash doesn't match
        flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 1. Basic Validation
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        # 2. Check if username already exists
        check_query = text("SELECT id FROM users WHERE username = :username")
        existing_user = db.session.execute(check_query, {'username': username}).fetchone()
        
        if existing_user:
            flash('Username already exists. Please choose another.', 'warning')
            return redirect(url_for('register'))

        # 3. Apply Pepper and Hash
        # We append the PEPPER before hashing so the database stores a hash of the peppered string
        peppered_password = password.strip() + PEPPER.strip()
        hashed_password = generate_password_hash(peppered_password, method='pbkdf2:sha256')

        # 4. Save to Database
        try:
            insert_query = text("INSERT INTO users (username, password) VALUES (:username, :password)")
            db.session.execute(insert_query, {
                'username': username,
                'password': hashed_password
            })
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html')

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
        # Check if this user already has a folder with this name
        check_sql = text("SELECT id FROM user_folders WHERE user_id = :u AND folder_name = :n")
        existing = db.session.execute(check_sql, {'u': user_id, 'n': name}).fetchone()
        
        if existing:
            flash(f'A list named "{name}" already exists!', 'warning')
            return redirect(request.referrer or url_for('index'))

        try:
            sql = text("INSERT INTO user_folders (user_id, folder_name) VALUES (:u, :n)")
            db.session.execute(sql, {'u': user_id, 'n': name})
            db.session.commit()
            flash(f'List "{name}" created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error creating list. Name might be too long.', 'danger')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/add_to_folder', methods=['POST'])
def add_to_folder():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    folder_id = request.form.get('folder_id')
    movie_id = request.form.get('movie_id')
    user_id = session['user_id']
    
    # 1. Verify ownership AND check if movie is already in this folder
    # We can do this in one query using a LEFT JOIN or just checking both tables
    check_sql = text("""
        SELECT f.id, c.movie_id 
        FROM user_folders f 
        LEFT JOIN folder_contents c ON f.id = c.folder_id AND c.movie_id = :m
        WHERE f.id = :f AND f.user_id = :u
    """)
    result = db.session.execute(check_sql, {'f': folder_id, 'u': user_id, 'm': movie_id}).fetchone()
    
    if not result:
        flash("Unauthorized or folder does not exist.", "danger")
        return redirect(request.referrer or url_for('index'))
    
    # result[1] is the movie_id from the folder_contents table
    if result[1] is not None:
        flash("This movie is already in that list!", "info")
        return redirect(request.referrer or url_for('index'))

    # 2. Proceed with insertion
    try:
        insert_sql = text("INSERT INTO folder_contents (folder_id, movie_id) VALUES (:f, :m)")
        db.session.execute(insert_sql, {'f': folder_id, 'm': movie_id})
        db.session.commit()
        flash("Added to list!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Failed to add movie.", "danger")
        
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
        JOIN movies m ON fc.movie_id = m.movieId
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
    
