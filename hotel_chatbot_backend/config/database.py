# hotel_chatbot_backend/config/database.py

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    """Single Responsibility: Manage MongoDB connection"""

    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        try:
            mongo_uri = os.getenv("MONGO_URI")
            self.client = MongoClient(mongo_uri)
            self.db = self.client.get_database()  # Default DB from URI
            print("Database connection successful")
        except Exception as e:
            print(" Database connection failed:", e)
            raise e

# Create a global instance
database = Database()
