import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Mongo URI from .env
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_database()  # automatically uses the database in URI

print(f"✅ Connected to MongoDB database: {db.name}")
