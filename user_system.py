from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, PEPPER

# Define the Blueprint
user_system = Blueprint('user_system', __name__)

# === Task 6: Curated Colletion Planner ===

@user_system.route('/login', methods=['GET', 'POST'])
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

@user_system.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 1. Basic Validation
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('user_system.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('user_system.register'))

        # 2. Check if username already exists
        check_query = text("SELECT id FROM users WHERE username = :username")
        existing_user = db.session.execute(check_query, {'username': username}).fetchone()
        
        if existing_user:
            flash('Username already exists. Please choose another.', 'warning')
            return redirect(url_for('user_system.register'))

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
            return redirect(url_for('user_system.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html')

@user_system.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@user_system.route('/create_folder', methods=['POST'])
def create_folder():
    if 'user_id' not in session:
        return redirect(url_for('user_system.login'))
    
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

@user_system.route('/add_to_folder', methods=['POST'])
def add_to_folder():
    if 'user_id' not in session: return redirect(url_for('user_system.login'))
    
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

@user_system.route('/delete_from_folder', methods=['POST'])
def delete_from_folder():
    if 'user_id' not in session: return redirect(url_for('user_system.login'))
    
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
        
    return redirect(url_for('user_system.mylist'))

@user_system.route('/delete_folder', methods=['POST'])
def delete_folder():
    if 'user_id' not in session: return redirect(url_for('user_system.login'))
    
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
        
    return redirect(url_for('user_system.mylist'))

@user_system.route('/mylist')
def mylist():
    if 'user_id' not in session: return redirect(url_for('user_system.login'))
    u_id = session['user_id']

    # 1. Fetch Folders (Owned + Shared)
    # We use a UNION to get both types in one list
    folders_sql = text("""
        SELECT id, folder_name, user_id as owner_id FROM user_folders WHERE user_id = :u
        UNION
        SELECT f.id, f.folder_name, f.user_id FROM user_folders f
        JOIN folder_shares s ON f.id = s.folder_id WHERE s.shared_with_user_id = :u
    """)
    folders = db.session.execute(folders_sql, {'u': u_id}).fetchall()

    # 2. Fetch Movies for these folders
    items_query = text("""
        SELECT DISTINCT
            fc.folder_id,
            m.movieId,
            m.title,
            r.avg_rating
        FROM folder_contents fc
        JOIN movies m ON fc.movie_id = m.movieId
        JOIN average_ratings r ON m.movieId = r.movieId
        JOIN user_folders uf ON fc.folder_id = uf.id
        LEFT JOIN folder_shares fs ON uf.id = fs.folder_id
        WHERE uf.user_id = :u OR fs.shared_with_user_id = :u
    """)
    items = db.session.execute(items_query, {'u': u_id}).fetchall()

    # 3. Fetch Comments
    comments_query = text("""
        SELECT c.folder_id, c.comment_text, u.username, c.created_at
        FROM folder_comments c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at ASC
    """)
    all_comments = db.session.execute(comments_query).fetchall()

    # Organize data for Template
    organized_data = {f.id: [] for f in folders}
    for item in items:
        if item.folder_id in organized_data:
            organized_data[item.folder_id].append(item)

    comment_map = {f.id: [] for f in folders}
    for c in all_comments:
        if c.folder_id in comment_map:
            comment_map[c.folder_id].append(c)

    return render_template('mylist.html', 
                           folders=folders, 
                           organized_data=organized_data, 
                           comment_map=comment_map)

@user_system.route('/share_folder', methods=['POST'])
def share_folder():
    if 'user_id' not in session: return redirect(url_for('user_system.login'))
    
    folder_id = request.form.get('folder_id')
    target_username = request.form.get('username').strip()
    
    # 1. Verify current user owns the folder
    owner_check = db.session.execute(
        text("SELECT id FROM user_folders WHERE id = :f AND user_id = :u"),
        {'f': folder_id, 'u': session['user_id']}
    ).fetchone()
    
    if not owner_check:
        flash("Unauthorized to share this list.", "danger")
        return redirect(url_for('user_system.mylist'))

    # 2. Find the user to share with
    user_to_share = db.session.execute(
        text("SELECT id FROM users WHERE username = :n"),
        {'n': target_username}
    ).fetchone()

    if not user_to_share:
        flash("User not found.", "warning")
    else:
        try:
            db.session.execute(
                text("INSERT INTO folder_shares (folder_id, shared_with_user_id) VALUES (:f, :u)"),
                {'f': folder_id, 'u': user_to_share.id}
            )
            db.session.commit()
            flash(f"List shared with {target_username}!", "success")
        except Exception:
            flash("This list is already shared with that user.", "info")

    return redirect(url_for('user_system.mylist'))

@user_system.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user_id' not in session: return redirect(url_for('user_system.login'))
    
    folder_id = request.form.get('folder_id')
    content = request.form.get('comment_text', '').strip()
    
    # Verify access: Is owner OR is shared with user
    access_sql = text("""
        SELECT id FROM user_folders WHERE id = :f AND user_id = :u
        UNION
        SELECT folder_id FROM folder_shares WHERE folder_id = :f AND shared_with_user_id = :u
    """)
    if db.session.execute(access_sql, {'f': folder_id, 'u': session['user_id']}).fetchone() and content:
        db.session.execute(
            text("INSERT INTO folder_comments (folder_id, user_id, comment_text) VALUES (:f, :u, :t)"),
            {'f': folder_id, 'u': session['user_id'], 't': content}
        )
        db.session.commit()
    
    return redirect(request.referrer or url_for('user_system.mylist'))