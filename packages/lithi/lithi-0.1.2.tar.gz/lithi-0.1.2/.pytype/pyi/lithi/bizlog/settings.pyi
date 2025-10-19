# (generated with --quick)

import lithi.config
from typing import Any, Optional

BaseModel: Any
ConfigSettings: type[lithi.config.ConfigSettings]
Field: Any

class DefaultConfig(Any):
    __doc__: str
    session_name: Optional[str]

class SessionConfig(Any):
    __doc__: str
    config: Any
    target: str

class Settings(lithi.config.ConfigSettings):
    __doc__: str
    default: DefaultConfig
    sessions: dict[str, SessionConfig]
