# (generated with --quick)

import argparse
import dataclasses
import inspect
import lithi.bizlog.settings
import lithi.config
import lithi.core.args
import lithi.core.cli
import lithi.interface.target
import lithi.logger
import sys
import typing
from typing import Any, Callable, ClassVar, TypeVar, overload

Argument: type[lithi.core.args.Argument]
ArgumentBoolean: type[lithi.core.args.ArgumentBoolean]
BaseModel: Any
Command: type[lithi.core.cli.Command]
ConfigManager: type[lithi.config.ConfigManager]
SessionConfig: type[lithi.bizlog.settings.SessionConfig]
Settings: type[lithi.bizlog.settings.Settings]
TargetFactory: type[lithi.interface.target.TargetFactory]
ValidationError: Any
logger: lithi.logger._GlobalLoggerProxy

_T = TypeVar('_T')

@dataclasses.dataclass
class ConfigCommand(lithi.core.cli.Command):
    name: ClassVar[str]
    args: ClassVar[list[lithi.core.args.Argument]]
    __doc__: str
    def __init__(self) -> None: ...
    def exec(self, _: argparse.Namespace) -> None: ...

def _convert_input_value(raw_input: str, field_type) -> Any: ...
def _get_field_default_value(field) -> Any: ...
def _parse_boolean(value: str) -> bool: ...
@overload
def dataclass(cls: None, /) -> Callable[[type[_T]], type[_T]]: ...
@overload
def dataclass(cls: type[_T], /) -> type[_T]: ...
@overload
def dataclass(*, init: bool = ..., repr: bool = ..., eq: bool = ..., order: bool = ..., unsafe_hash: bool = ..., frozen: bool = ..., match_args: bool = ..., kw_only: bool = ..., slots: bool = ...) -> Callable[[type[_T]], type[_T]]: ...
def get_init_args(cls: type) -> list[dict[str, Any]]: ...
def get_logo() -> str: ...
def prompt_for_model(model_cls: type) -> Any: ...
