from services.base_service import BaseService
from utils.date_validator import DateValidator
from config.database import database
import re
from datetime import datetime, timedelta

class ServiceHandler(BaseService):

    def __init__(self):
        self.reset()

    def reset(self):
        self.booking_state = {
            "checkin": None,
            "checkout": None,
            "guests": None,
            "room_condition": None,
            "available_rooms": [],  # Store fetched rooms
            "selected_room": None,  # Store user's choice
        }

    # ===============================
    # FETCH AVAILABLE ROOMS
    # ===============================
    def get_available_rooms(self, guests, room_condition):
        try:
            # Query: Capacity >= guests AND Room Type matches condition
            query = {
                "noOfPerson": {"$gte": guests},
                "roomType": room_condition
            }
            
            # Projection: Include necessary fields
            projection = {
                "roomNo": 1, 
                "noOfPerson": 1, 
                "price": 1, 
                "images": 1, 
                "roomType": 1
            }

            rooms = list(database.db["rooms"].find(query, projection))
            return rooms

        except Exception as e:
            print(f"Error fetching rooms: {e}")
            return []

    # ===============================
    # MAIN BOOKING HANDLER
    # ===============================
    def handle(self, message: str):

        text = message.strip()

        # --------------------------------------
        # 1. CHECK-IN DATE
        # --------------------------------------
        if self.booking_state["checkin"] is None:
            parsed, reason = DateValidator.parse_date_verbose(text)

            if reason == "none":
                return (
                    "Sure! 😊\n"
                    "When would you like to **check-in**?\n"
                    "(Please choose a date within the next 30 days.)"
                )

            if reason == "past":
                return (
                    "⚠️ The date you entered is in the past.\n"
                    "Please choose a future date within the next 30 days."
                )

            if reason == "too_far":
                return (
                    f"⚠️ Sorry! We only accept bookings within the next 30 days.\n\n"
                    f"The date you entered (**{text}**) is too far ahead.\n"
                    "Please select an earlier date."
                )

            if parsed:
                self.booking_state["checkin"] = parsed
                return "Perfect! When is your **check-out date**? 📅"

            return (
                "⚠️ I couldn't understand that date.\n"
                "Please enter a valid check-in date within the next 30 days."
            )

        # --------------------------------------
        # 2. CHECK-OUT DATE (MUST BE WITHIN 7 DAYS AFTER CHECK-IN)
        # --------------------------------------
        if self.booking_state["checkout"] is None:
            parsed, reason = DateValidator.parse_date_verbose(text)
            checkin_date = self.booking_state["checkin"]
            ci = datetime.strptime(checkin_date, "%Y-%m-%d").date()

            # INVALID FORMAT → NOT A DATE
            if reason == "none":
                return (
                    "⚠️ I couldn't understand that check-out date.\n"
                    "Please enter a date within **7 days after your check-in date**."
                )

            # USER ENTERED A VALID PARSED DATE
            if parsed:
                co = datetime.strptime(parsed, "%Y-%m-%d").date()

                # RULE 1: Must be after check-in
                if co <= ci:
                    return (
                        f"⚠️ The check-out date you entered (**{text}**) is before your check-in date.\n"
                        "Please enter a valid check-out date."
                    )

                # RULE 2: Must be within 7 days
                max_allowed = ci + timedelta(days=7)

                if co > max_allowed:
                    return (
                        f"⚠️ The check-out date you entered (**{text}**) is too far.\n"
                        "You can stay **up to 7 days** from your check-in date.\n\n"
                        f"Valid check-out range: **{ci} to {max_allowed}**.\n"
                        "Please enter a date within this range."
                    )

                # VALID CHECK-OUT DATE
                self.booking_state["checkout"] = parsed
                return "Would you like an **AC or Non-AC** room? ❄️🔥\n1. AC\n2. Non-AC"

            # FALLBACK
            return (
                "⚠️ Please enter a valid check-out date within 7 days after check-in."
            )

        # --------------------------------------
        # 3. ROOM CONDITION (AC / Non-AC)
        # --------------------------------------
        if self.booking_state["room_condition"] is None:
            cond = self.extract_room_condition(text.lower())
            if cond:
                self.booking_state["room_condition"] = cond
                return "How many **guests** will be staying? 👨‍👩‍👧"
            return f"⚠️ Sorry, '**{text}**' is not a valid option.\nPlease select:\n1. AC\n2. Non-AC"

        # --------------------------------------
        # 4. GUEST COUNT
        # --------------------------------------
        if self.booking_state["guests"] is None:
            guests = self.extract_guests(text)
            if guests:
                self.booking_state["guests"] = guests
                
                # FETCH ROOMS NOW
                rooms = self.get_available_rooms(guests, self.booking_state["room_condition"])
                self.booking_state["available_rooms"] = rooms
                
                if not rooms:
                    return (
                        f"❌ Sorry, no **{self.booking_state['room_condition']}** rooms are available "
                        f"for **{guests} guests**.\n"
                        "Would you like to try different options?"
                    )

                return self.format_room_list(rooms)

            return "❌ Please enter a valid **number of guests**."

        # --------------------------------------
        # 5. ROOM SELECTION
        # --------------------------------------
        if self.booking_state["selected_room"] is None:
            # User input should be the index number (1, 2, 3...)
            if text.isdigit():
                idx = int(text) - 1
                rooms = self.booking_state["available_rooms"]
                
                if 0 <= idx < len(rooms):
                    self.booking_state["selected_room"] = rooms[idx]
                    return self.summary()
            
            return (
                "⚠️ Please select a valid room number from the list above.\n"
                "(e.g., type '1' to select the first room)"
            )

        return self.summary()

    # ===============================
    # HELPERS
    # ===============================
    def extract_guests(self, text):
        date_patterns = [
            r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b",
            r"\b20\d{2}[-/]\d{1,2}\b",
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",
        ]
        for p in date_patterns:
            if re.search(p, text):
                return None

        if text.isdigit():
            return int(text) if int(text) >= 1 else None

        words = {
            "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10
        }

        if text.lower() in words:
            return words[text.lower()]

        match = re.search(r"\b(\d+)\b", text)
        if match:
            return int(match.group(1))

        return None

    def extract_room_condition(self, text):
        if "1" in text: return "AC"
        if "2" in text: return "Non-AC"
        
        if "non ac" in text or "no ac" in text:
            return "Non-AC"
        if "ac" in text:
            return "AC"
        return None

    def format_room_list(self, rooms):
        msg = f"📌 **Available {self.booking_state['room_condition']} Rooms:**\n\n"
        for i, room in enumerate(rooms, 1):
            msg += f"**{i}. Room {room.get('roomNo')}**\n"
            msg += f"   - Capacity: {room.get('noOfPerson')} Guests\n"
            msg += f"   - Price: ${room.get('price', 'N/A')}\n"
            
            # Add first image if available
            images = room.get('images', [])
            if images and isinstance(images, list) and len(images) > 0:
                msg += f"   - Image: {images[0]}\n"
            
            msg += "\n"
        
        msg += "👉 Please reply with the **Room Number** you want to book (e.g., 1)."
        return msg

    # ===============================
    # SUMMARY
    # ===============================
    def summary(self):
        s = self.booking_state
        room = s['selected_room']
        
        if not room:
            return "⚠️ Error: No room selected."

        return (
            "✨ **Your Booking Summary**\n"
            f"- Check-in: {s['checkin']}\n"
            f"- Check-out: {s['checkout']}\n"
            f"- Guests: {s['guests']}\n"
            f"- Room Condition: {s['room_condition']}\n"
            "----------------------------------\n"
            f"🏠 **Selected Room: {room.get('roomNo')}**\n"
            f"- Type: {room.get('roomType')}\n"
            f"- Capacity: {room.get('noOfPerson')} Guests\n"
            f"- Price: ${room.get('price')}\n"
            "\n"
            "Would you like me to **confirm the booking**? ✔️"
        )
