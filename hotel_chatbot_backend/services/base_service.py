class BaseService:
    def handle(self, message: str) -> str:
        raise NotImplementedError("Service classes must implement handle() method")
