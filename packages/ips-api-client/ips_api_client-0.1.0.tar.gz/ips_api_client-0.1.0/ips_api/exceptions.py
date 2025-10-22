"""Custom exceptions for IPS Controllers API."""


class IPSError(Exception):
    """Base exception for IPS API errors."""
    pass


class AuthenticationError(IPSError):
    """Raised when authentication fails."""
    pass


class SessionExpiredError(IPSError):
    """Raised when the session has expired."""
    pass


class ControllerNotFoundError(IPSError):
    """Raised when a controller is not found."""
    pass


class ParseError(IPSError):
    """Raised when HTML parsing fails."""
    pass
