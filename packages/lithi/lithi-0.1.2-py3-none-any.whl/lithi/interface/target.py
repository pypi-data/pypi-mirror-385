"""Module for base target data acquisition."""

from __future__ import annotations

import importlib
import pkgutil
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from types import ModuleType
from typing import Any, TypeVar, cast

from pydantic import BaseModel


class TargetData(ABC):
    """Abstract base for data that can be read from a target."""

    @classmethod
    def format(cls, value: int | list[int] | None) -> str | list[str]:
        """Format integers or lists of integers as hex strings."""
        formatted: list[str] | str = "?"
        if isinstance(value, int):
            formatted = f"0x{value & 0xFFFFFFFF:08X}"
        elif isinstance(value, list) and all(
            isinstance(v, int) for v in value
        ):
            formatted = [f"0x{v & 0xFF:02X}" for v in value]
        elif value is None:
            formatted = "?"
        else:
            raise TypeError(f"Unsupported type: {type(value).__name__}")
        return formatted

    def read_from(self, target: BaseTarget) -> list[int]:
        """Read data from the target via a dynamically resolved method."""
        method_name = f"_read_{self.__class__.__name__.lower()}"
        method = getattr(target, method_name, None)
        if method is None:
            raise NotImplementedError(
                f"{target.__class__.__name__} does not implement {method_name}"
            )

        # Tell mypy: this is a callable taking Any and returning list[int]
        typed_method = cast(Callable[[Any], list[int]], method)
        return typed_method(self)


@dataclass(frozen=True)
class CoreRegister(TargetData):
    """Represent a CPU core register."""

    name: str

    def __str__(self) -> str:
        """Return a human-readable string representation of the object."""
        return self.name


@dataclass(frozen=True)
class MemoryArea(TargetData):
    """Represent a memory area in the target."""

    address: int
    size: int

    def __str__(self) -> str:
        """Return a human-readable string representation of the object."""
        return f"0x{self.address:08X}"


class TargetFactory:
    """
    Create and manage target instances with auto-discovery.

    This is a factory design pattern.
    """

    _is_initialised: bool = False
    _registry: dict[str, tuple[type[BaseTarget], type[BaseModel] | None]] = {}

    @classmethod
    def init(cls, targets_package: ModuleType) -> None:
        """
        Initialize the target factory with auto-discovery.

        Args:
            targets_package: Package to scan for target modules.
        """
        for _, module_name, _ in pkgutil.iter_modules(
            targets_package.__path__
        ):
            importlib.import_module(
                f"{targets_package.__name__}.{module_name}"
            )
        cls._is_initialised = True

    @classmethod
    def register(
        cls,
        name: str,
        target_cls: type[BaseTarget],
        config_cls: type[BaseModel] | None,
    ) -> None:
        """
        Register a target class with its configuration.

        Args:
            name: Target identifier.
            target_cls: Target class to register.
            config_cls: Configuration class for the target.
        """
        cls._registry[name] = (target_cls, config_cls)

    @classmethod
    def create(
        cls, name: str, cfg: dict[str, Any] | BaseModel | None = None
    ) -> BaseTarget:
        """
        Create a target instance by name.

        Args:
            name: Registered target name.
            cfg: Configuration as dict, Pydantic model, or None.

        Returns:
            Instantiated target object.

        Raises:
            RuntimeError: If factory not initialized.
            ValueError: If target name not found.
        """
        if not cls._is_initialised:
            raise RuntimeError(f"{cls.__name__} is not initialised")
        if name not in cls._registry:
            raise ValueError(f"Unknown target: {name}")
        target_cls, config_cls = cls._registry[name]

        if cfg is None:
            # No configuration provided
            return target_cls()  # pytype: disable=not-instantiable

        if config_cls is None:
            # Target doesn't expect configuration
            return target_cls()  # pytype: disable=not-instantiable

        # Handle different config input types
        validated_cfg = cls._prepare_config(cfg, config_cls)
        return target_cls(validated_cfg)  # pytype: disable=not-instantiable

    @classmethod
    def _prepare_config(
        cls, cfg: dict[str, Any] | BaseModel, config_cls: type[BaseModel]
    ) -> BaseModel:
        """
        Prepare configuration for target creation.

        Args:
            cfg: Configuration as dict or Pydantic model.
            config_cls: Expected configuration class.

        Returns:
            Validated configuration instance.
        """
        if not isinstance(cfg, BaseModel):
            # cfg is a dict - validate with Pydantic
            return config_cls.model_validate(cfg)
        # cfg is already a Pydantic model
        if isinstance(cfg, config_cls):
            # Perfect match - use as-is
            return cfg
        if hasattr(cfg, "model_dump"):
            # Different Pydantic model - convert via dict
            return config_cls.model_validate(cfg.model_dump())
        # Shouldn't happen, but fallback
        raise ValueError(f"Cannot convert {type(cfg)} to {config_cls}")

    @classmethod
    def get_config_type(cls, name: str) -> type[BaseModel] | None:
        """
        Get the configuration type for a registered target.

        Args:
            name: Target name.

        Returns:
            Configuration class or None.

        Raises:
            RuntimeError: If factory not initialized.
            ValueError: If target name not found.
        """
        if not cls._is_initialised:
            raise RuntimeError(f"{cls.__name__} is not initialised")
        if name not in cls._registry:
            raise ValueError(f"Unknown target: {name}")
        return cls._registry[name][1]

    @classmethod
    def get_target_type(cls, name: str) -> type[BaseTarget]:
        """
        Get the target class for a registered target.

        Args:
            name: Target name.

        Returns:
            Target class.

        Raises:
            RuntimeError: If factory not initialized.
            ValueError: If target name not found.
        """
        if not cls._is_initialised:
            raise RuntimeError(f"{cls.__name__} is not initialised")
        if name not in cls._registry:
            raise ValueError(f"Unknown target: {name}")
        return cls._registry[name][0]

    @classmethod
    def available(cls) -> list[str]:
        """
        Get list of available target names.

        Returns:
            List of registered target names.

        Raises:
            RuntimeError: If factory not initialized.
        """
        if not cls._is_initialised:
            raise RuntimeError(f"{cls.__name__} is not initialised")
        return list(cls._registry.keys())


class BaseTarget(ABC):
    """Abstract interface for communicating with a target device."""

    UNKNOWN_BYTE: int = 0xAA

    def __init__(self, config: BaseModel | None = None) -> None:
        """Initialize the object."""
        self.config = config

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if a connection to the target backend is established."""
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the target backend."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection to the target backend."""
        raise NotImplementedError

    @abstractmethod
    def is_stopped(self) -> bool:
        """Check if the target is currently stopped."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Stop the target."""
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        """Resume execution on the target."""
        raise NotImplementedError

    def read(self, target: TargetData) -> list[int] | int | None:
        """
        Read data from the target using TargetData interface.

        Args:
            target: TargetData instance specifying what to read.

        Returns:
            Data read from target.
        """
        return target.read_from(self)

    @abstractmethod
    def get_core_registers(self) -> list[CoreRegister]:
        """Get a list of the available core registers."""
        raise NotImplementedError


_T = TypeVar("_T", bound=BaseTarget)


def register_target(
    name: str, config_cls: type[BaseModel] | None = None
) -> Callable[[type[_T]], type[_T]]:
    """
    Register a target class and its configuration type.

    This is a decorator.
    """

    def wrapper(target_cls: type[_T]) -> type[_T]:
        """Register the target class and return it unchanged."""
        TargetFactory.register(name, target_cls, config_cls)
        return target_cls

    return wrapper
