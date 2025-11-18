class ServiceHandler:
    def handle(self, user_message: str) -> str:

        text = user_message.lower()

        if "restaurant" in text or "food" in text or "menu" in text:
            return "Our restaurant is open 7 AM – 10 PM. Would you like breakfast, lunch, dinner, or today's menu? 🍽️"

        if "wifi" in text:
            return "Our WiFi is free for guests. Would you like the password? 📶"

        if "clean" in text or "housekeeping" in text:
            return "Housekeeping is available 7 AM – 7 PM. Shall I arrange cleaning for your room? 🧹"

        if "laundry" in text:
            return "Laundry service is available until 5 PM. Should we pick up your clothes? 👕"

        if "taxi" in text or "pickup" in text:
            return "We offer taxi and airport pickup services. Where would you like to go? 🚗"

        if "parking" in text:
            return "Yes, we provide free secure parking. Would you like a reserved spot? 🅿️"

        return "Sure! I can help with guest services like food, WiFi, laundry, parking, and more. What do you need? 😊"
