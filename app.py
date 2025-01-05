import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
import shutil
from flask_talisman import Talisman

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security headers
Talisman(app,
         content_security_policy={
             'default-src': "'self'",
             'img-src': "'self' data: https:",
             'script-src': "'self' 'unsafe-inline'",
             'style-src': "'self' 'unsafe-inline'",
         },
         force_https=True,
         strict_transport_security=True,
         session_cookie_secure=True,
         session_cookie_http_only=True)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Use persistent storage path if available
UPLOAD_PATH = os.getenv('UPLOAD_PATH', os.path.join('static', 'uploads'))
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

# Ensure upload directories exist and migrate existing files if needed
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'covers'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'hero'), exist_ok=True)

# If we're switching to persistent storage, migrate existing files
default_upload_path = os.path.join('static', 'uploads')
if UPLOAD_PATH != default_upload_path and os.path.exists(default_upload_path):
    for subdir in ['covers', 'hero']:
        src_dir = os.path.join(default_upload_path, subdir)
        dst_dir = os.path.join(UPLOAD_PATH, subdir)
        if os.path.exists(src_dir):
            for filename in os.listdir(src_dir):
                src_file = os.path.join(src_dir, filename)
                dst_file = os.path.join(dst_dir, filename)
                if os.path.isfile(src_file) and not os.path.exists(dst_file):
                    shutil.copy2(src_file, dst_file)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)

# Define models here
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(200))
    cover_image = db.Column(db.String(200))

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_title = db.Column(db.String(200), nullable=False, default="Top 50 Songs of 2024")
    hero_description = db.Column(db.Text, nullable=False, default="Discover the most anticipated albums and songs of 2024")
    hero_background = db.Column(db.String(200))
    stats_enabled = db.Column(db.Boolean, default=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    songs = Song.query.group_by(Song.title).order_by(Song.rank).all()  # Group by title to avoid duplicates
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    return render_template('index.html', 
                         songs=songs, 
                         current_time=datetime.now(),
                         settings=settings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin'))
        
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    songs = Song.query.group_by(Song.title).order_by(Song.rank).all()  # Group by title to avoid duplicates
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    return render_template('admin.html', songs=songs, settings=settings)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        settings.hero_title = request.form['title']
        settings.hero_description = request.form['description']
        settings.stats_enabled = 'stats_enabled' in request.form

        if 'background' in request.files:
            file = request.files['background']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'hero', filename))
                settings.hero_background = filename

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))

    return render_template('admin_settings.html', settings=settings)

@app.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.get(session['user_id'])
        
        if not check_password_hash(user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'error')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
        else:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully', 'success')
            return redirect(url_for('admin'))
            
    return render_template('change_password.html')

@app.route('/api/songs', methods=['GET'])
def get_songs():
    songs = Song.query.order_by(Song.rank).distinct().all()
    return jsonify([{
        'id': song.id,
        'rank': song.rank,
        'artist': song.artist,
        'title': song.title,
        'description': song.description,
        'link': song.link,
        'cover_image': song.cover_image
    } for song in songs])

@app.route('/api/songs/<int:song_id>', methods=['GET', 'PUT'])
@login_required
def song_api(song_id):
    song = Song.query.get_or_404(song_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': song.id,
            'rank': song.rank,
            'artist': song.artist,
            'title': song.title,
            'description': song.description,
            'link': song.link
        })
    
    elif request.method == 'PUT':
        data = request.json
        if 'artist' in data:
            song.artist = data['artist']
        if 'title' in data:
            song.title = data['title']
        if 'description' in data:
            song.description = data['description']
        if 'link' in data:
            song.link = data['link']
        
        db.session.commit()
        return jsonify({'message': 'Song updated successfully'})

@app.route('/api/upload_cover/<int:song_id>', methods=['POST'])
@login_required
def upload_cover(song_id):
    if 'cover' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['cover']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and allowed_file(file.filename):
        # Generate a unique filename using song_id and timestamp
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"song_{song_id}_{int(datetime.now().timestamp())}.{ext}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'covers', filename)
        file.save(file_path)
        
        # Update the song record
        song = Song.query.get_or_404(song_id)
        
        # Delete old cover if it exists
        if song.cover_image:
            old_file = os.path.join(app.config['UPLOAD_FOLDER'], 'covers', song.cover_image)
            if os.path.exists(old_file):
                os.remove(old_file)
        
        song.cover_image = filename
        db.session.commit()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': url_for('static', filename=f'uploads/covers/{filename}')
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

# Initialize database and admin user
with app.app_context():
    db.create_all()
    # Check if admin user exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123')  # Change this password!
        )
        db.session.add(admin_user)
        
        # Create default settings if they don't exist
        if not Settings.query.first():
            settings = Settings(
                hero_title="Top 50 Songs of 2024",
                hero_description="Discover the most anticipated albums and songs of 2024",
                stats_enabled=True
            )
            db.session.add(settings)
        
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
