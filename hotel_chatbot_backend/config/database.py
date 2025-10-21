from pymongo import MongoClient

mongo = None

def init_db(app):
    """Initialize the MongoDB client using the provided Flask app.

    Uses app.logger to avoid requiring an application context when called
    during app setup.
    """
    global mongo
    try:
        mongo = MongoClient(app.config.get("MONGO_URI"))
        app.logger.info("✅ MongoDB Connected Successfully!")
    except Exception as e:
        # Log via app.logger so this function can be called during app setup
        try:
            app.logger.exception("Failed to connect to MongoDB: %s", e)
        except Exception:
            # Last-resort print if logger is not available
            print("Failed to connect to MongoDB:", e)
        mongo = None
    return mongo
