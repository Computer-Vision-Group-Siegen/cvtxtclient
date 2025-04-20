class APIError(Exception):
    """Base class for all API errors."""
    def __init__(self, message: str, status_code: int = None, response_data: any = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)

class BadRequestError(APIError):
    """400 Bad Request."""

class NotFoundError(APIError):
    """404 Not Found."""

class PreconditionFailedError(APIError):
    """412 Precondition Failed."""

class InternalServerError(APIError):
    """500 Internal Server Error."""

class UnexpectedError(APIError):
    """Unexpected API Error."""