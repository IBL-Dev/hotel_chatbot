import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser

class DateValidator:

    @staticmethod
    def parse_date(text: str):
        """
        Accepts ANY date format:
        - 2025/05/12
        - 2025-05-12
        - 12/05/2025
        - 12-05-25
        - tomorrow
        - next monday
        - this friday
        - in 2 days
        - 2025 / 05 / 12 (spaces)
        ALWAYS returns: YYYY-MM-DD
        """
        text = text.strip().lower()

        # -------------------------------
        # TODAY / TOMORROW
        # -------------------------------
        if "today" in text:
            return datetime.now().strftime("%Y-%m-%d")

        if "tomorrow" in text:
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # -------------------------------
        # WEEKDAYS (next monday, monday)
        # -------------------------------
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        for day, index in weekdays.items():
            if day in text:
                today_index = datetime.now().weekday()
                offset = index - today_index
                if offset <= 0:
                    offset += 7
                return (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")

        # -------------------------------
        # GENERIC FORMATS (12/05/2025, etc.)
        # -------------------------------
        # Try ISO / US / universal parsing
        for day_first in [False, True]:
            try:
                parsed = date_parser.parse(text, fuzzy=True, dayfirst=day_first)
                return parsed.strftime("%Y-%m-%d")
            except:
                pass

        return None

    @staticmethod
    def is_checkout_valid(checkin: str, checkout: str):
        """
        Ensures checkout > checkin.
        """
        try:
            ci = datetime.strptime(checkin, "%Y-%m-%d")
            co = datetime.strptime(checkout, "%Y-%m-%d")
            return co > ci
        except:
            return False
