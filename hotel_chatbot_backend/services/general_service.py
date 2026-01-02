from promt.general_prompt import get_general_intent_prompt
from config.gemini_config import load_gemini
import re

llm = load_gemini()

class ServiceHandler:
    def handle(self, user_message: str) -> str:
        """
        Politely redirects non-hotel queries back to hotel-related topics
        """
        
        prompt = get_general_intent_prompt(user_message)
        
        try:
            response = llm.complete(prompt)
            response_text = response.text.strip()
            
            # Extract message and badge if formatted correctly
            message_match = re.search(r'Message:\s*(.+?)(?=Badge:|$)', response_text, re.DOTALL)
            badge_match = re.search(r'Badge:\s*(.+?)$', response_text, re.DOTALL)
            
            if message_match and badge_match:
                message = message_match.group(1).strip()
                badge = badge_match.group(1).strip()
                
                return f"{message}\n\n🎨 Suggested Icon: {badge}"
            else:
                # If format is not correct, return the raw response
                return response_text
                
        except Exception as e:
            print(f"Error in general service: {e}")
            return "I'm your Anjana Guest Hotel assistant! 🏨 I specialize in helping with bookings, rooms, amenities, and dining. How can I make your stay better? 😊✨"