"""
Exception classes for OMAM AuthKit SDK
"""


class AuthKitError(Exception):
    """Base exception for all AuthKit errors"""
    pass


class AuthenticationError(AuthKitError):
    """Raised when authentication fails"""
    pass


class TokenExpiredError(AuthKitError):
    """Raised when a token has expired"""
    pass


class InvalidTokenError(AuthKitError):
    """Raised when a token is invalid"""
    pass


class APIError(AuthKitError):
    """Raised when an API request fails"""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
