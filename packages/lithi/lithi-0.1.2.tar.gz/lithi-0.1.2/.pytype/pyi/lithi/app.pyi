# (generated with --quick)

import argparse
import lithi
import logging
import pathlib
import sys
from lithi import commands

Cli: type[lithi.core.cli.Cli]
ConfigManager: type[lithi.config.ConfigManager]
Logger: type[lithi.logger.Logger]
Path: type[pathlib.Path]
Settings: type[lithi.bizlog.settings.Settings]
TargetFactory: type[lithi.interface.target.TargetFactory]
__version__: str
logger: lithi.logger._GlobalLoggerProxy

def app() -> None: ...
def get_cache_dirpath() -> str: ...
def get_config_dirpath() -> str: ...
def get_config_name() -> str: ...
def load_commands(cli: lithi.core.cli.Cli, package: module) -> None: ...
def on_cli_init(_: lithi.core.cli.Cli, args: argparse.Namespace) -> None: ...
def on_cli_no_command(cli: lithi.core.cli.Cli, args: argparse.Namespace) -> None: ...
