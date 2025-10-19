"""Config command."""

from __future__ import annotations

import argparse
import inspect
import sys
import typing
from dataclasses import dataclass
from typing import Any, ClassVar, get_type_hints

from pydantic import BaseModel, ValidationError

from lithi.bizlog.brand import get_logo
from lithi.bizlog.settings import SessionConfig, Settings
from lithi.config import ConfigManager
from lithi.core.args import (
    Argument,
    ArgumentBoolean,
)
from lithi.core.cli import Command
from lithi.interface.target import TargetFactory
from lithi.logger import logger


def _parse_boolean(value: str) -> bool:
    """Parse string input to boolean."""
    lower_value = value.lower()

    if lower_value in ("true", "1", "yes", "y", "on"):
        return True
    if lower_value in ("false", "0", "no", "n", "off"):
        return False
    raise ValueError(
        "Enter True/False (accepted: true/false, 1/0, yes/no, y/n, on/off)"
    )


def _convert_input_value(raw_input: str, field_type: Any) -> Any:
    """Convert raw input string to the appropriate type."""
    # Handle None/null inputs
    if raw_input.lower() in ("none", "null", "n/a"):
        return None

    # Check if it's an Optional type (Union with None)
    actual_type = field_type

    if (
        hasattr(typing, "get_origin")
        and typing.get_origin(field_type) is typing.Union
    ):
        args = typing.get_args(field_type)
        NoneType = type(None)
        if NoneType in args:
            # Get the non-None type
            non_none_types = [arg for arg in args if arg is not NoneType]
            if non_none_types:
                actual_type = non_none_types[0]

    # Convert based on type
    if actual_type is bool:
        return _parse_boolean(raw_input)
    if actual_type is int:
        return int(raw_input)
    if actual_type is float:
        return float(raw_input)

    # For str and other types, return as string
    return raw_input


def _get_field_default_value(field: Any) -> Any:
    """
    Get the default value for a Pydantic field in a version-agnostic way.

    Args:
        field: Pydantic field info object

    Returns:
        Default value for the field, or None if no default exists
    """
    try:
        # Check if field has a concrete default value
        if hasattr(field, "default") and field.default is not ...:
            return field.default

        # Check if field has a default factory
        if (
            hasattr(field, "default_factory")
            and field.default_factory is not None
        ):
            try:
                return field.default_factory()
            except TypeError:
                # Some factories need arguments, return placeholder
                return None

        return None
    except (AttributeError, RuntimeError, ValueError):
        # Catch specific exceptions that might occur during field access
        return None


def get_init_args(cls: type[Any]) -> list[dict[str, Any]]:
    """
    Extract initialization arguments from a class constructor.

    Analyzes the __init__ method of a class and returns detailed information
    about each parameter including name, type hint, and default value.

    Args:
        cls: The class to inspect for initialization arguments.

    Returns:
        A list of dictionaries, each containing:
            - name (str): Parameter name
            - type: Type hint if available, None otherwise
            - default: Default value if specified, None otherwise

    Example:
        >>> class MyClass:
        ...     def __init__(self, name: str, age: int = 25):
        ...         pass
        >>> get_init_args(MyClass)
        [
            {'name': 'name', 'type': <class 'str'>, 'default': None},
            {'name': 'age', 'type': <class 'int'>, 'default': 25}
        ]
    """
    sig = inspect.signature(cls.__init__)
    parameters = list(sig.parameters.values())[1:]  # Skip 'self'
    args = []
    for param in parameters:
        arg = {
            "name": param.name,
            "type": get_type_hints(cls.__init__).get(param.name, None),
            "default": (
                param.default
                if param.default != inspect.Parameter.empty
                else None
            ),
        }
        args.append(arg)
    return args


def prompt_for_model(model_cls: type[BaseModel]) -> BaseModel | None:
    """
    Prompt user to fill in all fields of a Pydantic model interactively.

    Press Enter to accept default values.

    Args:
        model_cls: The Pydantic model class to configure.

    Returns:
        Configured model instance or None if cancelled.

    Raises:
        ValidationError: If the final model validation fails.
    """
    values: dict[str, Any] = {}

    for name, field in model_cls.model_fields.items():
        # Get default value - use empty string if no default
        default_value = _get_field_default_value(field)
        field_type = field.annotation

        while True:
            prompt_text = f"{name}"
            if default_value is not None and default_value != "":
                prompt_text += f" [{default_value}]"
            prompt_text += ": "

            raw = input(prompt_text).strip()

            if not raw:
                if default_value is not None:
                    values[name] = default_value
                break

            try:
                values[name] = _convert_input_value(raw, field_type)
                break

            except (ValueError, TypeError):
                logger.error(
                    f"Invalid input for '{name}'. Extected type '{field_type}'"
                )
                continue

    try:
        return model_cls(**values)
    except ValidationError as e:
        logger.error(f"Model validation failed: {e}")
        return None


@dataclass
class ConfigCommand(Command):
    """Configure this tool."""

    name: ClassVar[str] = "config"
    args: ClassVar[list[Argument]] = [
        ArgumentBoolean(
            name="list",
            flag="l",
            default=False,
            description="List all available sessions",
        ),
    ]

    def exec(self, _: argparse.Namespace) -> None:
        """Execute the command."""
        print(get_logo())

        # Select session name
        selected_session_name = (
            input("Enter a name for this session[default]: ") or "default"
        )

        # Select target for session
        print(f"Available targets: {TargetFactory.available()}")
        selected_target_name = input("Enter your target[sim]: ") or "sim"
        try:
            target_cls = TargetFactory.get_target_type(selected_target_name)
        except ValueError:
            logger.critical(f"Target '{selected_target_name}' does not exist")
            sys.exit(1)
        target_init_args = get_init_args(target_cls)
        config_target_cls = None
        if len(target_init_args) == 1:
            target_init_arg = target_init_args[0]
            config_target_cls = target_init_arg["type"]
        elif len(target_init_args) == 0:
            config_target_cls = None
        else:
            raise ValueError("f'{selected_target_name}' is not configurable")

        # Select configuration
        try:
            if config_target_cls:
                target_config = prompt_for_model(config_target_cls)
            else:
                target_config = None
        except ValidationError as e:
            logger.critical("Validation error %s", e)
            sys.exit(1)

        # Save the settings
        settings: Settings = ConfigManager.load()
        settings.default.session_name = selected_session_name
        settings.sessions[selected_session_name] = SessionConfig(
            target=selected_target_name, config=target_config
        )
        ConfigManager.save()
