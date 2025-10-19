# (generated with --quick)

import json
import lithi.logger
import os
import pathlib
from typing import Any, Generic, Optional, TypeVar, Union

BaseSettings: Any
Path: type[pathlib.Path]
__package__: None
logger: lithi.logger._GlobalLoggerProxy
xdg_cache_home: Any
xdg_config_home: Any

_T = TypeVar('_T', bound=Any)

class ConfigManager(Generic[_T]):
    _SETTINGS_FILE: str
    __doc__: str
    _path: pathlib.Path
    _settings_cls: Optional[type[_T]]
    settings: Optional[_T]
    @classmethod
    def init(cls, settings_cls: type[_T], path: Union[str, pathlib.Path]) -> None: ...
    @classmethod
    def load(cls, reload: bool = ...) -> _T: ...
    @classmethod
    def save(cls) -> None: ...

class ConfigSettings(Any):
    __doc__: str
    model_config: dict[str, str]

def _save_config_file(file: pathlib.Path, data: dict[str, Any]) -> None: ...
def get_cache_dirpath() -> str: ...
def get_config_dirpath() -> str: ...
def get_config_name() -> str: ...
