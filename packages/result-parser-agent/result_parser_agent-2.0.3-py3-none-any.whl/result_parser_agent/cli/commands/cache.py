"""Cache commands for the CLI."""

import typer
from loguru import logger

from ...exceptions import CacheError
from ...services import CacheService

cache_commands = typer.Typer(name="cache", help="Manage script and registry cache")


@cache_commands.command("info")
def cache_info(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Show cache information and statistics."""
    try:
        # Initialize cache service
        cache_service = CacheService()
        cache_service.initialize()

        try:
            # Get cache info
            info = cache_service.get_cache_info()

            logger.info("📊 Cache Information:")
            logger.info(f"  • Total scripts: {info['total_scripts']}")
            logger.info(f"  • Cache size: {info['cache_size']:,} bytes")
            logger.info(f"  • Cached workloads: {len(info['workloads'])}")

            if info["workloads"]:
                logger.info("  • Workload details:")
                for workload in info["workloads"]:
                    logger.info(
                        f"    - {workload['name']}: {workload['script_count']} scripts, {workload['size_bytes']:,} bytes"
                    )

            if verbose:
                logger.info(f"  • Full cache info: {info}")

        finally:
            cache_service.cleanup()

    except CacheError as e:
        logger.error(f"❌ Cache error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e


@cache_commands.command("list")
def list_cached_workloads(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """List all cached workloads."""
    try:
        # Initialize cache service
        cache_service = CacheService()
        cache_service.initialize()

        try:
            # Get cached workloads
            workloads = cache_service.list_cached_workloads()

            if not workloads:
                logger.info("📝 No workloads found in cache")
                return

            logger.info(f"📋 Cached workloads ({len(workloads)}):")
            for workload in sorted(workloads):
                logger.info(f"  • {workload}")

        finally:
            cache_service.cleanup()

    except CacheError as e:
        logger.error(f"❌ Cache error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e


@cache_commands.command("clear")
def clear_cache(
    workload: str = typer.Option(
        None, "--workload", "-w", help="Specific workload to clear"
    ),
    scripts: bool = typer.Option(
        True, "--scripts/--no-scripts", help="Clear script cache"
    ),
    registry: bool = typer.Option(
        False, "--registry/--no-registry", help="Clear registry cache"
    ),
    all: bool = typer.Option(
        False, "--all", help="Clear all cache (scripts and registry)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Clear cache (scripts and/or registry)."""
    try:
        # Initialize cache service
        cache_service = CacheService()
        cache_service.initialize()

        try:
            if all:
                # Clear all cache
                cache_service.clear_all_cache()
                logger.info("✅ Cleared all cache (scripts and registry)")
            else:
                # Clear specific cache types
                if scripts:
                    cache_service.clear_script_cache(workload)
                    if workload:
                        logger.info(f"✅ Cleared script cache for workload: {workload}")
                    else:
                        logger.info("✅ Cleared all script cache")

                if registry:
                    cache_service.clear_registry_cache()
                    logger.info("✅ Cleared registry cache")

                if not scripts and not registry:
                    logger.warning(
                        "⚠️  No cache type specified. Use --scripts, --registry, or --all"
                    )

        finally:
            cache_service.cleanup()

    except CacheError as e:
        logger.error(f"❌ Cache error: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e
