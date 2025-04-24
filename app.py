from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid

# Load environment variables from .env
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or 'muleconnect_super_secret_key_2025'
app.permanent_session_lifetime = timedelta(days=7)

# MongoDB setup
username = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASS")
cluster = os.getenv("MONGO_CLUSTER")
db_name = os.getenv("DB_NAME")

uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client[db_name]

# Define your users collection
users_collection = db["users"]


@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        job = {
            "title": request.form.get("title", "").strip(),
            "description": request.form.get("description", "").strip(),
            "posted_by": request.form.get("posted_by", "").strip(),
            "contact_info": request.form.get("contact_info", "").strip(),
            "tags": [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()],
            "location": request.form.get("location", "").strip(),
            "job_type": request.form.get("job_type", "").strip(),
            "timestamp": datetime.utcnow()
        }

        print("✅ Job Submitted:", job)
        db.jobs.insert_one(job)
        return redirect(url_for('jobs'))  # Redirect to job list after submission

    return render_template("post_job.html")

# --- Route to view all jobs ---


@app.route('/jobs')
def jobs():
    query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 18  # show more jobs per page to fill screen as you requested

    # Build a MongoDB search filter
    search_filter = {}
    if query:
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"posted_by": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}}
            ]
        }

    # Count and fetch paginated results
    total_jobs = db.jobs.count_documents(search_filter)
    jobs_cursor = (
        db.jobs.find(search_filter)
        .sort("timestamp", -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    jobs = list(jobs_cursor)
    total_pages = (total_jobs + per_page - 1) // per_page  # ceil logic

    return render_template("jobs.html",
                           jobs=jobs,
                           query=query,
                           page=page,
                           total_pages=total_pages)



# Ensure 'uploads' folder exists in static
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        content = request.form.get("content")
        image_file = request.files.get("image")
        image_filename = None

        if image_file and image_file.filename != '':
            ext = os.path.splitext(image_file.filename)[1]
            unique_name = str(uuid.uuid4()) + ext
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            image_file.save(image_path)
            image_filename = unique_name

        post = {
            "username": session.get("username", "anonymous"),
            "content": content,
            "image": image_filename,
            "timestamp": datetime.now()
        }
        db.mule.insert_one(post)
        return redirect(url_for('home'))

    # Pagination setup
    page = int(request.args.get('page', 1))
    per_page = 5
    total_posts = db.mule.count_documents({})
    skip = (page - 1) * per_page
    posts_cursor = db.mule.find().sort("timestamp", -1).skip(skip).limit(per_page)
    posts = list(posts_cursor)

    return render_template("home.html", posts=posts, page=page, total_pages=(total_posts + per_page - 1) // per_page)

# MongoDB setup

# Routes

# @app.route('/')
# def home():
#     posts = list(db.mule.find().sort("timestamp", -1))
#     return render_template("home.html", posts=posts)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user_type = request.form['user_type']

        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            flash('⚠️ Username already exists. Try logging in.')
            return redirect(url_for('signup'))

        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'user_type': user_type
        }

        users_collection.insert_one(user_data)
        flash('✅ Signup successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('auth.html', mode='signup')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            flash('🎉 Logged in successfully!')
            return redirect(url_for('home'))  # or dashboard

        flash('❌ Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('auth.html', mode='login')


@app.route('/logout')
def logout():
    session.clear()
    flash('You’ve been logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return f"Hello, {session['username']}! You're logged in as a {session['user_type']}."


@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route('/reports')
def reports():
    return render_template("reports.html")

@app.route('/create-mentorship-post', methods=['GET', 'POST'])
def create_mentorship_post():
    if request.method == 'POST':
        # handle post creation logic
        return redirect(url_for('mentorship_posts'))
    return render_template("create_post.html")

@app.route('/mentorship-posts')
def mentorship_posts():
    offers = list(db.mule.find({"type": "offer"}))
    requests = list(db.mule.find({"type": "request"}))
    return render_template("posts.html", offers=offers, requests=requests)

# Example POST route (optional)
@app.route('/send_request', methods=['POST'])
def send_request():
    mentor = request.form.get("mentor")
    message = request.form.get("message")
    db.requests.insert_one({"mentor": mentor, "message": message})
    return redirect(url_for("mentorship_posts"))

if __name__ == '__main__':
    app.run(debug=True)
