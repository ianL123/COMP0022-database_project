from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db:3306/my_project_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    alerts = []

    f_title = request.form.get('title', '')
    f_genre = request.form.get('genre', '')
    f_tag = request.form.get('tag', '')
    f_year_start = request.form.get('year_start', '')
    f_year_end = request.form.get('year_end', '')

    f_director = request.form.get('director', '')
    f_actor = request.form.get('actor', '')
    f_awards = request.form.get('awards', '')
    f_runtime = request.form.get('runtime', '')
    f_language = request.form.get('language', '')

    if f_director:
        alerts.append(f"需要找导演的数据 (目前数据库缺失)")
    
    if f_actor:
        alerts.append(f"需要找演员的数据 (目前数据库缺失)")
        
    if f_awards:
        alerts.append("需要找奖项的数据 (目前数据库缺失)")
        
    if f_runtime:
        alerts.append("需要找时长的数据 (目前数据库缺失)")
        
    if f_language:
        alerts.append("需要找语言的数据 (目前数据库缺失)")

    sql = """
        SELECT 
            m.movieId,
            MAX(m.title) as title, 
            MAX(m.genres) as genres,
            -- 提取标题里的年份 (假设格式总是 'Title (YYYY)')
            SUBSTRING(MAX(m.title), -5, 4) AS release_year,
            IFNULL(MAX(r.avg_rating), 0) as avg_rating,
            IFNULL(MAX(r.count), 0) as vote_count,
            GROUP_CONCAT(DISTINCT t.tag SEPARATOR ', ') as all_tags
        FROM movies m
        LEFT JOIN average_ratings r ON m.movieId = r.movieId
        LEFT JOIN tags t ON m.movieId = t.movieId
        WHERE 
            m.title LIKE :title
            AND m.genres LIKE :genre
            AND (:tag = '' OR t.tag LIKE :tag)
            -- 年份范围筛选 (比较字符串 '1995' >= '1990')
            AND (:year_start = '' OR SUBSTRING(m.title, -5, 4) >= :year_start)
            AND (:year_end = '' OR SUBSTRING(m.title, -5, 4) <= :year_end)
        GROUP BY m.movieId
        ORDER BY avg_rating DESC
        LIMIT 50
    """
    
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
        alerts.append("数据库连接或查询错误")

    return render_template('index.html', 
                           results=results, 
                           alerts=alerts,
                           inputs=request.form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)