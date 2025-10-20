from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

T = TypeVar("T")
PropsT = TypeVar("PropsT")


class SupportsFromDict(Protocol[PropsT]):
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PropsT: ...


@dataclass
class Page(Generic[T]):
    data: list[T]
    next_page_token: str | None = None


@dataclass
class LinkedEdge:
    from_pk: str
    to_pk: str
    link_properties: object
    raw: dict


@dataclass
class TraversalResult(Page[LinkedEdge]):
    @classmethod
    def from_payload(
        cls,
        payload: dict[str, Any],
        properties_cls: type[SupportsFromDict[Any]] | None,
    ) -> TraversalResult:
        edges: list[LinkedEdge] = []
        for item in list(payload.get("data") or []):
            props_raw = dict(item.get("linkProperties") or {})
            props_typed = properties_cls.from_dict(props_raw) if properties_cls else props_raw
            edges.append(
                LinkedEdge(
                    from_pk=str(item.get("fromPk", "")),
                    to_pk=str(item.get("toPk", "")),
                    link_properties=props_typed,
                    raw=item,
                )
            )
        return cls(data=edges, next_page_token=payload.get("nextPageToken"))


def page_from_payload(payload: dict[str, Any], converter: Callable[[dict[str, Any]], T]) -> Page[T]:
    items = [converter(item) for item in list(payload.get("data") or [])]
    return Page(data=items, next_page_token=payload.get("nextPageToken"))
