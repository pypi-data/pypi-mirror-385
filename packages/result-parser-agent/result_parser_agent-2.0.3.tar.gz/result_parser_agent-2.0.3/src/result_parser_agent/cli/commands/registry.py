"""Registry commands for the CLI."""

import json
from typing import Any

import typer
from loguru import logger

from ...exceptions import RegistryError, ValidationError
from ...services import RegistryService
from ...utils.validators import ConfigValidator

registry_commands = typer.Typer(name="registry", help="Manage workload registry")


@registry_commands.command("list")
def list_workloads(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """List all available workloads in the registry."""
    try:
        # Initialize registry service
        registry_service = RegistryService()
        registry_service.initialize()

        try:
            # Get all workloads
            workloads = registry_service.get_all_workloads()

            if not workloads:
                logger.info("📝 No workloads found in registry")
                return

            logger.info(f"📋 Found {len(workloads)} workloads in registry:")

            for workload in workloads:
                workload_name = workload.get("workloadName", "Unknown")
                description = workload.get("description", "No description")
                metrics = workload.get("metrics", [])
                status = workload.get("status", "unknown")

                logger.info(f"  • {workload_name}")
                logger.info(f"    Description: {description}")
                logger.info(f"    Metrics: {metrics}")
                logger.info(f"    Status: {status}")
                logger.info("")

        finally:
            registry_service.cleanup()

    except RegistryError as e:
        logger.error(f"❌ Registry error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e


@registry_commands.command("show")
def show_workload(
    workload_name: str = typer.Argument(..., help="Name of the workload to show"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Show detailed information about a specific workload."""
    try:
        # Initialize registry service
        registry_service = RegistryService()
        registry_service.initialize()

        try:
            # Get workload info
            workload = registry_service.get_workload_by_name(workload_name)

            if not workload:
                logger.error(f"❌ Workload '{workload_name}' not found in registry")
                raise typer.Exit(1)

            # Display workload info
            logger.info(f"📋 Workload: {workload.get('workloadName', 'Unknown')}")
            logger.info(
                f"  Description: {workload.get('description', 'No description')}"
            )
            logger.info(f"  Script: {workload.get('script', 'extractor.sh')}")
            logger.info(f"  Metrics: {workload.get('metrics', [])}")
            logger.info(f"  Status: {workload.get('status', 'unknown')}")

            if verbose:
                logger.info(f"  Full data: {json.dumps(workload, indent=2)}")

        finally:
            registry_service.cleanup()

    except RegistryError as e:
        logger.error(f"❌ Registry error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e


@registry_commands.command("add")
def add_workload(
    workload_name: str = typer.Argument(..., help="Name of the workload"),
    metrics: str = typer.Argument(..., help="Comma-separated list of metrics"),
    script: str = typer.Option("extractor.sh", "--script", "-s", help="Script name"),
    description: str = typer.Option(
        None, "--description", "-d", help="Workload description"
    ),
    status: str = typer.Option("active", "--status", help="Workload status"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Add a new workload to the registry."""
    try:
        # Parse metrics
        metrics_list = [m.strip() for m in metrics.split(",") if m.strip()]

        # Prepare workload data
        workload_data = {
            "workloadName": workload_name,
            "metrics": metrics_list,
            "script": script,
            "description": description or f"Performance benchmark for {workload_name}",
            "status": status,
        }

        # Validate workload data
        validated_data = ConfigValidator.validate_workload_config(workload_data)

        # Initialize registry service
        registry_service = RegistryService()
        registry_service.initialize()

        try:
            # Add workload
            result = registry_service.add_workload(validated_data)

            if result["success"]:
                logger.info(
                    f"✅ Successfully added workload '{workload_name}' to registry"
                )
                if verbose:
                    logger.info(
                        f"Workload data: {json.dumps(result['data'], indent=2)}"
                    )
            else:
                logger.error(f"❌ Failed to add workload: {result['error']}")
                raise typer.Exit(1)

        finally:
            registry_service.cleanup()

    except ValidationError as e:
        logger.error(f"❌ Validation error: {e}")
        raise typer.Exit(1) from e
    except RegistryError as e:
        logger.error(f"❌ Registry error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e


@registry_commands.command("update")
def update_workload(
    workload_name: str = typer.Argument(..., help="Name of the workload to update"),
    metrics: str = typer.Option(
        None, "--metrics", "-m", help="Comma-separated list of metrics"
    ),
    script: str = typer.Option(None, "--script", "-s", help="Script name"),
    description: str = typer.Option(
        None, "--description", "-d", help="Workload description"
    ),
    status: str = typer.Option(None, "--status", help="Workload status"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Update an existing workload in the registry."""
    try:
        # Prepare updates
        updates: dict[str, Any] = {}

        if metrics:
            metrics_list = [m.strip() for m in metrics.split(",") if m.strip()]
            updates["metrics"] = metrics_list

        if script:
            updates["script"] = script

        if description:
            updates["description"] = description

        if status:
            updates["status"] = status

        if not updates:
            logger.error("❌ No updates specified")
            raise typer.Exit(1)

        # Initialize registry service
        registry_service = RegistryService()
        registry_service.initialize()

        try:
            # Update workload
            result = registry_service.update_workload(workload_name, updates)

            if result["success"]:
                logger.info(
                    f"✅ Successfully updated workload '{workload_name}' in registry"
                )
                if verbose:
                    logger.info(
                        f"Updates applied: {json.dumps(result['updates'], indent=2)}"
                    )
            else:
                logger.error(f"❌ Failed to update workload: {result['error']}")
                raise typer.Exit(1)

        finally:
            registry_service.cleanup()

    except RegistryError as e:
        logger.error(f"❌ Registry error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e


@registry_commands.command("download")
def download_workload(
    workload_name: str = typer.Argument(..., help="Name of the workload to download"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Download workload script from registry to cache."""
    try:
        # Initialize registry service
        registry_service = RegistryService()
        registry_service.initialize()

        try:
            # Check if workload exists in registry
            workload = registry_service.get_workload_by_name(workload_name)
            if not workload:
                logger.error(f"❌ Workload '{workload_name}' not found in registry")
                raise typer.Exit(1)

            # Download the workload script
            from ...services.workload_service import WorkloadService

            workload_service = WorkloadService(registry_service=registry_service)
            workload_service.initialize()

            try:
                tool_info = workload_service.download_workload_from_registry(
                    workload_name
                )

                if tool_info:
                    logger.info(
                        f"✅ Successfully downloaded workload '{workload_name}'"
                    )
                    logger.info(
                        f"  • Script: {tool_info.get('script', 'extractor.sh')}"
                    )
                    logger.info(f"  • Metrics: {tool_info.get('metrics', [])}")
                    logger.info(
                        f"  • Script path: {tool_info.get('script_path', 'Unknown')}"
                    )
                else:
                    logger.error(f"❌ Failed to download workload '{workload_name}'")
                    raise typer.Exit(1)
            finally:
                workload_service.cleanup()

        finally:
            registry_service.cleanup()

    except RegistryError as e:
        logger.error(f"❌ Registry error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e
