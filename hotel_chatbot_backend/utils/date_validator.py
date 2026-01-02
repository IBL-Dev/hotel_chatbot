import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser

class DateValidator:

    @staticmethod
    def parse_date_verbose(text: str):
        text = text.strip().lower()
        now = datetime.now()
        max_future = now + timedelta(days=30)

        if "today" in text:
            return now.strftime("%Y-%m-%d"), "ok"

        if "tomorrow" in text:
            tomorrow = now + timedelta(days=1)
            if tomorrow.date() > max_future.date():
                return tomorrow.strftime("%Y-%m-%d"), "too_far"
            return tomorrow.strftime("%Y-%m-%d"), "ok"

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
                parsed = now + timedelta(days=offset)

                if parsed.date() > max_future.date():
                    return parsed.strftime("%Y-%m-%d"), "too_far"

                return parsed.strftime("%Y-%m-%d"), "ok"

        for df in [False, True]:
            try:
                parsed = date_parser.parse(text, fuzzy=True, dayfirst=df)

                if parsed.date() < now.date():
                    return parsed.strftime("%Y-%m-%d"), "past"

                if parsed.date() > max_future.date():
                    return parsed.strftime("%Y-%m-%d"), "too_far"

                return parsed.strftime("%Y-%m-%d"), "ok"

            except:
                pass

        return None, "none"
