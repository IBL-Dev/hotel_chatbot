class ServiceHandler:
    def handle(self, user_message: str) -> str:

        text = user_message.lower()

        if "price" in text or "rate" in text:
            return "Our room rates vary by type and season. Would you prefer Single, Double, or Family rooms?"

        if "availability" in text or "available" in text:
            return "Sure! Please tell me your check-in date, and I’ll check room availability for you. 🛏️"

        if "cancel" in text:
            return "To cancel a booking, please share your booking reference number."

        if "extend" in text:
            return "Absolutely! How long would you like to extend your stay?"

        return "I can help with your room booking! May I know your check-in date and number of guests?"
