from services.base_service import BaseService

class ServiceHandler(BaseService):
    def handle(self, message: str):
        return "General hotel service handler responding..."
