from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .dsl import Expr, as_expr
from .types import Page, page_from_payload


@dataclass
class WhereCondition:
    property: str
    op: str
    value: Any


@dataclass
class OrderBySpec:
    property: str
    direction: str = "asc"


class QueryBuilder:
    def __init__(self, *, client, object_type: str, object_cls=None):
        self._client = client
        self._object_type = object_type
        self._where_exprs: list[Expr] = []
        self._order_specs: list[dict[str, Any]] = []
        self._limit: int = 100
        self._offset: int = 0
        self._traverse_steps: list[dict[str, Any]] = []
        self._object_cls = object_cls

    def where(self, *conds: Any) -> QueryBuilder:
        for cond in conds:
            self._consume_where(cond)
        return self

    def order_by(self, *specs: Any) -> QueryBuilder:
        for spec in specs:
            self._consume_order(spec)
        return self

    def limit(self, n: int) -> QueryBuilder:
        self._limit = int(n)
        return self

    def offset(self, n: int) -> QueryBuilder:
        self._offset = int(n)
        return self

    def traverse(
        self,
        link: Any,
        *,
        where: Any | None = None,
        limit: int | None = None,
        direction: str = "forward",
    ) -> QueryBuilder:
        link_name = (
            getattr(link, "link_type", None)
            or getattr(link, "_link_type", None)
            or getattr(link, "linkTypeApiName", None)
            or str(link)
        )
        filters = self._normalize_where(where)
        step: dict[str, Any] = {
            "link": link_name,
            "direction": direction,
            "where": _serialize_where(filters),
        }
        if limit is not None:
            step["limit"] = int(limit)
        self._traverse_steps.append(step)
        return self

    def all(self) -> dict[str, Any]:
        return self._run(limit=self._limit, offset=self._offset)

    def all_typed(self) -> Page[Any]:
        if self._object_cls is None:
            raise ValueError("Object class not provided for typed results")
        payload = self._run(limit=self._limit, offset=self._offset)
        return page_from_payload(payload, self._build_object)

    def iter_pages(self, *, page_size: int | None = None):
        size = int(page_size or self._limit or 100)
        offset = self._offset
        while True:
            payload = self._run(limit=size, offset=offset)
            data = payload.get("data") or []
            if not data:
                break
            yield payload
            if len(data) < size:
                break
            offset += size

    def iter_pages_typed(self, *, page_size: int | None = None):
        if self._object_cls is None:
            raise ValueError("Object class not provided for typed results")
        for payload in self.iter_pages(page_size=page_size):
            yield page_from_payload(payload, self._build_object)

    def _consume_where(self, cond: Any) -> None:
        if cond is None:
            return
        if isinstance(cond, WhereCondition):
            expr = Expr(
                op="leaf",
                operands=[{"property": cond.property, "op": cond.op, "value": cond.value}],
            )
            self._where_exprs.append(expr)
            return
        if isinstance(cond, (list, tuple)):
            for item in cond:
                self._consume_where(item)
            return
        if isinstance(cond, Expr):
            self._where_exprs.append(cond)
            return
        if isinstance(cond, dict):
            self._where_exprs.append(as_expr(cond))
            return
        raise TypeError(f"Unsupported where condition: {cond!r}")

    def _consume_order(self, spec: Any) -> None:
        if spec is None:
            return
        if isinstance(spec, OrderBySpec):
            self._order_specs.append({"property": spec.property, "direction": spec.direction})
            return
        if isinstance(spec, (list, tuple)):
            for item in spec:
                self._consume_order(item)
            return
        if isinstance(spec, Expr):
            self._order_specs.append(spec.to_order_spec())
            return
        if isinstance(spec, dict):
            self._order_specs.append(dict(spec))
            return
        raise TypeError(f"Unsupported order specification: {spec!r}")

    def _normalize_where(self, conds: Any) -> list[Expr]:
        exprs: list[Expr] = []
        if conds is None:
            return exprs
        if isinstance(conds, Expr):
            exprs.append(conds)
            return exprs
        if isinstance(conds, WhereCondition):
            exprs.append(
                Expr(
                    op="leaf",
                    operands=[{"property": conds.property, "op": conds.op, "value": conds.value}],
                )
            )
            return exprs
        if isinstance(conds, dict):
            exprs.append(as_expr(conds))
            return exprs
        if isinstance(conds, (list, tuple)):
            for item in conds:
                exprs.extend(self._normalize_where(item))
            return exprs
        raise TypeError(f"Unsupported traversal filter: {conds!r}")

    def _run(self, *, limit: int, offset: int) -> dict[str, Any]:
        where_payload = _serialize_where(self._where_exprs)
        kwargs = {
            "where": where_payload,
            "order_by": list(self._order_specs),
            "limit": int(limit),
            "offset": int(offset),
        }
        if self._traverse_steps:
            kwargs["traverse"] = list(self._traverse_steps)
        return self._client.search_objects(self._object_type, **kwargs)

    def _build_object(self, data: dict[str, Any]):
        if self._object_cls is None:
            raise ValueError("Object class not provided for typed results")
        return self._object_cls.from_response(self._client, data)


def _serialize_where(exprs: Iterable[Expr]) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for expr in exprs:
        payload.extend(expr.to_filters())
    return payload
