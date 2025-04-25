from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from datetime import datetime
import os
from flask import request, redirect, url_for, render_template, session
from datetime import datetime
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

        db.jobs.insert_one(job)
        return redirect(url_for('jobs'))

    return render_template("post_job.html")

@app.route('/jobs')
def jobs():
    query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 18

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

    total_jobs = db.jobs.count_documents(search_filter)
    jobs_cursor = (
        db.jobs.find(search_filter)
        .sort("timestamp", -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    jobs = list(jobs_cursor)
    total_pages = (total_jobs + per_page - 1) // per_page

    return render_template("jobs.html", jobs=jobs, query=query, page=page, total_pages=total_pages)

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

    page = int(request.args.get('page', 1))
    per_page = 5
    total_posts = db.mule.count_documents({})
    skip = (page - 1) * per_page
    posts_cursor = db.mule.find().sort("timestamp", -1).skip(skip).limit(per_page)
    posts = list(posts_cursor)

    return render_template("home.html", posts=posts, page=page, total_pages=(total_posts + per_page - 1) // per_page)

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
            return redirect(url_for('dashboard'))  # ⬅️ Important: redirect to dashboard

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

    user_type = session.get('user_type')

    return render_template("dashboard.html", user_type=user_type, username=session.get("username"))







# ===========================
# 1. Create Mentorship Post
# ===========================
@app.route('/create-mentorship-post', methods=['GET', 'POST'])
def create_mentorship_post():
    if request.method == 'POST':
        post_type = request.form.get("mentorship_type")  # 'offer' or 'request'
        title = request.form.get("title")
        description = request.form.get("description")
        expertise_area = request.form.get("expertise_area")
        username = session.get("username", "anonymous")

        post = {
            "username": username,
            "title": title,
            "description": description,
            "expertise_area": expertise_area,
            "mentorship_type": post_type,
            "timestamp": datetime.utcnow()
        }

        db.mentorship_posts.insert_one(post)
        flash("✅ Your mentorship post has been submitted!")
        return redirect(url_for('mentorship_posts'))

    return render_template("mentorship_create_post.html")

# ===========================
# 2. View Mentorship Posts
# ===========================
@app.route('/mentorship-posts')
def mentorship_posts():
    offers = list(db.mentorship_posts.find({"mentorship_type": "offer"}).sort("timestamp", -1))
    requests = list(db.mentorship_posts.find({"mentorship_type": "request"}).sort("timestamp", -1))

    return render_template("posts.html", offers=offers, requests=requests)

# ===========================
# 3. Send Mentorship Request
# ===========================
@app.route('/send_request', methods=['POST'])
def send_request():
    mentor = request.form.get("mentor")
    message = request.form.get("message")
    student = session.get("username", "anonymous")

    entry = {
        "mentor": mentor,
        "student": student,
        "message": message,
        "status": "pending",
        "timestamp": datetime.utcnow()
    }

    db.mentorship_requests.insert_one(entry)
    flash("📩 Your mentorship request has been sent!")
    return redirect(url_for("mentorship_posts"))









# events

@app.route('/events')
def events():
    events_data = list(db.events.find().sort("date", 1))  # upcoming events first
    return render_template("events.html", events=events_data)













@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route('/reports')
def reports():
    return render_template("reports.html")




if __name__ == '__main__':
    app.run(debug=True)