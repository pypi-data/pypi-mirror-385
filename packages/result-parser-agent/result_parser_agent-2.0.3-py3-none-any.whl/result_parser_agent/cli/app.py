"""Main CLI application."""

import typer
from loguru import logger

from .commands import (
    cache_commands,
    parse_commands,
    registry_commands,
)

# Create main app
app = typer.Typer(
    name="result-parser",
    help="A CLI tool for extracting metrics from raw result files using workload-specific tools",
    no_args_is_help=True,
    add_completion=False,
)

# Add parse as direct command
app.add_typer(parse_commands)

# Add other command groups
app.add_typer(registry_commands, name="registry")
app.add_typer(cache_commands, name="cache")


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Result Parser Agent - Extract metrics from raw result files."""
    if verbose:
        logger.remove()
        logger.add(
            lambda msg: typer.echo(msg, err=True),
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )
    else:
        logger.remove()
        logger.add(
            lambda msg: typer.echo(msg, err=True),
            level="INFO",
            format="<level>{level: <8}</level> | <level>{message}</level>",
        )


@app.command()
def version() -> None:
    """Show version and exit."""
    from .. import __version__

    typer.echo(f"result-parser-agent version {__version__}")


if __name__ == "__main__":
    app()
