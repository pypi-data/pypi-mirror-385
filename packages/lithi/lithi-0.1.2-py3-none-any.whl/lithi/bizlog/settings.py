"""Settings for this app."""

from typing import Any

from pydantic import BaseModel, Field

from lithi.config import ConfigSettings


class SessionConfig(BaseModel):
    """Session configuration model."""

    target: str = "sim"
    config: Any | None = None


class DefaultConfig(BaseModel):
    """Default configuration model."""

    session_name: str | None = None


class Settings(ConfigSettings):
    """Application settings."""

    default: DefaultConfig = DefaultConfig()
    sessions: dict[str, SessionConfig] = Field(default_factory=dict)
