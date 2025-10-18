import asyncio
import logging
import logging.config
import os
import sys
from pathlib import Path

import click
from fluidattacks_core.logging import PRODUCT_LOGGING

from sifts.analysis.orchestrator import scan_projects
from sifts.config import SiftsConfig

os.environ["AWS_REGION_NAME"] = os.environ.get("AWS_REGION_NAME", "us-east-1")


LOGGING_CONFIG = {
    **PRODUCT_LOGGING,
}


logging.config.dictConfig(LOGGING_CONFIG)

LOGGER = logging.getLogger(__name__)


@click.group()
def main_cli() -> None:
    pass


@main_cli.command()
@click.argument("analysis-dir")
@click.option("--group-name", required=True)
@click.option("--root-nickname", required=True)
def scan(analysis_dir: str, group_name: str, root_nickname: str) -> None:
    """Scan code in the specified directory."""
    try:
        asyncio.run(
            scan_projects(
                SiftsConfig.create_with_overrides(
                    root_dir=Path(analysis_dir).resolve(),
                    group_name=group_name,
                    root_nickname=root_nickname,
                ),
            ),
        )
    except Exception:
        LOGGER.exception("Error during scan")
        sys.exit(1)


@main_cli.command()
@click.argument(
    "config-file",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
)
def run_with_config(config_file: str) -> None:
    """Run analysis using a YAML configuration file."""
    try:
        config = SiftsConfig.from_yaml(config_file)
        LOGGER.info("Running with configuration from %s", config_file)

        # Configure runtime settings
        if config.parallel:
            LOGGER.info("Running with %d threads in parallel mode", config.threads)
            # You would implement parallel processing logic here

        # Create output directory if it doesn't exist
        if config.output_path:
            output_path = Path(config.output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        asyncio.run(scan_projects(config))

    except Exception:
        LOGGER.exception("Error running with config file %s", config_file)
        sys.exit(1)
