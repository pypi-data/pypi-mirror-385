"""Workload service for managing workload operations."""

import subprocess
from typing import Any

from ..config.settings import ParserConfig
from ..exceptions import WorkloadError
from ..services.base import BaseService
from ..services.cache_service import CacheService
from ..services.registry_service import RegistryService


class WorkloadService(BaseService):
    """Service for managing workload operations."""

    def __init__(
        self,
        registry_service: RegistryService | None = None,
        cache_service: CacheService | None = None,
        config: ParserConfig | None = None,
    ) -> None:
        """Initialize the workload service.

        Args:
            registry_service: Registry service instance
            cache_service: Cache service instance
            config: Parser configuration
        """
        super().__init__(config)
        self.registry_service = registry_service or RegistryService(config)
        self.cache_service = cache_service or CacheService(config)
        self.script_downloader = self._create_script_downloader()

    def initialize(self) -> None:
        """Initialize the workload service."""
        self.registry_service.initialize()
        self.cache_service.initialize()

    def cleanup(self) -> None:
        """Cleanup workload service resources."""
        self.registry_service.cleanup()
        self.cache_service.cleanup()

    def _health_check(self) -> bool:
        """Check if workload service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return self.registry_service.is_healthy() and self.cache_service.is_healthy()

    def _create_script_downloader(self) -> Any:
        """Create script downloader instance.

        Returns:
            Script downloader instance
        """
        from ..utils.downloader import ScriptDownloader

        return ScriptDownloader()

    def get_workload_tool(self, workload_name: str) -> dict[str, Any] | None:
        """Get extraction tool for a specific workload (cache-first, then registry).

        Args:
            workload_name: Name of the workload

        Returns:
            Tool information dictionary or None if not found
        """
        try:
            # First try cache
            cached_tool = self.get_cached_workload_tool(workload_name)
            if cached_tool:
                return cached_tool

            # If not in cache, try to download from registry
            return self.download_workload_from_registry(workload_name)
        except Exception as e:
            self.logger.error(f"Failed to get workload tool for '{workload_name}': {e}")
            return None

    def get_cached_workload_tool(self, workload_name: str) -> dict[str, Any] | None:
        """Get workload tool info from cache only.

        Args:
            workload_name: Name of the workload

        Returns:
            Tool information dictionary or None if not cached
        """
        try:
            # Check if workload is cached
            if not self.cache_service.is_workload_cached(workload_name):
                return None

            # Get workload info from registry
            workload_info = self.registry_service.get_workload_by_name(workload_name)
            if workload_info:
                # Add script path and cache status
                script_name = workload_info.get("script", "extractor.sh")
                script_path = (
                    self.cache_service.cache_dir / workload_name.lower() / script_name
                )
                workload_info["script_path"] = str(script_path)
                workload_info["cached"] = True
                return workload_info

            # Fallback to basic info if not found in registry
            script_name = "extractor.sh"
            script_path = (
                self.cache_service.cache_dir / workload_name.lower() / script_name
            )
            return {
                "script": script_name,
                "description": f"Cached workload: {workload_name.lower()}",
                "metrics": [],  # Will be populated when script is executed
                "status": "active",
                "cached": True,
                "script_path": str(script_path),
            }
        except Exception as e:
            self.logger.error(
                f"Failed to get cached workload tool for '{workload_name}': {e}"
            )
            return None

    def download_workload_from_registry(
        self, workload_name: str
    ) -> dict[str, Any] | None:
        """Download workload script from registry and cache it.

        Args:
            workload_name: Name of the workload to download

        Returns:
            Tool information dictionary or None if failed
        """
        try:
            # Get workload info from registry
            workload_info = self.registry_service.get_workload_by_name(workload_name)
            if not workload_info:
                return None

            # Download the script
            script_name = workload_info.get("script", "extractor.sh")
            script_path = self.script_downloader.get_script(workload_name, script_name)

            # Return the tool info with updated path
            workload_info["script_path"] = str(script_path)
            workload_info["cached"] = True
            return workload_info

        except Exception as e:
            self.logger.error(
                f"Failed to download workload '{workload_name}' from registry: {e}"
            )
            return None

    def execute_extraction_tool(
        self, workload_name: str, input_path: str
    ) -> dict[str, Any]:
        """Execute an extraction tool for a specific workload.

        Args:
            workload_name: Name of the workload
            input_path: Path to input file or directory

        Returns:
            Execution result dictionary
        """
        try:
            # Get tool info
            tool_info = self.get_workload_tool(workload_name)
            if not tool_info:
                return {"error": f"No extraction tool for {workload_name}"}

            # Get script path and download if needed
            script_name = tool_info.get("script", "extractor.sh")
            try:
                script_path = self.script_downloader.get_script(
                    workload_name, script_name
                )
            except Exception as e:
                return {"error": f"Failed to get script: {e}"}

            if not script_path.exists():
                return {"error": f"Script not found: {script_path}"}

            # Execute the script
            self.logger.info(f"🔧 Using script: {script_path}")
            self.logger.info(f"🔧 Executing extraction script: {script_path}")

            result = subprocess.run(
                [str(script_path), input_path],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0 and result.stdout.strip():
                self.logger.info(f"✅ Data extraction successful for {workload_name}")
                return {
                    "success": True,
                    "raw_output": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                }
            else:
                error_msg = result.stderr.strip() or "Script execution failed"
                self.logger.warning(f"⚠️  Data extraction failed: {error_msg}")
                return {"error": error_msg}

        except subprocess.TimeoutExpired:
            error_msg = f"Script execution timed out for {workload_name}"
            self.logger.error(f"❌ {error_msg}")
            return {"error": error_msg}
        except Exception as e:
            self.logger.error(f"❌ Error executing data extraction script: {e}")
            return {"error": str(e)}

    def list_available_workloads(self) -> list[str]:
        """List all available workloads (cache-first, then registry).

        Returns:
            List of available workload names
        """
        try:
            # Return cached workloads first
            cached_workloads = self.cache_service.list_cached_workloads()

            # If no cached workloads, try to get from registry
            if not cached_workloads:
                registry_workloads = self.registry_service.list_workload_names()
                return registry_workloads

            return cached_workloads
        except Exception as e:
            self.logger.error(f"Failed to list workloads: {e}")
            return []

    def validate_workload(self, workload_name: str) -> str:
        """Validate workload with case-insensitive matching.

        Args:
            workload_name: Name of the workload to validate

        Returns:
            Validated workload name

        Raises:
            WorkloadError: If workload is invalid
        """
        # First check cached workloads
        cached_workloads = self.cache_service.list_cached_workloads()
        workload_lower = workload_name.lower()

        # Case-insensitive workload matching in cache
        for cached_workload in cached_workloads:
            if cached_workload.lower() == workload_lower:
                self.logger.debug(f"✅ Found workload '{workload_name}' in cache")
                return cached_workload

        # If not found in cache, check if workload exists in registry
        self.logger.debug(
            f"🔍 Workload '{workload_name}' not found in cache, checking registry..."
        )
        registry_workloads = self.registry_service.list_workload_names()

        for registry_workload in registry_workloads:
            if registry_workload.lower() == workload_lower:
                self.logger.debug(f"✅ Found workload '{workload_name}' in registry")
                return registry_workload

        # Workload not found
        raise WorkloadError(
            f"Invalid workload: {workload_name}",
            details={
                "cached_workloads": cached_workloads,
                "registry_workloads": registry_workloads,
            },
        )
