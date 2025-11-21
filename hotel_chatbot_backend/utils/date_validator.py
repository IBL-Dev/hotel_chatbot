import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser

class DateValidator:

    @staticmethod
    def parse_date(text: str):
        """
        Accept ANY format:
        - 2025/05/12
        - 2025-05-12
        - 12/05/2025
        - tomorrow
        - next monday
        - in 2 days
        ALWAYS returns: YYYY-MM-DD
        Ensures: DATE MUST BE FUTURE DATE (today onward)
        """
        text = text.strip().lower()

        now = datetime.now()

        # -------------------------------
        # TODAY / TOMORROW
        # -------------------------------
        if "today" in text:
            return now.strftime("%Y-%m-%d")

        if "tomorrow" in text:
            return (now + timedelta(days=1)).strftime("%Y-%m-%d")

        # -------------------------------
        # WEEKDAY HANDLING
        # -------------------------------
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        for day, index in weekdays.items():
            if day in text:
                today_index = now.weekday()
                offset = index - today_index
                if offset <= 0:
                    offset += 7
                parsed_date = now + timedelta(days=offset)
                return parsed_date.strftime("%Y-%m-%d")

        # -------------------------------
        # GENERIC FORMATS
        # -------------------------------
        # Use verbose parser and return only valid future dates for compatibility
        parsed, reason = DateValidator.parse_date_verbose(text)
        if parsed and reason == "ok":
            return parsed
        return None

    @staticmethod
    def parse_date_verbose(text: str):
        """
        Parse text to a date string and return a tuple (date_str_or_None, reason).

        Reasons:
          - 'ok'   : parsed and is today or future
          - 'past' : parsed but date is in the past
          - 'none' : could not parse
        """
        text = text.strip().lower()

        now = datetime.now()

        # TODAY / TOMORROW
        if "today" in text:
            return now.strftime("%Y-%m-%d"), "ok"

        if "tomorrow" in text:
            return (now + timedelta(days=1)).strftime("%Y-%m-%d"), "ok"

        # WEEKDAY HANDLING
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        for day, index in weekdays.items():
            if day in text:
                today_index = now.weekday()
                offset = index - today_index
                if offset <= 0:
                    offset += 7
                parsed_date = now + timedelta(days=offset)
                return parsed_date.strftime("%Y-%m-%d"), "ok"

        # GENERIC FORMATS
        for day_first in [False, True]:
            try:
                parsed = date_parser.parse(text, fuzzy=True, dayfirst=day_first)

                # BLOCK PAST DATES
                if parsed.date() < now.date():
                    return parsed.strftime("%Y-%m-%d"), "past"

                return parsed.strftime("%Y-%m-%d"), "ok"

            except:
                pass

        return None, "none"

    @staticmethod
    def is_future(date_str: str):
        """
        Ensure date is today or future.
        """
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            return d.date() >= datetime.now().date()
        except:
            return False

    @staticmethod
    def is_checkout_valid(checkin: str, checkout: str):
        """
        checkout > checkin AND checkout must be future
        """
        try:
            ci = datetime.strptime(checkin, "%Y-%m-%d")
            co = datetime.strptime(checkout, "%Y-%m-%d")
            return co > ci and co.date() >= datetime.now().date()
        except:
            return False
