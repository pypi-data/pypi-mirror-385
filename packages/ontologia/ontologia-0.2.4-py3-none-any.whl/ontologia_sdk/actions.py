from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from typing import Any

ActionMetadata = dict[str, Any]


class ActionsNamespace:
    def __init__(
        self,
        client,
        *,
        enable_validation: bool = True,
        cache_ttl: float = 60.0,
    ) -> None:
        self._client = client
        self._enable_validation = enable_validation
        self._cache_ttl = cache_ttl
        self._cache: dict[tuple[str, str], tuple[float, list[ActionMetadata]]] = {}

    def __getattr__(self, action_name: str) -> Callable[..., Any]:  # type: ignore[override]
        def _call(*, object_type: str, pk: str, **parameters: Any) -> Any:
            return self._call_action(action_name, object_type, pk, parameters)

        return _call

    def available(self, *, object_type: str, pk: str) -> list[ActionMetadata]:
        return self._fetch_metadata(object_type, pk)

    def _call_action(
        self,
        action_name: str,
        object_type: str,
        pk: str,
        parameters: dict[str, Any],
    ) -> Any:
        payload = dict(parameters or {})
        if self._enable_validation:
            metadata = self._fetch_metadata(object_type, pk)
            _validate_parameters(action_name, payload, metadata)
        return self._client.execute_action(object_type, pk, action_name, payload)

    def _fetch_metadata(self, object_type: str, pk: str) -> list[ActionMetadata]:
        key = (object_type, pk)
        cached = self._cache.get(key)
        now = time.monotonic()
        if cached:
            ts, metadata = cached
            if now - ts < self._cache_ttl:
                return metadata
        data = self._client.list_actions(object_type, pk)
        actions = list(data.get("data") or data.get("actions") or [])
        self._cache[key] = (now, actions)
        return actions


class ObjectActionsNamespace:
    def __init__(
        self,
        *,
        client,
        object_type: str,
        pk_getter: Callable[[], str],
        shared_namespace: ActionsNamespace | None = None,
    ) -> None:
        self._client = client
        self._object_type = object_type
        self._pk_getter = pk_getter
        self._shared = shared_namespace or ActionsNamespace(client)

    def __getattr__(self, action_name: str) -> Callable[..., Any]:  # type: ignore[override]
        def _call(**parameters: Any) -> Any:
            return self._shared._call_action(
                action_name, self._object_type, self._pk_getter(), parameters
            )

        return _call

    def available(self) -> list[ActionMetadata]:
        return self._shared.available(object_type=self._object_type, pk=self._pk_getter())


def _validate_parameters(
    action_name: str,
    parameters: dict[str, Any],
    metadata: Iterable[ActionMetadata],
) -> None:
    target = None
    for action in metadata:
        if str(action.get("apiName")) == action_name:
            target = action
            break
    if target is None:
        raise ValueError(f"Unknown action: {action_name}")
    params_meta = target.get("parameters") or []
    required = {str(p.get("apiName")) for p in params_meta if p.get("required")}
    missing = {k for k in required if k not in parameters}
    if missing:
        raise ValueError(
            f"Missing required parameters for action '{action_name}': {sorted(missing)}"
        )
