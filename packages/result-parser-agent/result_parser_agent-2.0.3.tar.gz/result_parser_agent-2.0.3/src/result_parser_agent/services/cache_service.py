"""Cache service for managing script and registry cache."""

import shutil
from pathlib import Path
from typing import Any

from ..config.settings import ParserConfig
from ..exceptions import CacheError
from ..services.base import BaseService


class CacheService(BaseService):
    """Service for managing cache operations."""

    def __init__(self, config: ParserConfig | None = None) -> None:
        """Initialize the cache service.

        Args:
            config: Parser configuration
        """
        super().__init__(config)
        self.cache_dir = Path(self.config.SCRIPTS_CACHE_DIR).expanduser()
        self.registry_file = self.cache_dir / "registry.json"

    def initialize(self) -> None:
        """Initialize the cache service."""
        self._ensure_cache_directory()

    def cleanup(self) -> None:
        """Cleanup cache service resources."""
        pass

    def _health_check(self) -> bool:
        """Check if cache service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return self.cache_dir.exists()

    def _ensure_cache_directory(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_info(self) -> dict[str, Any]:
        """Get information about cached scripts.

        Returns:
            Dictionary with cache statistics
        """
        try:
            if not self.cache_dir.exists():
                return {"total_scripts": 0, "cache_size": 0, "workloads": []}

            workloads = []
            total_size = 0
            seen_workloads = set()  # Track normalized names to avoid duplicates

            for workload_dir in self.cache_dir.iterdir():
                if workload_dir.is_dir() and workload_dir.name != "__pycache__":
                    workload_name = workload_dir.name
                    normalized_name = workload_name.lower()

                    # Skip if we've already processed this normalized name
                    if normalized_name in seen_workloads:
                        continue

                    seen_workloads.add(normalized_name)

                    script_count = len(list(workload_dir.glob("*.sh")))
                    workload_size = sum(
                        f.stat().st_size for f in workload_dir.rglob("*") if f.is_file()
                    )

                    workloads.append(
                        {
                            "name": normalized_name,
                            "script_count": script_count,
                            "size_bytes": workload_size,
                        }
                    )
                    total_size += workload_size

            return {
                "total_scripts": sum(w["script_count"] for w in workloads),
                "cache_size": total_size,
                "workloads": workloads,
            }
        except Exception as e:
            self.logger.error(f"Failed to get cache info: {e}")
            return {"total_scripts": 0, "cache_size": 0, "workloads": []}

    def list_cached_workloads(self) -> list[str]:
        """List workloads available in local cache.

        Returns:
            List of cached workload names (normalized to lowercase)
        """
        try:
            if not self.cache_dir.exists():
                return []

            cached_workloads = []
            for workload_dir in self.cache_dir.iterdir():
                if workload_dir.is_dir() and workload_dir.name != "__pycache__":
                    # Check if it has scripts
                    if list(workload_dir.glob("*.sh")):
                        cached_workloads.append(workload_dir.name.lower())

            self.logger.debug(f"Found {len(cached_workloads)} cached workloads")
            return cached_workloads
        except Exception as e:
            self.logger.error(f"Failed to list cached workloads: {e}")
            return []

    def clear_script_cache(self, workload: str | None = None) -> None:
        """Clear script cache.

        Args:
            workload: Specific workload to clear, or None for all

        Raises:
            CacheError: If cache cannot be cleared
        """
        try:
            if workload:
                workload_dir = self.cache_dir / workload.lower()
                if workload_dir.exists():
                    shutil.rmtree(workload_dir)
                    self.logger.info(f"Cleared cache for {workload}")
                else:
                    self.logger.warning(f"No cache found for workload: {workload}")
            else:
                # Clear all cache except registry.json
                for item in self.cache_dir.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    elif item.name != "registry.json":
                        item.unlink()

                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info("Cleared all script cache")
        except Exception as e:
            raise CacheError(f"Failed to clear cache: {e}") from e

    def clear_registry_cache(self) -> None:
        """Clear registry cache.

        Raises:
            CacheError: If registry cache cannot be cleared
        """
        try:
            if self.registry_file.exists():
                self.registry_file.unlink()
                self.logger.info("Cleared registry cache")
            else:
                self.logger.warning("No registry cache found")
        except Exception as e:
            raise CacheError(f"Failed to clear registry cache: {e}") from e

    def clear_all_cache(self) -> None:
        """Clear all cache (scripts and registry).

        Raises:
            CacheError: If cache cannot be cleared
        """
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info("Cleared all cache")
            else:
                self.logger.warning("No cache directory found")
        except Exception as e:
            raise CacheError(f"Failed to clear all cache: {e}") from e

    def get_cache_size(self) -> int:
        """Get total cache size in bytes.

        Returns:
            Cache size in bytes
        """
        try:
            if not self.cache_dir.exists():
                return 0

            total_size = 0
            for file_path in self.cache_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size

            return total_size
        except Exception as e:
            self.logger.error(f"Failed to get cache size: {e}")
            return 0

    def is_workload_cached(self, workload_name: str) -> bool:
        """Check if a workload is cached.

        Args:
            workload_name: Name of the workload to check

        Returns:
            True if cached, False otherwise
        """
        try:
            workload_dir = self.cache_dir / workload_name.lower()
            if not workload_dir.exists():
                return False

            # Check if it has scripts
            return bool(list(workload_dir.glob("*.sh")))
        except Exception as e:
            self.logger.error(
                f"Failed to check if workload '{workload_name}' is cached: {e}"
            )
            return False
