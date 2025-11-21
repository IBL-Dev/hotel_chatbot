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

            # Attempt connection
            self.client = MongoClient(mongo_uri)
            self.db = self.client.get_database()

            print("✅ MongoDB Connection Successful")

        except Exception as e:
            print("❌ MongoDB Connection Failed!")
            print(f"Error: {e}")
            raise e


# Global instance
database = Database()
