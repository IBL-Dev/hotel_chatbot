from flask import Flask
from config.database import db

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": f"Connected to MongoDB: {db.name}"}

if __name__ == '__main__':
    app.run(port=4070, debug=True)
