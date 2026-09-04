from .error_codes import ErrorCode


class NovaError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        source: str,
        status_code: int = 500,
        details: dict | None = None,
    ):
        super().__init__(message)

        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        self.source = "NovaEngine/" + source

    def to_dict(self):
        return {
            "code": self.code.value,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
            "source": self.source
        }
