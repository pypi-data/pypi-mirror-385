"""Archil SDK exceptions."""


class ArchilError(Exception):
    """Base exception for Archil SDK."""
    pass


class AuthenticationError(ArchilError):
    """Authentication failed."""
    pass


class ContainerError(ArchilError):
    """Container operation failed."""
    pass


class NotFoundError(ArchilError):
    """Resource not found."""
    pass


class APIError(ArchilError):
    """API request failed."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
