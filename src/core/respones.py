class Response:
    def __init__(self, success: bool, message: str, data=None):
        self.success = success
        self.message = message
        self.data = data

    def to_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }

    @classmethod
    def success(cls, message="Operation successful", data=None):
        return cls(success=True, message=message, data=data)

    @classmethod
    def failed(cls, message="Operation failed", data=None):
        return cls(success=False, message=message, data=data)

    @classmethod
    def bad_request(cls, message="Bad request", data=None):
        return cls(success=False, message=message, data=data)

