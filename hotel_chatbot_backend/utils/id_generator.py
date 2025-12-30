from datetime import datetime
import random
import time

def generate_structured_id(prefix, db, collection_name, id_field_name='id'):
    """
    Generates a structured ID like {prefix}_{YYMMDD}{count}
    Matches the logic provided in the TypeScript example.
    """
    now = datetime.utcnow()
    year = now.strftime('%y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    
    date_part = f"{year}{month}{day}"
    date_prefix = f"{prefix}_{date_part}"
    
    # Define the start and end of the current day for counting
    today_start = datetime(now.year, now.month, now.day)
    today_end = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
    
    # Retry up to 10 times to ensure uniqueness
    for attempt in range(10):
        # Count documents created today
        count = db[collection_name].count_documents({
            "createdAt": {"$gte": today_start, "$lte": today_end}
        })
        
        sequential = count + 1 + attempt
        candidate_id = f"{date_prefix}{sequential}"
        
        # Check if this ID already exists
        exists = db[collection_name].find_one({id_field_name: candidate_id})
        if not exists:
            return candidate_id
            
    # Fallback: use timestamp + random if all retries fail
    timestamp_part = str(int(time.time() * 1000))[-4:]
    random_part = random.randint(0, 999)
    return f"{date_prefix}{timestamp_part}{random_part}"

def generate_booking_id(db):
    """Specific wrapper for generating booking IDs."""
    return generate_structured_id('bid', db, 'bookings', 'bookingId')
