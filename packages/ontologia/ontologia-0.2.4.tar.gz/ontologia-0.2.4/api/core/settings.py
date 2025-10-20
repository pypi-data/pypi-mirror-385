"""
api/core/settings.py
---------------------
Centralized application settings using Pydantic Settings.

Environment variables (examples):
- USE_TEMPORAL_ACTIONS=1
- TEMPORAL_ADDRESS=127.0.0.1:7233
- TEMPORAL_NAMESPACE=default
- TEMPORAL_TASK_QUEUE=actions

Defaults are suitable for local development. Values can be provided via .env.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ontologia.config import load_config

_CONFIG = load_config(Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())))


class Settings(BaseSettings):
    # Feature flags
    use_temporal_actions: bool = Field(
        default_factory=lambda: _CONFIG.features.use_temporal_actions
    )

    # Database
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///metamodel.db")
    )

    # Authentication / Authorization
    jwt_secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", "change-me"))
    jwt_algorithm: str = Field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_access_token_ttl_minutes: int = Field(
        default_factory=lambda: int(os.getenv("JWT_ACCESS_TTL_MINUTES", "60"))
    )

    # Temporal
    temporal_address: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_ADDRESS", "127.0.0.1:7233")
    )
    temporal_namespace: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_NAMESPACE", "default")
    )
    temporal_task_queue: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TASK_QUEUE", "actions")
    )
    temporal_tls_enabled: bool = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_ENABLED", "0") in {"1", "true", "True"}
    )
    temporal_tls_server_name: str | None = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_SERVER_NAME")
    )
    temporal_tls_client_cert_path: str | None = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_CLIENT_CERT")
    )
    temporal_tls_client_key_path: str | None = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_CLIENT_KEY")
    )
    temporal_tls_server_ca_path: str | None = Field(
        default_factory=lambda: os.getenv("TEMPORAL_TLS_SERVER_CA")
    )
    temporal_api_key: str | None = Field(default_factory=lambda: os.getenv("TEMPORAL_API_KEY"))
    temporal_api_key_header: str = Field(
        default_factory=lambda: os.getenv("TEMPORAL_API_KEY_HEADER", "authorization")
    )
    temporal_retry_initial_interval_seconds: float = Field(
        default_factory=lambda: float(os.getenv("TEMPORAL_RETRY_INITIAL", "1.0"))
    )
    temporal_retry_max_interval_seconds: float = Field(
        default_factory=lambda: float(os.getenv("TEMPORAL_RETRY_MAX", "60.0"))
    )
    temporal_retry_max_attempts: int = Field(
        default_factory=lambda: int(os.getenv("TEMPORAL_RETRY_ATTEMPTS", "0"))
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
