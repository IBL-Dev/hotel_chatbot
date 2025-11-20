from services.base_service import BaseService
from utils.date_validator import DateValidator
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
    # MAIN HANDLER
    # ======================================================
    def handle(self, message: str):

        text = message.lower().strip()

        # =====================================
        # 1) CHECK-IN DATE
        # =====================================
        if self.booking_state["checkin"] is None:
            date = DateValidator.parse_date(text)
            if date:
                self.booking_state["checkin"] = date
                return "Great! When is your **check-out date**? 📅"
            return "Thank you for choosing our hotel! 😊\nWhen is your **check-in date**?"

        # =====================================
        # 2) CHECK-OUT DATE
        # =====================================
        if self.booking_state["checkout"] is None:
            date = DateValidator.parse_date(text)
            if date:
                if not DateValidator.is_checkout_valid(self.booking_state["checkin"], date):
                    return "⚠️ Check-out date must be **after** your check-in date. Please enter a valid one."
                self.booking_state["checkout"] = date
                return "How many **guests** will be staying? 👨‍👩‍👧"
            return "Please enter a valid **check-out date** (e.g., 2025-05-12)."

        # =====================================
        # 3) NUMBER OF GUESTS (NATURAL LANGUAGE)
        # =====================================
        if self.booking_state["guests"] is None:
            guests = self.extract_guests(text)
            if guests:
                self.booking_state["guests"] = guests
                return "What type of **room** do you prefer? (Single / Double / Family) 🛏️"
            return "❌ Please enter a valid **number of guests**.\nExamples: 1, 2, 3 or 'three', 'four'."

        # =====================================
        # 4) ROOM TYPE
        # =====================================
        if self.booking_state["room_type"] is None:
            room_type = self.extract_room_type(text)
            if room_type:
                self.booking_state["room_type"] = room_type
                return "Would you like an **AC or Non-AC** room? ❄️🔥"
            return "Please choose a valid room type:\n👉 Single\n👉 Double\n👉 Family"

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
    # NATURAL-LANGUAGE GUEST EXTRACTOR
    # ======================================================
    def extract_guests(self, text):
        """
        Extracts guests from:
        - "3 guests"
        - "we are 4 people"
        - "only two"
        - "three"
        - "need room for five"
        Rejects:
        - dates (2025/02/12)
        - 2.5
        - negative or zero
        """

        # ----------------------------------
        # 1) BLOCK DATE-LIKE INPUTS
        # ----------------------------------
        date_patterns = [
            r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b",  # 2025/02/12
            r"\b20\d{2}[-/]\d{1,2}\b",             # 2025/02
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",    # 02/12/2025
        ]
        for p in date_patterns:
            if re.search(p, text):
                return None  # This is a date, NOT a guest count

        # ----------------------------------
        # 2) PURE DIGIT INPUT (e.g., "3")
        # ----------------------------------
        if text.isdigit():
            g = int(text)
            return g if g >= 1 else None

        # ----------------------------------
        # 3) NATURAL LANGUAGE WORD NUMBERS
        # ----------------------------------
        number_words = {
            "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10,
        }

        # exact word ("three")
        if text in number_words:
            return number_words[text]

        # word inside sentence ("we are three people")
        for word, num in number_words.items():
            if word in text:
                return num

        # ----------------------------------
        # 4) DIGIT INSIDE SENTENCE ("we have 2 people")
        # ----------------------------------
        match = re.search(r"\b(\d+)\b", text)
        if match:
            g = int(match.group(1))
            return g if g >= 1 else None

        # ----------------------------------
        # INVALID CASE
        # ----------------------------------
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
    # SUMMARY MESSAGE
    # ======================================================
    def summary(self):
        s = self.booking_state
        return (
            "✨ **Your Booking Summary**\n"
            f"- Check-in: {s['checkin']}\n"
            f"- Check-out: {s['checkout']}\n"
            f"- Guests: {s['guests']}\n"
            f"- Room Type: {s['room_type']}\n"
            f"- Room Condition: {s['room_condition']}\n\n"
            "Would you like me to **confirm the booking**? ✔️"
        )
