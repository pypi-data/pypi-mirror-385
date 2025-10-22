import subprocess
import sys
from pathlib import Path

import click

from pytest_tui_runner.logging import logger, setup_logger
from pytest_tui_runner.paths import Paths, find_project_root_by_folder
from pytest_tui_runner.ui.tui.app import TestRunnerApp


@click.group()
def cli() -> None:
    """CLI for pytest-tui-runner plugin."""


@cli.command()
@click.argument("project_path", required=False, type=click.Path(exists=True, file_okay=False))
def run(project_path: str | None) -> None:
    """Run the terminal application."""
    try:
        if project_path:
            root = Path(project_path).resolve()
            Paths.set_user_root(root)
        else:
            root = find_project_root_by_folder(Path.cwd(), ["pytest_tui_runner"])
            if root is None:
                logger.error("Could not find project root (missing 'tests' directory).")
                sys.exit(1)
            Paths.set_user_root(root)

        setup_logger()
        logger.info("=============================== NEW RECORD ===============================")
        logger.debug("---------------------- APPLICATION PREPARATION ----------------------")
        logger.info(f"Path to user's project found: '{root}'")

        logger.info("▶️ Starting the application...")
        app = TestRunnerApp()
        app.run()

    except subprocess.CalledProcessError as e:
        logger.error(f"Error launching the application: {e}")
        sys.exit(1)
