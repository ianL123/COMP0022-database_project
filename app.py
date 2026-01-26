from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Note: 'db' is the hostname defined in your docker-compose.yml
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db:3306/my_project_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    search_query = ""
    
    if request.method == 'POST':
        search_query = request.form.get('query', '')
        
        # We perform a JOIN on movieId to connect titles with ratings
        # Using raw SQL text to keep it simple and match your exact table names
        sql = """
            SELECT m.title, r.avg_rating, r.count 
            FROM movies m 
            JOIN average_ratings r ON m.movieId = r.movieId 
            WHERE m.title LIKE :title
            LIMIT 20
        """
        
        try:
            results = db.session.execute(
                db.text(sql), 
                {'title': f'%{search_query}%'}
            ).fetchall()
        except Exception as e:
            print(f"Database Error: {e}")
            results = []

    return render_template('index.html', results=results, query=search_query)

if __name__ == '__main__':
    # host='0.0.0.0' is required to be accessible inside Docker
    app.run(host='0.0.0.0', port=5000)