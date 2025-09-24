from pymongo import MongoClient
from config.settings import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()  # "hotel_chatbot" from URI
