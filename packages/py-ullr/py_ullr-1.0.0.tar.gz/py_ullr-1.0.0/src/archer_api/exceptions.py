"""Custom exceptions for Archer API client."""


class ArcherAPIException(Exception):
    """Base exception for Archer API errors."""
    pass


class AuthenticationError(ArcherAPIException):
    """Raised when authentication fails."""
    pass


class ResourceNotFoundError(ArcherAPIException):
    """Raised when a requested resource is not found."""
    pass


class ValidationError(ArcherAPIException):
    """Raised when input validation fails."""
    pass


class RateLimitError(ArcherAPIException):
    """Raised when API rate limit is exceeded."""
    pass


class PermissionError(ArcherAPIException):
    """Raised when user lacks permission for an operation."""
    pass