from __future__ import annotations

from typing import Optional, Union

from pydantic import AnyUrl, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class KelvinClient(BaseModel):
    URL: Optional[AnyUrl] = None
    USERNAME: Optional[str] = None
    PASSWORD: Optional[str] = None
    TOTP: Optional[int] = None
    CLIENT_ID: Optional[str] = None
    CLIENT_SECRET: Optional[str] = None
    RETRIES: int = 3
    TIMEOUT: Union[float, tuple[float, float]] = (6, 10)


class EnvVars(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_nested_delimiter="__")  # type: ignore[override]

    KELVIN_CLIENT: KelvinClient = KelvinClient()
