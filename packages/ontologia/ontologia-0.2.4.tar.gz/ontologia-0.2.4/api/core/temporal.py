from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    from temporalio.client import Client
    from temporalio.service import RetryConfig, TLSConfig
except Exception:  # pragma: no cover - optional dependency
    Client = None  # type: ignore
    RetryConfig = None  # type: ignore
    TLSConfig = None  # type: ignore

from fastapi import Request

from api.core.settings import Settings


def get_temporal_client(request: Request) -> Any | None:
    """FastAPI dependency to retrieve the Temporal client singleton.

    Returns None when Temporal is disabled or client wasn't initialized.
    """
    app = request.app
    return getattr(app.state, "temporal_client", None)


@lru_cache
def _read_bytes(path: str | None) -> bytes | None:
    if not path:
        return None
    data = Path(path).expanduser().read_bytes()
    return data


def _build_tls_config(settings: Settings) -> TLSConfig | None:
    if not settings.temporal_tls_enabled:
        return None
    if TLSConfig is None:
        raise RuntimeError("temporalio package required for TLS configuration")
    client_cert = _read_bytes(settings.temporal_tls_client_cert_path)
    client_key = _read_bytes(settings.temporal_tls_client_key_path)
    server_ca = _read_bytes(settings.temporal_tls_server_ca_path)
    if not settings.temporal_tls_server_name:
        raise ValueError("TEMPORAL_TLS_SERVER_NAME required when TLS is enabled")
    return TLSConfig(
        domain=settings.temporal_tls_server_name,
        server_root_ca_cert=server_ca,
        client_cert=client_cert,
        client_private_key=client_key,
    )


async def connect_temporal(settings: Settings) -> Client:
    if Client is None or RetryConfig is None:
        raise RuntimeError("temporalio package not installed; unable to connect to Temporal")
    tls_config = _build_tls_config(settings)
    metadata = None
    if settings.temporal_api_key:
        token = settings.temporal_api_key
        metadata = {settings.temporal_api_key_header: f"Bearer {token}"}
    retry_cfg = RetryConfig(
        initial_interval_millis=int(settings.temporal_retry_initial_interval_seconds * 1000),
        max_interval_millis=int(settings.temporal_retry_max_interval_seconds * 1000),
        max_retries=settings.temporal_retry_max_attempts,
    )
    return await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
        tls=tls_config if tls_config is not None else False,
        retry_config=retry_cfg,
        rpc_metadata=metadata or {},
    )
