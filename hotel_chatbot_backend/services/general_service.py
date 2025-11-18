from services.base_service import BaseService

class ServiceHandler(BaseService):
    def handle(self, message: str):
        return "How can I assist you today?"
