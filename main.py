"""
main.py — Entry point. Thin. No logic lives here.
All logic lives in src/. This file only wires things together.
"""
import typer
from src.shared.logger import logger, setup_logger
from src.shared.config import config

app = typer.Typer(help=config.project.description or config.project.name)


@app.command()
def run(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
) -> None:
    """Main entry point."""
    if verbose:
        setup_logger(log_level="DEBUG")

    logger.info(f"Starting {config.project.name} v{config.project.version}")
    logger.info(f"Domain: {config.project.domain}")

    # TODO (Phase 5): wire in your main pipeline here
    # e.g. from src.pipeline import run_pipeline; run_pipeline(config)

    logger.info("Done.")


if __name__ == "__main__":
    app()
