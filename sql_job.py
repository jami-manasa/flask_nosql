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

# Build URI and connect to MongoDB
uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=muleconnect-cluster"
client = MongoClient(uri)
db = client[db_name]

# Define job_posts collection
job_posts = db["job_posts"]

# Insert sample job post
job_posts.insert_one({
    "title": "Backend Developer Intern for EdTech Startup",
    "description": "Looking for someone passionate about Python, Flask, and MongoDB. Flexible hours. Remote.",
    "posted_by": "Alumni - Sneha T.",
    "contact_info": "sneha@example.com",
    "tags": ["Remote", "Internship", "Flask", "MongoDB"],
    "timestamp": datetime.utcnow()
})

print("✅ job_posts collection created and sample job inserted!")
