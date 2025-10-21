"""Parse commands for the CLI."""

import asyncio
import json

import typer
from loguru import logger

from ...exceptions import ValidationError, WorkloadError
from ...services import ParsingService, WorkloadService
from ...utils.validators import PathValidator

parse_commands = typer.Typer(help="Parse result files using workload-specific tools")


@parse_commands.command()
def parse(
    input_path: str = typer.Argument(..., help="Path to input file or directory"),
    workload: str = typer.Argument(..., help="Name of the workload"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Parse results using workload-specific extraction tools."""
    try:
        # Validate input path
        input_path_obj = PathValidator.validate_input_path(input_path)

        # Initialize services
        workload_service = WorkloadService()
        parsing_service = ParsingService(workload_service)

        # Initialize services
        workload_service.initialize()
        parsing_service.initialize()

        try:
            # Validate workload
            validated_workload = workload_service.validate_workload(workload)
            logger.info(f"✅ Using workload: {validated_workload}")

            # Get workload info for display
            workload_info = workload_service.get_workload_tool(validated_workload)
            if workload_info:
                expected_metrics = workload_info.get("metrics", [])
                logger.info(
                    f"📊 Expected metrics for {validated_workload}: {expected_metrics}"
                )
            else:
                logger.warning(f"⚠️  No workload info found for {validated_workload}")
                expected_metrics = []

            # Parse results
            logger.info(f"🔍 Parsing results from: {input_path_obj}")
            results = asyncio.run(
                parsing_service.parse_results(str(input_path_obj), validated_workload)
            )

            # Display results
            if results.iterations:
                logger.info(
                    f"✅ Successfully parsed {len(results.iterations)} iterations"
                )

                # Show extracted metrics
                extracted_metrics = parsing_service.get_extracted_metrics(results)
                logger.info(f"📈 Extracted metrics: {extracted_metrics}")

                # Validate completeness
                if expected_metrics:
                    is_complete = parsing_service.validate_extraction_completeness(
                        results, expected_metrics
                    )
                    if is_complete:
                        logger.info("✅ All expected metrics were extracted")
                    else:
                        logger.warning("⚠️  Some expected metrics were missing")

                # Save to output file if specified
                if output:
                    output_path = PathValidator.validate_output_path(output)
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(results.dict(), f, indent=2, ensure_ascii=False)
                    logger.info(f"💾 Results saved to: {output_path}")
                else:
                    # Print to stdout
                    print(json.dumps(results.dict(), indent=2, ensure_ascii=False))
            else:
                logger.warning("⚠️  No results were extracted")
                if not output:
                    print(json.dumps({"iterations": []}, indent=2))

        finally:
            # Cleanup services
            parsing_service.cleanup()
            workload_service.cleanup()

    except ValidationError as e:
        logger.error(f"❌ Validation error: {e}")
        raise typer.Exit(1) from e
    except WorkloadError as e:
        logger.error(f"❌ Workload error: {e}")
        if e.details:
            logger.info(f"Available workloads: {e.details.get('cached_workloads', [])}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e
