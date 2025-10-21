"""Custom exceptions for the result parser agent."""

from typing import Any


class ParserError(Exception):
    """Base exception for all parser-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RegistryError(ParserError):
    """Registry-related errors."""

    pass


class CacheError(ParserError):
    """Cache-related errors."""

    pass


class WorkloadError(ParserError):
    """Workload-related errors."""

    pass


class ValidationError(ParserError):
    """Validation-related errors."""

    pass


class DownloadError(ParserError):
    """Download-related errors."""

    pass


class ExecutionError(ParserError):
    """Script execution errors."""

    pass
