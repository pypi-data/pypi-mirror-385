# (generated with --quick)

import datetime as _datetime
import logging
import pathlib
import sys
import time
from typing import Any, Optional, TextIO, TypeVar, Union

Path: type[pathlib.Path]
datetime: type[_datetime.datetime]
logger: _GlobalLoggerProxy
timezone: type[_datetime.timezone]

_T = TypeVar('_T')
_TLogger = TypeVar('_TLogger', bound=Logger)

class ColoredFormatter(logging.Formatter):
    COLORS: dict[str, str]
    __doc__: str
    _start_time: float
    enable_colors: bool
    def __init__(self, *args, **kwargs) -> None: ...
    def format(self, record: logging.LogRecord) -> str: ...

class Logger(logging.Logger):
    __doc__: str
    c_handler: logging.StreamHandler[TextIO]
    f_handler: logging.FileHandler
    def __init__(self, name: str = ..., level: int = ..., directory: Optional[pathlib.Path] = ...) -> None: ...
    @classmethod
    def get(cls: type[_TLogger], *args, **kwargs) -> _TLogger: ...
    def setLevel(self, level: Union[int, str]) -> None: ...

class _GlobalLoggerProxy:
    __doc__: str
    def __getattr__(self, attr: str) -> Any: ...

def get_utc_timestamp() -> str: ...
def singleton(cls: type[_T]) -> type[_T]: ...
