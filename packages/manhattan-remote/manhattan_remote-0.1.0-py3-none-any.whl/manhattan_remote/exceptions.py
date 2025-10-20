"""Exceptions for Manhattan Remote library."""


class ManhattanError(Exception):
    """Base exception for Manhattan Remote."""
    pass


class ManhattanConnectionError(ManhattanError):
    """Raised when connection to TV box fails."""
    pass


class ManhattanTimeoutError(ManhattanError):
    """Raised when request times out."""
    pass