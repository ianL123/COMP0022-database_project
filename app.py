from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import analytics

app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db:3306/my_project_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    alerts = []

    # Get search inputs
    f_title = request.form.get('title', '')
    f_genre = request.form.get('genre', '')
    f_tag = request.form.get('tag', '') # We handle this carefully now
    f_year_start = request.form.get('year_start', '')
    f_year_end = request.form.get('year_end', '')

    # ... [Alerts logic remains the same] ...

    # OPTIMIZED SQL:
    # 1. We only join 'tags' if the user actually searched for a specific tag.
    # 2. We remove GROUP_CONCAT which is extremely slow on large datasets.
    
    base_sql = """
        SELECT 
            m.movieId,
            m.title, 
            m.genres,
            SUBSTRING(m.title, -5, 4) AS release_year,
            r.avg_rating,
            r.count as vote_count
        FROM movies m
        INNER JOIN average_ratings r ON m.movieId = r.movieId
    """
    
    # If user wants a specific tag, we use an EXISTS clause (much faster than a JOIN + GROUP BY)
    tag_filter = ""
    if f_tag:
        tag_filter = " AND EXISTS (SELECT 1 FROM tags t WHERE t.movieId = m.movieId AND t.tag LIKE :tag)"

    where_clause = """
        WHERE m.title LIKE :title
        AND m.genres LIKE :genre
        AND (:year_start = '' OR SUBSTRING(m.title, -5, 4) >= :year_start)
        AND (:year_end = '' OR SUBSTRING(m.title, -5, 4) <= :year_end)
    """

    order_by = "ORDER BY r.count DESC"
    
    sql = f"{base_sql} {where_clause} {tag_filter} {order_by} LIMIT 50"
    
    params = {
        'title': f'%{f_title}%',
        'genre': f'%{f_genre}%',
        'tag': f'%{f_tag}%',
        'year_start': f_year_start,
        'year_end': f_year_end
    }

    try:
        results = db.session.execute(text(sql), params).fetchall()
    except Exception as e:
        print(f"Database Error: {e}")
        alerts.append("Query error - Check if database is fully loaded.")

    return render_template('index.html', results=results, alerts=alerts, inputs=request.form)

# === Task 2: Analytics Reports Route ===
@app.route('/reports')
def reports():
    """
    Displays the analysis reports for Popularity and Polarization.
    Fetches data using the analytics module.
    """
    # Call functions from analytics.py
    popularity_data = analytics.get_genre_popularity(db.session)
    polarization_data = analytics.get_genre_polarization(db.session)
    
    return render_template('reports.html', 
                           popularity=popularity_data, 
                           polarization=polarization_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)