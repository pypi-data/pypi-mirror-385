"""Support for configuration operations."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic_settings import BaseSettings
from xdg_base_dirs import xdg_cache_home, xdg_config_home

from lithi.logger import logger


def get_config_name() -> str:
    """
    Get the configuration name.

    Returns:
        str: The configuration name derived from the module name.
    """
    return __package__


def get_config_dirpath() -> str:
    """
    Get the configuration directory path.

    This path is based on the XDG configuration home.

    Returns:
        str: The absolute path to the configuration directory.
    """
    return os.path.join(xdg_config_home(), get_config_name())


def get_cache_dirpath() -> str:
    """
    Get the cache directory path.

    This path is based on the XDG configuration cache.

    Returns:
        str: The absolute path to the cache directory.
    """
    return os.path.join(xdg_cache_home(), get_config_name())


def _save_config_file(file: Path, data: dict[str, Any]) -> None:
    """Save configuration data to file."""
    if file.suffix == ".json":
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    else:
        raise ValueError(f"Unsupported config format: {file.suffix}")


class ConfigSettings(BaseSettings):
    """Base configuration settings with file and environment support."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


_T = TypeVar("_T", bound=BaseSettings)


class ConfigManager(Generic[_T]):
    """Config loader with reload + save support."""

    settings: _T | None = None
    _path: Path = Path.cwd()
    _settings_cls: type[_T] | None = None
    _SETTINGS_FILE: str = "settings.json"

    @classmethod
    def init(cls, settings_cls: type[_T], path: Path | str) -> None:
        """Initialize the config manager with settings class and path."""
        cls._settings_cls = settings_cls
        cls._path = Path(path) if isinstance(path, str) else path
        logger.info("Initialised config")

    @classmethod
    def load(cls, reload: bool = False) -> _T:
        """Load configuration from file and environment."""
        if not cls._settings_cls:
            raise RuntimeError("Config not initialised yet")
        if reload or cls.settings is None:
            filepath = cls._path / cls._SETTINGS_FILE
            logger.info("Will load the config from %s", filepath)
            if filepath.exists():
                data = json.loads(filepath.read_text())
                cls.settings = cls._settings_cls.model_validate(
                    data
                )  # pytype: disable=attribute-error
            else:
                # Let BaseSettings handle environment variables only
                cls.settings = (
                    # pylint: disable=not-callable
                    cls._settings_cls()
                )

        return cls.settings

    @classmethod
    def save(cls) -> None:
        """Save current configuration to file."""
        if not cls._settings_cls:
            raise RuntimeError("Config not initialised yet")
        if cls.settings is None:
            raise RuntimeError("Config not loaded yet")
        data = cls.settings.model_dump(
            exclude_none=True
        )  # pytype: disable=attribute-error
        filepath = cls._path / cls._SETTINGS_FILE
        _save_config_file(filepath, data)
