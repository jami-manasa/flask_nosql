from pymongo import MongoClient
username = "mxj68970"
password = "OFYtfcmYaQJbrIoX"  # If this is the actual password
cluster = "muleconnect-cluster.owabrgv.mongodb.net"
db_name = "muleconnectdb"

uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=muleconnect-cluster"



try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    print("✅ Connected to fresh MongoDB!")
    print("Collections:", db.list_collection_names())
except Exception as e:
    print("❌ Connection failed:", e)
