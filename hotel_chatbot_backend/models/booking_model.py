from config.database import database
from datetime import datetime

class BookingModel:
    COLLECTION = "bookings"

    @staticmethod
    def create_booking(booking_data):
        """
        Inserts a new booking into the database.
        
        Args:
            booking_data (dict): A dictionary containing booking details.
            
        Returns:
            str: The ID of the inserted booking, or None if failed.
        """
        try:
            # Add timestamps
            booking_data["createdAt"] = datetime.utcnow()
            booking_data["updatedAt"] = datetime.utcnow()
            booking_data["status"] = booking_data.get("status", "pending")
            booking_data["__v"] = 0

            result = database.db[BookingModel.COLLECTION].insert_one(booking_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating booking: {e}")
            return None
