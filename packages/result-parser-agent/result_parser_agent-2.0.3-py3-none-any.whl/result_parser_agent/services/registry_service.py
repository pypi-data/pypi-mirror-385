"""Registry service for managing workload registry."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..config.settings import ParserConfig
from ..exceptions import RegistryError
from ..services.base import BaseService


class RegistryService(BaseService):
    """Service for managing workload registry."""

    def __init__(self, config: ParserConfig | None = None) -> None:
        """Initialize the registry service.

        Args:
            config: Parser configuration
        """
        super().__init__(config)
        self.registry_file = (
            Path(self.config.SCRIPTS_CACHE_DIR).expanduser() / "registry.json"
        )
        self.remote_registry_url = "https://raw.githubusercontent.com/AMD-DEAE-CEME/epdw2.0_parser_scripts/main/registry.json"
        self.git_url = self._get_git_url()
        self._ensure_directories()

    def initialize(self) -> None:
        """Initialize the registry service."""
        self._ensure_registry_available()

    def cleanup(self) -> None:
        """Cleanup registry service resources."""
        pass

    def _health_check(self) -> bool:
        """Check if registry service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return self.registry_file.exists()

    def _get_git_url(self) -> str:
        """Get Git URL from configuration.

        Returns:
            Git URL for the scripts repository
        """
        base_url = self.config.SCRIPTS_BASE_URL

        # Convert HTTPS raw URL to SSH git URL if needed
        if base_url.startswith("https://raw.githubusercontent.com/"):
            parts = base_url.replace("https://raw.githubusercontent.com/", "").split(
                "/"
            )
            if len(parts) >= 2:
                owner_repo = parts[0] + "/" + parts[1]
                return f"git@github.com:{owner_repo}.git"
            else:
                raise RegistryError(f"Invalid raw GitHub URL format: {base_url}")

        return base_url

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_registry(self) -> dict[str, Any]:
        """Load registry data from local file.

        Returns:
            Registry data dictionary

        Raises:
            RegistryError: If registry cannot be loaded
        """
        try:
            if not self.registry_file.exists():
                self.logger.warning(f"Registry file not found at {self.registry_file}")
                return {"version": "1.0.0", "workloads": []}

            with open(self.registry_file, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                self.logger.debug(
                    f"Loaded registry with {len(data.get('workloads', []))} workloads"
                )
                return data
        except Exception as e:
            raise RegistryError(f"Failed to load registry: {e}") from e

    def _save_registry(self, data: dict[str, Any]) -> None:
        """Save registry data to local file.

        Args:
            data: Registry data to save

        Raises:
            RegistryError: If registry cannot be saved
        """
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Saved registry to {self.registry_file}")
        except Exception as e:
            raise RegistryError(f"Failed to save registry: {e}") from e

    def _download_registry(self) -> bool:
        """Download the registry.json file from the Git repository.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Downloading registry.json from Git repository...")

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Clone the repository
                subprocess.run(
                    ["git", "clone", "--depth", "1", self.git_url, "repo"],
                    cwd=temp_path,
                    capture_output=True,
                    check=True,
                )

                repo_path = temp_path / "repo"
                registry_file_path = repo_path / "registry.json"

                if not registry_file_path.exists():
                    self.logger.error("registry.json not found in repository")
                    return False

                # Read and save the registry file
                with open(registry_file_path, encoding="utf-8") as f:
                    data = json.load(f)

                self._save_registry(data)
                self.logger.info(
                    f"Successfully downloaded registry with {len(data.get('workloads', []))} workloads"
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to download registry: {e}")
            return False

    def _ensure_registry_available(self) -> bool:
        """Ensure registry is available, download if necessary.

        Returns:
            True if registry is available, False otherwise
        """
        if self.registry_file.exists():
            return True

        self.logger.info("Registry not found, attempting to download...")
        return self._download_registry()

    def get_all_workloads(self) -> list[dict[str, Any]]:
        """Get all workloads from the registry.

        Returns:
            List of workload dictionaries
        """
        try:
            if not self._ensure_registry_available():
                raise RegistryError("Failed to ensure registry is available")

            data = self._load_registry()
            workloads: list[dict[str, Any]] = data.get("workloads", [])
            self.logger.debug(f"Retrieved {len(workloads)} workloads from registry")
            return workloads
        except Exception as e:
            self.logger.error(f"Failed to get workloads: {e}")
            return []

    def get_workload_by_name(self, workload_name: str) -> dict[str, Any] | None:
        """Get a specific workload by name (case-insensitive).

        Args:
            workload_name: Name of the workload to find

        Returns:
            Workload dictionary if found, None otherwise
        """
        try:
            workloads = self.get_all_workloads()
            for workload in workloads:
                if workload.get("workloadName", "").lower() == workload_name.lower():
                    return workload
            return None
        except Exception as e:
            self.logger.error(f"Failed to get workload '{workload_name}': {e}")
            return None

    def list_workload_names(self) -> list[str]:
        """Get list of workload names from the registry.

        Returns:
            List of workload names
        """
        try:
            workloads = self.get_all_workloads()
            names = [
                w.get("workloadName", "") for w in workloads if w.get("workloadName")
            ]
            self.logger.debug(f"Retrieved {len(names)} workload names from registry")
            return names
        except Exception as e:
            self.logger.error(f"Failed to list workload names: {e}")
            return []

    def add_workload(self, workload_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new workload to the registry.

        Args:
            workload_data: Workload data to add

        Returns:
            Result dictionary with success status

        Raises:
            RegistryError: If workload cannot be added
        """
        try:
            workload_name = workload_data.get("workloadName")
            if not workload_name:
                raise RegistryError("workloadName is required")

            # Ensure registry is available
            if not self._ensure_registry_available():
                raise RegistryError("Failed to ensure registry is available")

            # Load current registry
            data = self._load_registry()
            workloads = data.get("workloads", [])

            # Check if workload already exists
            for existing in workloads:
                if existing.get("workloadName", "").lower() == workload_name.lower():
                    raise RegistryError(f"Workload '{workload_name}' already exists")

            # Add new workload
            workloads.append(workload_data)
            data["workloads"] = workloads
            self._save_registry(data)

            self.logger.info(
                f"Successfully added workload '{workload_name}' to registry"
            )
            return {
                "success": True,
                "message": f"Workload '{workload_name}' successfully added to registry",
                "workload": workload_name,
                "data": workload_data,
            }
        except Exception as e:
            error_msg = f"Failed to add workload '{workload_name}': {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def update_workload(
        self, workload_name: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing workload in the registry.

        Args:
            workload_name: Name of the workload to update
            updates: Updates to apply

        Returns:
            Result dictionary with success status

        Raises:
            RegistryError: If workload cannot be updated
        """
        try:
            # Ensure registry is available
            if not self._ensure_registry_available():
                raise RegistryError("Failed to ensure registry is available")

            # Get current workload data
            current_workload = self.get_workload_by_name(workload_name)
            if not current_workload:
                raise RegistryError(f"Workload '{workload_name}' not found")

            # Prepare update data by merging current workload with updates
            update_data = current_workload.copy()
            update_data.update(updates)

            # Update workload in registry
            data = self._load_registry()
            workloads = data.get("workloads", [])

            # Find and update workload
            updated = False
            for i, workload in enumerate(workloads):
                if workload.get("workloadName", "").lower() == workload_name.lower():
                    workloads[i] = update_data
                    updated = True
                    break

            if not updated:
                raise RegistryError(f"Workload '{workload_name}' not found for update")

            data["workloads"] = workloads
            self._save_registry(data)

            self.logger.info(
                f"Successfully updated workload '{workload_name}' in registry"
            )
            return {
                "success": True,
                "message": f"Workload '{workload_name}' successfully updated in registry",
                "workload": workload_name,
                "updates": updates,
                "data": update_data,
            }
        except Exception as e:
            error_msg = f"Failed to update workload '{workload_name}': {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
