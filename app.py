from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, secrets, os, uuid, re
from pathlib import Path
from PIL import Image

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('FITGEAR_SECRET_KEY') or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
)
DB_PATH = Path(__file__).with_name('fitgear.db')
UPLOAD_DIR = Path(__file__).parent / 'static' / 'uploads' / 'profiles'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {'jpg','jpeg','png','webp'}
MAX_PROFILE_PHOTO_SIZE = 5 * 1024 * 1024
USERNAME_RE = re.compile(r'^[A-Za-z0-9_.-]{3,30}$')

PRODUCTS = [
    (1, 'Flex Resistance Band Set', 'bands', '5 resistance levels for strength, mobility and warm-ups.', 'https://images.pexels.com/photos/31467579/pexels-photo-31467579.jpeg?auto=compress&cs=tinysrgb&w=900', 449, 0, 0, 0, 'BEST SELLER'),
    (2, 'CoreGrip Training Mat', 'mats', 'Cushioned, non-slip surface with a clean textured finish.', 'https://images.pexels.com/photos/6146099/pexels-photo-6146099.jpeg?auto=compress&cs=tinysrgb&w=900', 899, 0, 0, 0, 'POPULAR'),
    (3, 'Move Duffel 32L', 'bags', 'Water-resistant gym bag with shoe compartment and padded strap.', 'https://images.pexels.com/photos/8554900/pexels-photo-8554900.jpeg?auto=compress&cs=tinysrgb&w=900', 1399, 0, 0, 0, 'NEW'),
    (4, 'Hydra Shaker 700ml', 'shakers', 'Leak-resistant shaker with measurement marks and mixing ball.', 'https://images.pexels.com/photos/16513595/pexels-photo-16513595.jpeg?auto=compress&cs=tinysrgb&w=900', 349, 0, 0, 0, ''),
    (5, 'ProLift Training Gloves', 'gloves', 'Breathable palm padding with secure wrist support.', 'https://images.pexels.com/photos/7697774/pexels-photo-7697774.jpeg?auto=compress&cs=tinysrgb&w=900', 499, 0, 0, 0, 'TOP RATED'),
    (6, 'DeepRoll Foam Roller', 'rollers', 'High-density recovery roller for post-workout release.', 'https://images.pexels.com/photos/4804294/pexels-photo-4804294.jpeg?auto=compress&cs=tinysrgb&w=900', 699, 0, 0, 0, 'RECOVERY'),
    (7, 'Mini Loop Band Trio', 'bands', 'Compact loop bands for glutes, mobility and travel workouts.', 'https://images.pexels.com/photos/6339604/pexels-photo-6339604.jpeg?auto=compress&cs=tinysrgb&w=900', 249, 0, 0, 0, 'TRAVEL'),
    (8, 'Everyday Yoga Mat 6mm', 'mats', 'Lightweight 6mm mat for yoga, stretching and home training.', 'https://images.pexels.com/photos/8539115/pexels-photo-8539115.jpeg?auto=compress&cs=tinysrgb&w=900', 649, 0, 0, 0, ''),
    (9, 'LiftPro Knee Sleeves', 'gloves', 'Supportive training sleeves for squats, lunges and leg sessions.', 'https://images.pexels.com/photos/7697774/pexels-photo-7697774.jpeg?auto=compress&cs=tinysrgb&w=900', 799, 0, 0, 0, ''),
    (10, 'GripMax Wrist Wraps', 'gloves', 'Adjustable wrist support for pressing and weight training.', 'https://images.pexels.com/photos/7697774/pexels-photo-7697774.jpeg?auto=compress&cs=tinysrgb&w=900', 299, 0, 0, 0, ''),
    (11, 'FlexCore Long Band', 'bands', 'Long resistance band for assisted stretching and full-body training.', 'https://images.pexels.com/photos/31467579/pexels-photo-31467579.jpeg?auto=compress&cs=tinysrgb&w=900', 299, 0, 0, 0, ''),
    (12, 'Travel Stretch Mat', 'mats', 'Foldable training mat designed for compact storage and travel.', 'https://images.pexels.com/photos/8539115/pexels-photo-8539115.jpeg?auto=compress&cs=tinysrgb&w=900', 749, 0, 0, 0, 'TRAVEL'),
    (13, 'Daily Carry Gym Bag 24L', 'bags', 'Compact everyday gym bag with separate wet-item pocket.', 'https://images.pexels.com/photos/8554900/pexels-photo-8554900.jpeg?auto=compress&cs=tinysrgb&w=900', 999, 0, 0, 0, ''),
    (14, 'SteelMix Shaker 750ml', 'shakers', 'Durable stainless-steel shaker with secure screw lid.', 'https://images.pexels.com/photos/16513595/pexels-photo-16513595.jpeg?auto=compress&cs=tinysrgb&w=900', 599, 0, 0, 0, ''),
    (15, 'ClearMix Shaker 600ml', 'shakers', 'Lightweight BPA-free shaker with easy-clean mixing insert.', 'https://images.pexels.com/photos/16513595/pexels-photo-16513595.jpeg?auto=compress&cs=tinysrgb&w=900', 249, 0, 0, 0, ''),
    (16, 'Recovery Ball Set', 'rollers', 'Two-density massage balls for targeted recovery and mobility.', 'https://images.pexels.com/photos/4804294/pexels-photo-4804294.jpeg?auto=compress&cs=tinysrgb&w=900', 399, 0, 0, 0, ''),
    (17, 'Compact Massage Roller', 'rollers', 'Portable textured roller for calves, shoulders and legs.', 'https://images.pexels.com/photos/4804294/pexels-photo-4804294.jpeg?auto=compress&cs=tinysrgb&w=900', 449, 0, 0, 0, ''),
    (18, 'Performance Gym Towel', 'bags', 'Quick-dry training towel with a compact carry loop.', 'https://images.pexels.com/photos/8554900/pexels-photo-8554900.jpeg?auto=compress&cs=tinysrgb&w=900', 249, 0, 0, 0, ''),
]

CATEGORY_NAMES = {'all':'All Gear', 'bands':'Resistance Bands', 'mats':'Yoga Mats', 'bags':'Gym Bags', 'shakers':'Shakers', 'gloves':'Gloves', 'rollers':'Foam Rollers'}

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        profile_photo TEXT,
        email_verified INTEGER NOT NULL DEFAULT 0,
        email_verify_token_hash TEXT,
        email_verify_expires TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Upgrade databases created by earlier FITGEAR versions.
    columns = {row['name'] for row in db.execute('PRAGMA table_info(users)').fetchall()}
    if 'profile_photo' not in columns:
        db.execute('ALTER TABLE users ADD COLUMN profile_photo TEXT')
    if 'username' not in columns:
        db.execute('ALTER TABLE users ADD COLUMN username TEXT')
    if 'email_verified' not in columns:
        db.execute('ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0')
    if 'email_verify_token_hash' not in columns:
        db.execute('ALTER TABLE users ADD COLUMN email_verify_token_hash TEXT')
    if 'email_verify_expires' not in columns:
        db.execute('ALTER TABLE users ADD COLUMN email_verify_expires TIMESTAMP')
    legacy = db.execute('SELECT id,email FROM users WHERE username IS NULL OR username=""').fetchall()
    for row in legacy:
        base = re.sub(r'[^A-Za-z0-9_.-]', '', row['email'].split('@')[0])[:24] or 'member'
        candidate = base
        n = 1
        while db.execute('SELECT 1 FROM users WHERE username=? AND id!=?', (candidate, row['id'])).fetchone():
            n += 1
            candidate = f"{base}{n}"[:30]
        db.execute('UPDATE users SET username=? WHERE id=?', (candidate, row['id']))
    db.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(product_id, user_id),
        FOREIGN KEY(product_id) REFERENCES products(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        image TEXT NOT NULL,
        price INTEGER NOT NULL,
        old_price INTEGER NOT NULL,
        rating REAL NOT NULL,
        reviews INTEGER NOT NULL,
        badge TEXT
    )''')
    db.executemany('''INSERT OR REPLACE INTO products
        (id,name,category,description,image,price,old_price,rating,reviews,badge)
        VALUES (?,?,?,?,?,?,?,?,?,?)''', PRODUCTS)
    # Ratings/review counts are calculated from real user reviews only.
    db.commit()

@app.context_processor
def inject_user():
    user = None
    if session.get('user_id'):
        user = get_db().execute('SELECT id,name,username,email,profile_photo,email_verified FROM users WHERE id=?', (session['user_id'],)).fetchone()
        if user is None:
            session.clear()
    return {'current_user': user, 'csrf_token': get_csrf_token(), 'category_names': CATEGORY_NAMES}

def get_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

def valid_csrf():
    return secrets.compare_digest(request.form.get('csrf_token',''), session.get('csrf_token',''))

@app.route('/')
def home():
    db = get_db()
    featured = db.execute('''SELECT p.*, ROUND(AVG(r.rating),1) AS live_rating, COUNT(r.id) AS live_reviews
                             FROM products p LEFT JOIN reviews r ON r.product_id=p.id
                             GROUP BY p.id ORDER BY p.id LIMIT 6''').fetchall()
    return render_template('index.html', products=featured)

@app.route('/shop')
def shop():
    category = request.args.get('category','all').lower()
    if category not in CATEGORY_NAMES: category = 'all'
    q = request.args.get('q','').strip()
    db = get_db()
    sql = '''SELECT p.*, ROUND(AVG(r.rating),1) AS live_rating, COUNT(r.id) AS live_reviews FROM products p LEFT JOIN reviews r ON r.product_id=p.id WHERE 1=1'''
    params = []
    if category != 'all':
        sql += ' AND category=?'; params.append(category)
    if q:
        sql += ' AND (name LIKE ? OR description LIKE ?)'; pattern=f'%{q}%'; params += [pattern, pattern]
    sql += ' ORDER BY id'
    products = db.execute(sql.replace(' ORDER BY id', ' GROUP BY p.id ORDER BY p.id'), params).fetchall()
    return render_template('shop.html', products=products, active_category=category, q=q)

@app.route('/product/<int:product_id>')
def product(product_id):
    db = get_db()
    item = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
    if not item:
        return redirect(url_for('shop'))
    reviews = db.execute('''SELECT r.rating, r.comment, r.created_at, u.name, u.profile_photo
                            FROM reviews r JOIN users u ON u.id=r.user_id
                            WHERE r.product_id=? ORDER BY r.created_at DESC''', (product_id,)).fetchall()
    related = db.execute('''SELECT p.*, ROUND(AVG(r.rating),1) AS live_rating, COUNT(r.id) AS live_reviews
                             FROM products p LEFT JOIN reviews r ON r.product_id=p.id
                             WHERE p.category=? AND p.id!=? GROUP BY p.id ORDER BY p.id LIMIT 3''',
                          (item['category'], product_id)).fetchall()
    stats = db.execute('SELECT ROUND(AVG(rating),1) AS avg_rating, COUNT(*) AS review_count FROM reviews WHERE product_id=?', (product_id,)).fetchone()
    return render_template('product.html', product=item, related=related, reviews=reviews,
                           avg_rating=stats['avg_rating'] or 0, review_count=stats['review_count'] or 0)

@app.route('/product/<int:product_id>/review', methods=['POST'])
def add_review(product_id):
    if not session.get('user_id'):
        flash('Please log in to leave a review.')
        return redirect(url_for('login', next=url_for('product', product_id=product_id)))
    db = get_db()
    review_user = db.execute('SELECT profile_photo FROM users WHERE id=?', (session['user_id'],)).fetchone()
    if not review_user or not review_user['profile_photo']:
        flash('Please upload a profile photo before leaving a review.')
        return redirect(url_for('profile', next=url_for('product', product_id=product_id)))
    if not valid_csrf():
        flash('Your form expired. Please try again.')
        return redirect(url_for('product', product_id=product_id))
    product = db.execute('SELECT id FROM products WHERE id=?', (product_id,)).fetchone()
    if not product:
        return redirect(url_for('shop'))
    try:
        rating = int(request.form.get('rating', '0'))
    except ValueError:
        rating = 0
    comment = request.form.get('comment', '').strip()
    if rating not in range(1, 6) or not comment or len(comment) > 1000:
        flash('Choose a rating from 1–5 and write a comment (max 1000 characters).')
        return redirect(url_for('product', product_id=product_id))
    try:
        db.execute('INSERT INTO reviews (product_id,user_id,rating,comment) VALUES (?,?,?,?)',
                   (product_id, session['user_id'], rating, comment))
        db.commit()
        flash('Your review has been posted.')
    except sqlite3.IntegrityError:
        flash('You already reviewed this item.')
    return redirect(url_for('product', product_id=product_id))

@app.route('/search', methods=['GET','POST'])
def search():
    q = (request.form.get('q','') if request.method == 'POST' else request.args.get('q','')).strip()
    return redirect(url_for('shop', q=q))

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        if not valid_csrf():
            flash('Your form expired. Please try again.'); return redirect(url_for('signup'))
        name=request.form.get('name','').strip()
        username=request.form.get('username','').strip()
        email=request.form.get('email','').strip().lower()
        password=request.form.get('password','')

        if not name or len(name)>80 or not USERNAME_RE.fullmatch(username):
            flash('Enter a valid name and username (3–30 letters, numbers, dots, dashes or underscores).')
            return render_template('signup.html')

        if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            flash('Password must be at least 8 characters and contain at least one letter and one number.')
            return render_template('signup.html')

        try:
            db=get_db()
            cur=db.execute('''INSERT INTO users
                (name,username,email,password_hash,profile_photo,email_verified,email_verify_token_hash,email_verify_expires)
                VALUES (?,?,?,?,?,1,NULL,NULL)''',
                (name,username,email,generate_password_hash(password),None))
            user_id=cur.lastrowid
            db.commit()
        except sqlite3.IntegrityError:
            flash('That username or email is already registered.')
            return render_template('signup.html')

        flash('Account created. You can log in now.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if not valid_csrf():
            flash('Your form expired. Please try again.'); return redirect(url_for('login'))
        identifier=request.form.get('identifier','').strip()
        password=request.form.get('password','')
        if not identifier or not password:
            flash('Enter your username/email and password.')
            return render_template('login.html')
        db=get_db()
        user=db.execute('''SELECT id,name,username,email,password_hash,email_verified,profile_photo
                           FROM users WHERE lower(username)=lower(?) OR lower(email)=lower(?)''',
                        (identifier,identifier)).fetchone()
        if not user or not check_password_hash(user['password_hash'],password):
            flash('Invalid username/email or password.')
            return render_template('login.html')
        session.clear(); session['user_id']=user['id']; session['csrf_token']=secrets.token_urlsafe(32)
        return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/profile')
def profile():
    if not session.get('user_id'): return redirect(url_for('login'))
    user=get_db().execute('SELECT id,name,username,email,profile_photo,email_verified FROM users WHERE id=?',
                          (session['user_id'],)).fetchone()
    if not user: session.clear(); return redirect(url_for('login'))
    return render_template('profile.html', user=user)

@app.route('/profile/photo', methods=['POST'])
def update_profile_photo():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if not valid_csrf():
        flash('Your form expired. Please try again.')
        return redirect(url_for('profile'))
    photo=request.files.get('profile_photo')
    saved_photo=save_profile_photo(photo)
    if not saved_photo:
        flash('Please upload a valid JPG, PNG or WEBP image up to 5 MB.')
        return redirect(url_for('profile'))
    db=get_db()
    old=db.execute('SELECT profile_photo FROM users WHERE id=?',(session['user_id'],)).fetchone()
    db.execute('UPDATE users SET profile_photo=? WHERE id=?',(saved_photo,session['user_id']))
    db.commit()
    if old and old['profile_photo']:
        (UPLOAD_DIR / old['profile_photo']).unlink(missing_ok=True)
    flash('Profile photo updated.')
    return redirect(url_for('profile'))

def save_profile_photo(file):
    if not file or not file.filename:
        return None
    if request.content_length and request.content_length > MAX_PROFILE_PHOTO_SIZE + 1024*64:
        return None
    ext=file.filename.rsplit('.',1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return None
    data=file.read(MAX_PROFILE_PHOTO_SIZE + 1)
    if len(data) > MAX_PROFILE_PHOTO_SIZE:
        return None
    try:
        from io import BytesIO
        with Image.open(BytesIO(data)) as img:
            img.verify()
    except Exception:
        return None
    filename=f"{uuid.uuid4().hex}.{ext}"
    (UPLOAD_DIR / filename).write_bytes(data)
    return filename

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('home'))

@app.route('/api/products')
def api_products():
    rows=get_db().execute('SELECT * FROM products ORDER BY id').fetchall()
    return jsonify([dict(r) for r in rows])

with app.app_context(): init_db()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
