from __future__ import annotations

from datetime import date, datetime
from typing import Any

import httpx

from ontologia_sdk.actions import ActionsNamespace


class OntologyClient:
    """
    Thin synchronous client for the Ontology API v2.

    Usage:
        client = OntologyClient(host="http://localhost:8000", ontology="default", token=None)
        obj = client.get_object("employee", "e1")
    """

    def __init__(
        self,
        host: str = "http://localhost:8000",
        *,
        ontology: str = "default",
        token: str | None = None,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        enable_action_validation: bool = True,
        action_cache_ttl: float = 60.0,
    ) -> None:
        self.host = host.rstrip("/")
        self.ontology = ontology
        self._timeout = timeout
        self._session = httpx.Client(timeout=timeout)
        base_headers: dict[str, str] = {"Accept": "application/json"}
        if token:
            base_headers["Authorization"] = f"Bearer {token}"
        if headers:
            base_headers.update(headers)
        self._headers = base_headers
        self.actions = ActionsNamespace(
            self,
            enable_validation=enable_action_validation,
            cache_ttl=action_cache_ttl,
        )

    # --- Helpers ---
    def _format_timestamp(self, value: datetime | date | str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day).isoformat()
        return str(value)

    # --- Metamodel ---
    def list_object_types(self) -> list[dict[str, Any]]:
        url = f"{self.host}/v2/ontologies/{self.ontology}/objectTypes"
        r = self._session.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json().get("data", [])

    def list_link_types(self) -> list[dict[str, Any]]:
        url = f"{self.host}/v2/ontologies/{self.ontology}/linkTypes"
        r = self._session.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json().get("data", [])

    def list_interfaces(self) -> list[dict[str, Any]]:
        url = f"{self.host}/v2/ontologies/{self.ontology}/interfaces"
        r = self._session.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json().get("data", [])

    # --- Objects ---
    def get_object(
        self,
        object_type: str,
        pk: str,
        *,
        valid_at: datetime | date | str | None = None,
    ) -> dict[str, Any]:
        base = f"{self.host}/v2/ontologies/{self.ontology}/objects/{object_type}/{pk}"
        ts = self._format_timestamp(valid_at)
        url = base + (f"?validAt={ts}" if ts else "")
        r = self._session.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json()

    def upsert_object(
        self, object_type: str, pk: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        url = f"{self.host}/v2/ontologies/{self.ontology}/objects/{object_type}/{pk}"
        r = self._session.put(url, headers=self._headers, json={"properties": properties})
        r.raise_for_status()
        return r.json()

    def delete_object(self, object_type: str, pk: str) -> None:
        url = f"{self.host}/v2/ontologies/{self.ontology}/objects/{object_type}/{pk}"
        r = self._session.delete(url, headers=self._headers)
        if r.status_code not in (200, 204):
            r.raise_for_status()

    def search_objects(
        self,
        object_type: str,
        *,
        where: list[dict[str, Any]] | None = None,
        order_by: list[dict[str, Any]] | None = None,
        limit: int = 100,
        offset: int = 0,
        traverse: list[dict[str, Any]] | None = None,
        as_of: datetime | date | str | None = None,
    ) -> dict[str, Any]:
        url = f"{self.host}/v2/ontologies/{self.ontology}/objects/{object_type}/search"
        body = {
            "where": list(where or []),
            "orderBy": list(order_by or []),
            "limit": int(limit),
            "offset": int(offset),
            "traverse": list(traverse or []),
        }
        ts = self._format_timestamp(as_of)
        if ts:
            body["asOf"] = ts
        r = self._session.post(url, headers=self._headers, json=body)
        r.raise_for_status()
        return r.json()

    # --- Traversal ---
    def traverse(
        self,
        from_object_type: str,
        from_pk: str,
        link_type: str,
        *,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | date | str | None = None,
    ) -> dict[str, Any]:
        base = f"{self.host}/v2/ontologies/{self.ontology}/objects/{from_object_type}/{from_pk}/{link_type}"
        params = [f"limit={int(limit)}", f"offset={int(offset)}"]
        ts = self._format_timestamp(valid_at)
        if ts:
            params.append(f"validAt={ts}")
        url = base + ("?" + "&".join(params))
        r = self._session.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json()

    # --- Links (edges) ---
    def create_link(
        self, link_type: str, from_pk: str, to_pk: str, properties: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"{self.host}/v2/ontologies/{self.ontology}/links/{link_type}"
        payload = {"fromPk": from_pk, "toPk": to_pk, "properties": dict(properties or {})}
        r = self._session.post(url, headers=self._headers, json=payload)
        r.raise_for_status()
        return r.json()

    def get_link(
        self,
        link_type: str,
        from_pk: str,
        to_pk: str,
        *,
        valid_at: datetime | date | str | None = None,
    ) -> dict[str, Any]:
        base = f"{self.host}/v2/ontologies/{self.ontology}/links/{link_type}/{from_pk}/{to_pk}"
        ts = self._format_timestamp(valid_at)
        url = base + (f"?validAt={ts}" if ts else "")
        r = self._session.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json()

    def list_links(
        self,
        link_type: str,
        *,
        from_pk: str | None = None,
        to_pk: str | None = None,
        valid_at: datetime | date | str | None = None,
    ) -> dict[str, Any]:
        base = f"{self.host}/v2/ontologies/{self.ontology}/links/{link_type}"
        params: list[str] = []
        if from_pk is not None:
            params.append(f"fromPk={from_pk}")
        if to_pk is not None:
            params.append(f"toPk={to_pk}")
        ts = self._format_timestamp(valid_at)
        if ts:
            params.append(f"validAt={ts}")
        url = base + ("?" + "&".join(params) if params else "")
        r = self._session.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json()

    def delete_link(self, link_type: str, from_pk: str, to_pk: str) -> None:
        url = f"{self.host}/v2/ontologies/{self.ontology}/links/{link_type}/{from_pk}/{to_pk}"
        r = self._session.delete(url, headers=self._headers)
        if r.status_code not in (200, 204):
            r.raise_for_status()

    # --- Actions ---
    def list_actions(self, object_type: str, pk: str) -> dict[str, Any]:
        url = f"{self.host}/v2/ontologies/{self.ontology}/objects/{object_type}/{pk}/actions"
        r = self._session.get(url, headers=self._headers)
        r.raise_for_status()
        return r.json()

    def execute_action(
        self,
        object_type: str,
        pk: str,
        action_api_name: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.host}/v2/ontologies/{self.ontology}/objects/{object_type}/{pk}/actions/{action_api_name}/execute"
        r = self._session.post(
            url, headers=self._headers, json={"parameters": dict(parameters or {})}
        )
        r.raise_for_status()
        return r.json()

    # --- Utilities ---
    def close(self) -> None:
        try:
            self._session.close()
        except Exception:
            pass
