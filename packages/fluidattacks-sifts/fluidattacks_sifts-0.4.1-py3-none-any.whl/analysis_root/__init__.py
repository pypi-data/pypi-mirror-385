import argparse
import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

import aiofiles
import aiohttp
import yaml
from platformdirs import user_data_dir

import sifts
from sifts.analysis.orchestrator import scan_projects
from sifts.config import SiftsConfig
from sifts.core.sarif_result import get_sarif
from sifts.io.api import GraphQLApiError, fetch_group_roots, initialize_session

HTTP_OK = 200


# Detect if running in AWS Batch
def _get_base_dir() -> Path:
    """
    Get the base directory for sifts data.

    In AWS Batch, use a temporary directory to avoid issues with user_data_dir.
    Otherwise, use the standard user data directory.
    """
    if os.getenv("AWS_BATCH_JOB_ID"):
        # Running in AWS Batch, use a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="sifts_")
        return Path(temp_dir)

    # Running locally, use user data directory
    return Path(user_data_dir(appname="sifts", appauthor="fluidattacks", ensure_exists=True))


_BASE_DIR = _get_base_dir()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

LOGGER = logging.getLogger(__name__)


async def download_taxonomy() -> dict[str, Any]:
    """Download and parse the taxonomy.yaml file from GitHub."""
    url = "https://raw.githubusercontent.com/fluidattacks/universe/refs/heads/trunk/sifts/taxonomy/taxonomy.yaml"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == HTTP_OK:
                    content = await response.text()
                    taxonomy_data = yaml.safe_load(content)
                    LOGGER.info("Successfully downloaded taxonomy.yaml")
                    return taxonomy_data or {}
                LOGGER.error("Failed to download taxonomy.yaml: HTTP %s", response.status)
                return {}
        except Exception:
            LOGGER.exception("Error downloading taxonomy.yaml")
            return {}


async def run_cli(
    group_name: str,
    nickname: str,
    output_path: Path,
) -> None:
    integrates_session, _ = initialize_session()
    LOGGER.info("Fetching group roots for %s %s", group_name, nickname)
    try:
        data = await fetch_group_roots(integrates_session, group_name)
    except GraphQLApiError:
        LOGGER.exception("Failed to fetch group roots")
        return
    finally:
        await integrates_session.close()
    root_id = next(
        (
            x["id"]
            for x in data["data"]["group"]["roots"]
            if (x["nickname"]).lower() == nickname.lower()
        ),
        None,
    )

    if not root_id:
        LOGGER.error("Root ID not found")
        return

    Path(_BASE_DIR, "groups").mkdir(parents=True, exist_ok=True)
    process = await asyncio.create_subprocess_exec(
        "melts",
        "pull-repos",
        "--group",
        group_name,
        "--root",
        nickname,
        cwd=_BASE_DIR,
    )
    await process.wait()
    if process.returncode != 0:
        LOGGER.error("Failed to pull repos")
        return
    working_dir = Path(_BASE_DIR, "groups", group_name, nickname)
    if not working_dir.exists() or not any(working_dir.iterdir()):
        LOGGER.warning("Working directory not found")
        return

    # Download taxonomy and extract vulnerability IDs
    taxonomy_data = await download_taxonomy()
    valid_vulnerabilities: list[str] = [
        val["id"] for x in taxonomy_data["Unexpected Injection"].values() for val in x
    ]

    config = SiftsConfig.create_with_overrides(
        root_nickname=nickname,
        group_name=group_name,
        root_dir=working_dir,
        split_subdirectories=False,
        enable_navigation=True,
        include_vulnerabilities=valid_vulnerabilities,
        model="gpt-4.1-mini",
        database_backend="dynamodb",
    )
    LOGGER.info("Scanning projects for %s %s", group_name, nickname)
    LOGGER.info("Using database backend: %s", config.database_backend)
    if config.database_backend == "sqlite":
        LOGGER.info("SQLite database path: %s", config.sqlite_database_path)

    await scan_projects(config)
    db_backend = config.get_database()
    analyses = await db_backend.get_analyses_by_root(group_name, nickname, sifts.__version__)
    sarif = await get_sarif(analyses, config)
    async with aiofiles.open(output_path, "w") as f:
        await f.write(json.dumps(sarif, indent=2))


async def main() -> None:
    parser = argparse.ArgumentParser(description="CLI for sifts analysis.")
    parser.add_argument("group_name", help="Name of the group")
    parser.add_argument("nickname", help="Nickname of the root")
    parser.add_argument(
        "output_path",
        nargs="?",
        help="Path to output SARIF file",
        default="sarif.json",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as temp_dir:
        await run_cli(args.group_name, args.nickname, Path(temp_dir, "output.json"))


def main_cli() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    main_cli()
