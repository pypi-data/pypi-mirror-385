"""The main application."""

import argparse
import logging
import sys
from pathlib import Path

import lithi.implementation
from lithi.bizlog.settings import Settings
from lithi.config import (
    ConfigManager,
    get_cache_dirpath,
    get_config_dirpath,
    get_config_name,
)
from lithi.interface.target import TargetFactory

from . import __version__, commands
from .core.cli import Cli, load_commands
from .logger import Logger, logger


def on_cli_init(_: Cli, args: argparse.Namespace) -> None:
    """Perform custom initialisation for the command line init."""
    if args.verbose:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)


def on_cli_no_command(cli: Cli, args: argparse.Namespace) -> None:
    """Handle the default behavior when no command is given."""
    if args.version:
        print(__version__)
        sys.exit(0)
    else:
        cli.print_help()


def app() -> None:
    """Run the main application."""
    try:
        Logger.get(
            name=get_config_name(),
            level=logging.WARNING,
            directory=Path(get_cache_dirpath()),
        )
        ConfigManager.init(
            settings_cls=Settings, path=Path(get_config_dirpath())
        )
        TargetFactory.init(targets_package=lithi.implementation)
        cli = Cli(
            name="lithi",
            description="ELF parser and memory live inspector",
            on_init=on_cli_init,
            on_no_command=on_cli_no_command,
        )

        load_commands(cli, commands)
        cli.exec()

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    app()
