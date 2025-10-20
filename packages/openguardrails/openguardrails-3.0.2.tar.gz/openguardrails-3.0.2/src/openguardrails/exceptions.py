"""
Exception definition
"""


class OpenGuardrailsError(Exception):
    """OpenGuardrails base exception class"""
    pass


class AuthenticationError(OpenGuardrailsError):
    """Authentication error"""
    pass


class RateLimitError(OpenGuardrailsError):
    """Rate limit error"""
    pass


class ValidationError(OpenGuardrailsError):
    """Input validation error"""
    pass


class NetworkError(OpenGuardrailsError):
    """Network error"""
    pass


class ServerError(OpenGuardrailsError):
    """Server error"""
    pass