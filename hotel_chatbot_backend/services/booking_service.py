from services.base_service import BaseService
from utils.date_validator import DateValidator
from config.database import database
import re

class ServiceHandler(BaseService):

    booking_state = {
        "checkin": None,
        "checkout": None,
        "guests": None,
        "room_type": None,
        "room_condition": None,
    }

    # ======================================================
    # FETCH AVAILABLE ROOMS BASED ON GUEST COUNT
    # ======================================================
    def get_available_rooms(self):
        try:
            guests = self.booking_state["guests"]

            if guests is None:
                return "⚠️ Guest count missing."

            rooms = list(database.db["rooms"].find(
                {"noOfPerson": {"$gte": guests}},
                {"roomNo": 1, "noOfPerson": 1}
            ))

            if not rooms:
                return f"❌ Sorry, no rooms are available for **{guests} guests**."

            result = f"📌 **Available Rooms for {guests} Guest(s):**\n"
            for idx, room in enumerate(rooms, start=1):
                result += f"{idx}) Room {room.get('roomNo')} (Capacity: {room.get('noOfPerson')})\n"

            return result

        except Exception as e:
            return f"⚠️ Error fetching rooms: {e}"

    # ======================================================
    # MAIN HANDLER
    # ======================================================
    def handle(self, message: str):

        text = message.lower().strip()

        # =====================================
        # 1) CHECK-IN DATE
        # =====================================
        if self.booking_state["checkin"] is None:
            parsed, reason = DateValidator.parse_date_verbose(text)
            if reason == "past":
                return "⚠️ The date you provided appears to be in the past. Please provide a future check-in date (today onward)."

            if parsed:
                # MUST BE FUTURE (parse_date_verbose already ensures reason=='ok')
                self.booking_state["checkin"] = parsed
                return "Great! When is your **check-out date**? 📅"

            return "Thank you for choosing our hotel! 😊\nWhen is your **check-in date**?"

        # =====================================
        # 2) CHECK-OUT DATE
        # =====================================
        if self.booking_state["checkout"] is None:
            parsed, reason = DateValidator.parse_date_verbose(text)
            if reason == "past":
                return "⚠️ The check-out date you entered is in the past. Please enter a future date after your check-in."

            if parsed:
                # Check-out must be after check-in AND future
                if not DateValidator.is_checkout_valid(self.booking_state["checkin"], parsed):
                    return "⚠️ Check-out date must be **after** check-in and also a future date. Please enter a valid one."

                self.booking_state["checkout"] = parsed
                return "How many **guests** will be staying? 👨‍👩‍👧"

            return "Please enter a valid **check-out date**."

        # =====================================
        # 3) NUMBER OF GUESTS
        # =====================================
        if self.booking_state["guests"] is None:
            guests = self.extract_guests(text)
            if guests:
                self.booking_state["guests"] = guests
                return "What type of **room** do you prefer? (Single / Double / Family) 🛏️"
            return "❌ Please enter a valid **number of guests**."

        # =====================================
        # 4) ROOM TYPE
        # =====================================
        if self.booking_state["room_type"] is None:
            room_type = self.extract_room_type(text)
            if room_type:
                self.booking_state["room_type"] = room_type
                return "Would you like an **AC or Non-AC** room? ❄️🔥"
            return "Please choose a valid room type (Single, Double, Family)."

        # =====================================
        # 5) ROOM CONDITION
        # =====================================
        if self.booking_state["room_condition"] is None:
            cond = self.extract_room_condition(text)
            if cond:
                self.booking_state["room_condition"] = cond
                return self.summary()
            return "Do you prefer **AC or Non-AC** room? ❄️🔥"

        return self.summary()

    # ======================================================
    # NATURAL LANGUAGE GUEST EXTRACTION
    # ======================================================
    def extract_guests(self, text):
        # Prevent dates from being detected as guest count
        date_patterns = [
            r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b",
            r"\b20\d{2}[-/]\d{1,2}\b",
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",
        ]
        for p in date_patterns:
            if re.search(p, text):
                return None

        if text.isdigit():
            g = int(text)
            return g if g >= 1 else None

        number_words = {
            "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10,
        }

        if text in number_words:
            return number_words[text]

        for word, num in number_words.items():
            if word in text:
                return num

        match = re.search(r"\b(\d+)\b", text)
        if match:
            g = int(match.group(1))
            return g if g >= 1 else None

        return None

    # ======================================================
    # EXTRACTORS
    # ======================================================
    def extract_room_type(self, text):
        if "single" in text: return "Single"
        if "double" in text: return "Double"
        if "family" in text: return "Family"
        return None

    def extract_room_condition(self, text):
        if "non ac" in text or "no ac" in text:
            return "Non-AC"
        if "ac" in text:
            return "AC"
        return None

    # ======================================================
    # SUMMARY
    # ======================================================
    def summary(self):
        s = self.booking_state
        rooms_text = self.get_available_rooms()
        # If no rooms are available, return a polite, actionable message
        if rooms_text.strip().lower().startswith("❌ sorry, no rooms are available"):
            guests = s.get('guests')
            guest_part = f" for **{guests} guests**" if guests else ""
            # include the user's requested booking details so they know what failed
            return (
                f"❌ Sorry — we can't book that day{guest_part}.\n\n"
                "Your requested booking:\n"
                f"- Check-in: {s.get('checkin')}\n"
                f"- Check-out: {s.get('checkout')}\n"
                f"- Guests: {s.get('guests')}\n"
                f"- Room Type: {s.get('room_type')}\n"
                f"- Room Condition: {s.get('room_condition')}\n\n"
                "Would you like to try different dates or reduce the number of guests?"
            )

        return (
            "✨ **Your Booking Summary**\n"
            f"- Check-in: {s['checkin']}\n"
            f"- Check-out: {s['checkout']}\n"
            f"- Guests: {s['guests']}\n"
            f"- Room Type: {s['room_type']}\n"
            f"- Room Condition: {s['room_condition']}\n\n"
            f"{rooms_text}\n\n"
            "Would you like me to **confirm the booking**? ✔️"
        )
