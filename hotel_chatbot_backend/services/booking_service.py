class ServiceHandler:
    def handle(self, user_message: str) -> str:

        text = user_message.lower()

        if "price" in text or "rate" in text:
            return "Our room rates vary by type and season. Would you prefer Single, Double, or Family rooms? 🏨"

        if "availability" in text or "available" in text:
            return "Sure! Please tell me your check-in date, and I’ll check room availability for you. 🛏️"

        if "cancel" in text:
            return "No problem! Please share your booking reference number so I can cancel it for you. ❌"

        if "extend" in text:
            return "Of course! How many extra nights would you like to stay? 😊"

        return "I'd be happy to help with your booking! May I know your check-in date and number of guests? ✨"
