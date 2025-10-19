# (generated with --quick)

import argparse
import dataclasses
import lithi.core.args
import lithi.core.cli
import lithi.logger
from typing import Callable, ClassVar, TypeVar, overload

Argument: type[lithi.core.args.Argument]
Command: type[lithi.core.cli.Command]
logger: lithi.logger._GlobalLoggerProxy

_T = TypeVar('_T')

@dataclasses.dataclass
class Development(lithi.core.cli.Command):
    name: ClassVar[str]
    args: ClassVar[list[lithi.core.args.Argument]]
    __doc__: str
    def __init__(self) -> None: ...
    def exec(self, _: argparse.Namespace) -> None: ...

@overload
def dataclass(cls: None, /) -> Callable[[type[_T]], type[_T]]: ...
@overload
def dataclass(cls: type[_T], /) -> type[_T]: ...
@overload
def dataclass(*, init: bool = ..., repr: bool = ..., eq: bool = ..., order: bool = ..., unsafe_hash: bool = ..., frozen: bool = ..., match_args: bool = ..., kw_only: bool = ..., slots: bool = ...) -> Callable[[type[_T]], type[_T]]: ...
