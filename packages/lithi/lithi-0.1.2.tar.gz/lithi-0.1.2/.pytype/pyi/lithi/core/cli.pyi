# (generated with --quick)

import abc
import argparse
import dataclasses
import importlib
import inspect
import lithi.core.args
import lithi.logger
import pkgutil
import types
import typing
from typing import Any, ClassVar, Optional, TypeVar, overload

ABC: type[abc.ABC]
Argument: type[lithi.core.args.Argument]
Callable: type
logger: lithi.logger._GlobalLoggerProxy

_FuncT = TypeVar('_FuncT', bound=typing.Callable)
_T = TypeVar('_T')

class Cli:
    __doc__: str
    commands: dict[str, Command]
    on_init: Any
    on_no_command: Any
    parser: argparse.ArgumentParser
    def __init__(self, name: str = ..., description: Optional[str] = ..., on_init: Optional[typing.Callable[[Cli, argparse.Namespace], None]] = ..., on_no_command: Optional[typing.Callable[[Cli, argparse.Namespace], None]] = ...) -> None: ...
    def exec(self) -> None: ...
    def print_help(self) -> None: ...
    def register_arg(self, parser: argparse.ArgumentParser, argument: lithi.core.args.Argument) -> None: ...
    def register_cmd(self, command: Command) -> None: ...

@dataclasses.dataclass
class Command(abc.ABC):
    name: ClassVar[str]
    args: ClassVar[Optional[list[lithi.core.args.Argument]]]
    __doc__: str
    def __init__(self) -> None: ...
    def __init_subclass__(cls, **kwargs) -> None: ...
    @abstractmethod
    def exec(self, args: argparse.Namespace) -> None: ...

def abstractmethod(funcobj: _FuncT) -> _FuncT: ...
@overload
def dataclass(cls: None, /) -> typing.Callable[[type[_T]], type[_T]]: ...
@overload
def dataclass(cls: type[_T], /) -> type[_T]: ...
@overload
def dataclass(*, init: bool = ..., repr: bool = ..., eq: bool = ..., order: bool = ..., unsafe_hash: bool = ..., frozen: bool = ..., match_args: bool = ..., kw_only: bool = ..., slots: bool = ...) -> typing.Callable[[type[_T]], type[_T]]: ...
def load_commands(cli: Cli, package: module) -> None: ...
