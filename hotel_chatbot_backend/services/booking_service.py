from services.base_service import BaseService
import re

class ServiceHandler(BaseService):

    booking_state = {
        "checkin": None,
        "checkout": None,
        "guests": None,
        "room_type": None,
        "room_condition": None,
    }

    def handle(self, message: str):

        text = message.lower().strip()

        # 1) CHECK-IN
        if self.booking_state["checkin"] is None:
            date = self.extract_date(text)
            if date:
                self.booking_state["checkin"] = date
            else:
                return "Thank you for choosing our hotel! 😊\nWhen is your **check-in date**?"

        # 2) CHECK-OUT
        if self.booking_state["checkout"] is None:
            date = self.extract_date(text)
            if date:
                self.booking_state["checkout"] = date
            else:
                return "Great! When is your **check-out date**? 📅"

        # 3) GUESTS
        if self.booking_state["guests"] is None:
            guests = self.extract_guests(text)
            if guests:
                self.booking_state["guests"] = guests
            else:
                return "How many **guests** will be staying? 👪"

        # 4) ROOM TYPE
        if self.booking_state["room_type"] is None:
            room_type = self.extract_room_type(text)
            if room_type:
                self.booking_state["room_type"] = room_type
            else:
                return "What type of **room** do you prefer? (Single / Double / Family) 🛏️"

        # 5) ROOM CONDITION
        if self.booking_state["room_condition"] is None:
            cond = self.extract_room_condition(text)
            if cond:
                self.booking_state["room_condition"] = cond
            else:
                return "Do you want **AC or Non-AC** room? ❄️🔥"

        return self.summary()

    # ---------------------------------------------------
    def extract_date(self, text):
        m = re.search(r"\b(20\d{2}[-/]\d{2}[-/]\d{2})\b", text)
        return m.group(1) if m else None

    def extract_guests(self, text):
        m = re.search(r"(\d+)\s*(guest|guests|people|persons)?", text)
        return int(m.group(1)) if m else None

    def extract_room_type(self, text):
        if "single" in text: return "Single"
        if "double" in text: return "Double"
        if "family" in text: return "Family"
        return None

    def extract_room_condition(self, text):
        if "non ac" in text or "no ac" in text: return "Non-AC"
        if "ac" in text: return "AC"
        return None

    # ---------------------------------------------------
    def summary(self):
        s = self.booking_state
        return (
            "✨ **Your Booking Details**\n"
            f"- Check-in: {s['checkin']}\n"
            f"- Check-out: {s['checkout']}\n"
            f"- Guests: {s['guests']}\n"
            f"- Room Type: {s['room_type']}\n"
            f"- Room Condition: {s['room_condition']}\n\n"
            "Would you like me to **confirm the booking now**? ✔️"
        )
