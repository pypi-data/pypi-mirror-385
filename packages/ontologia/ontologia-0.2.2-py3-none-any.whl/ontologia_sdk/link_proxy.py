from __future__ import annotations

import datetime
from collections.abc import Generator
from typing import Any

from ontologia_sdk.client import OntologyClient
from ontologia_sdk.types import TraversalResult


class LinkDescriptor:
    def __init__(
        self,
        link_type: str,
        *,
        to_object_type: str | None = None,
        properties_cls: type | None = None,
    ) -> None:
        self.link_type = link_type
        self.to_object_type = to_object_type
        self.properties_cls = properties_cls

    def __set_name__(self, owner, name):  # pragma: no cover - informational only
        self.name = name

    def __get__(self, instance, owner):  # type: ignore[override]
        if instance is None:
            return self
        return BoundLinkSetProxy(
            instance=instance,
            link_type=self.link_type,
            to_object_type=self.to_object_type,
            properties_cls=self.properties_cls,
        )


class BoundLinkSetProxy:
    def __init__(
        self,
        *,
        instance,
        link_type: str,
        to_object_type: str | None,
        properties_cls: type | None,
    ) -> None:
        self._instance = instance
        self._link_type = link_type
        self._to_object_type = to_object_type
        self._properties_cls = properties_cls

    @property
    def client(self) -> OntologyClient:
        return self._instance._client

    @property
    def from_object_type(self) -> str:
        return self._instance.object_type_api_name

    @property
    def from_pk(self) -> str:
        return self._instance.pk

    def all(self, *, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self.client.traverse(
            self.from_object_type,
            self.from_pk,
            self._link_type,
            limit=limit,
            offset=offset,
        )

    def get(
        self,
        to_pk: str,
        *,
        valid_at: datetime.datetime | datetime.date | str | None = None,
    ) -> dict[str, Any]:
        return self.client.get_link(
            self._link_type,
            self.from_pk,
            to_pk,
            valid_at=valid_at,
        )

    def get_typed(self, to_pk: str):
        raw = self.get(to_pk)
        if not self._properties_cls:
            return raw
        props = dict(raw.get("linkProperties") or {})
        return self._properties_cls.from_dict(props)

    def create(self, to_pk: str, properties: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.client.create_link(self._link_type, self.from_pk, to_pk, properties)

    def delete(self, to_pk: str) -> None:
        self.client.delete_link(self._link_type, self.from_pk, to_pk)

    def list(
        self,
        *,
        to_pk: str | None = None,
        valid_at: datetime.datetime | datetime.date | str | None = None,
    ) -> dict[str, Any]:
        return self.client.list_links(
            self._link_type,
            from_pk=self.from_pk,
            to_pk=to_pk,
            valid_at=valid_at,
        )

    def iter_pages(self, *, page_size: int = 100) -> Generator[dict[str, Any], None, None]:
        offset = 0
        while True:
            page = self.all(limit=page_size, offset=offset)
            yield page
            data = page.get("data") or []
            if len(data) < page_size:
                break
            offset += page_size

    # Backwards-compatible helpers for legacy naming
    def all_typed(self, *, limit: int = 100, offset: int = 0) -> TraversalResult:
        return self._convert_to_traversal(self.all(limit=limit, offset=offset))

    def list_typed(self, *, to_pk: str | None = None) -> TraversalResult:
        return self._convert_to_traversal(self.list(to_pk=to_pk))

    def iter_pages_typed(self, *, page_size: int = 100) -> Generator[TraversalResult, None, None]:
        for page in self.iter_pages(page_size=page_size):
            yield self._convert_to_traversal(page)

    def _convert_to_traversal(self, payload: dict[str, Any]) -> TraversalResult:
        return TraversalResult.from_payload(payload, self._properties_cls)
