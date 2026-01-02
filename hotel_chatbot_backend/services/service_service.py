from services.base_service import BaseService
from promt.service_response_prompt import get_service_response_prompt
from config.gemini_config import load_gemini
import re

llm = load_gemini()

class ServiceHandler(BaseService):
    def handle(self, message: str):

        prompt = get_service_response_prompt(message)
        response = llm.complete(prompt).text.strip()

        msg = re.search(r"Message:\s*(.+?)(?=Badge:)", response, re.DOTALL)
        badge = re.search(r"Badge:\s*(.+)$", response, re.DOTALL)

        message_out = msg.group(1).strip() if msg else response
        badge_out = badge.group(1).strip() if badge else "service-bell icon"

        return f"{message_out}\n\n🎨 Suggested Icon: {badge_out}"
