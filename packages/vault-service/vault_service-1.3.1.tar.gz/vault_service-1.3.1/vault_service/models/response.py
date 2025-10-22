class Response:
    def __init__(self, status: str, message: str, data=None):
        self.status = status
        self.message = message
        self.data = data

    def dict(self):
        return {"status": self.status, "message": self.message, "data": self.data}