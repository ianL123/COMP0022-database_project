from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db:3306/my_project_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    f_title = request.form.get('title', '')
    f_genre = request.form.get('genre', '')
    f_tag = request.form.get('tag', '')
    f_year = request.form.get('year', '')

    sql = """
        SELECT 
            MAX(m.title) as title, 
            MAX(m.genres) as genres,
            SUBSTRING(MAX(m.title), -5, 4) AS release_year,
            IFNULL(MAX(r.avg_rating), 0) as avg_rating,
            IFNULL(MAX(r.count), 0) as vote_count,
            GROUP_CONCAT(DISTINCT t.tag SEPARATOR ', ') as all_tags
        FROM movies m
        LEFT JOIN average_ratings r ON m.movieId = r.movieId
        LEFT JOIN tags t ON m.movieId = t.movieId
        WHERE m.title LIKE :title
          AND m.genres LIKE :genre
          AND (:tag = '' OR t.tag LIKE :tag)
          AND (:year = '' OR m.title LIKE :year_search)
        GROUP BY m.movieId
        ORDER BY avg_rating DESC
        LIMIT 50
    """
    
    params = {
        'title': f'%{f_title}%',
        'genre': f'%{f_genre}%',
        'tag': f'%{f_tag}%',
        'year': f_year,
        'year_search': f'%({f_year})%'
    }

    try:
        results = db.session.execute(db.text(sql), params).fetchall()
    except Exception as e:
        print(f"Error: {e}")

    return render_template('index.html', results=results, 
                           inputs={'title': f_title, 'genre': f_genre, 'tag': f_tag, 'year': f_year})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
