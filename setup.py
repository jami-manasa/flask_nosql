from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# MongoDB credentials from .env
username = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASS")
cluster = os.getenv("MONGO_CLUSTER")
db_name = os.getenv("DB_NAME")

# Build URI and connect
uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=muleconnect-cluster"
client = MongoClient(uri)
db = client[db_name]

# Define collections
users = db["users"]
community_posts = db["community_posts"]
mentorship_posts = db["mentorship_posts"]
mentorship_requests = db["mentorship_requests"]

# Insert sample data to force-create collections
users.insert_one({
    "username": "sample_user",
    "email": "sample@example.com",
    "password": "hashed_password"
})

community_posts.insert_one({
    "username": "sample_user",
    "content": "This is a sample community post",
    "image": None,
    "timestamp": datetime.utcnow()
})

mentorship_posts.insert_one({
    "username": "mentor_user",
    "title": "Career Advice in Data Science",
    "description": "Happy to help with resumes and interview prep.",
    "mentorship_type": "offer",  # or "request"
    "expertise_area": "Data Science",
    "timestamp": datetime.utcnow()
})

mentorship_requests.insert_one({
    "mentor": "mentor_user",
    "student": "sample_user",
    "message": "Can you mentor me on DS interviews?",
    "status": "pending",
    "timestamp": datetime.utcnow()
})

print("✅ All collections created with sample data!")
