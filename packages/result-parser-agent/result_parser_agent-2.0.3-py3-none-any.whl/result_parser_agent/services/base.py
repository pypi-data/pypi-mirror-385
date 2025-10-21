"""Base service class for all services."""

from abc import ABC, abstractmethod

from loguru import logger

from ..config.settings import ParserConfig


class BaseService(ABC):
    """Base class for all services."""

    def __init__(self, config: ParserConfig | None = None) -> None:
        """Initialize the service.

        Args:
            config: Optional configuration object
        """
        self.config = config or ParserConfig()
        self.logger = logger.bind(service=self.__class__.__name__)

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources."""
        pass

    def is_healthy(self) -> bool:
        """Check if the service is healthy.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            return self._health_check()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    @abstractmethod
    def _health_check(self) -> bool:
        """Internal health check implementation.

        Returns:
            True if healthy, False otherwise
        """
        pass
