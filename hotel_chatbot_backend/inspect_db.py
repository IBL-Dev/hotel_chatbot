from config.database import database
from dotenv import load_dotenv
import os

load_dotenv()
database.connect()

try:
    room = database.db["rooms"].find_one()
    print("Room Document Sample:")
    print(room)
except Exception as e:
    print(f"Error: {e}")
