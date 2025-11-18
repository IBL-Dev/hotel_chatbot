from services.base_service import BaseService

class ServiceHandler(BaseService):
    def handle(self, message: str):
        return "Booking service handler responding..."
