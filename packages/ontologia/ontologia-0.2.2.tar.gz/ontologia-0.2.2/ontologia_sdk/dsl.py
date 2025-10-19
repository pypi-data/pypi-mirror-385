from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

_OP_EQ = "eq"
_OP_NE = "ne"
_OP_GT = "gt"
_OP_GTE = "ge"
_OP_LT = "lt"
_OP_LTE = "le"
_OP_IN = "in"


class Expr:
    """Boolean expression that can be serialized into search payload structures."""

    def __init__(self, *, op: str, operands: Sequence[Any]):
        self._op = op
        self._operands = list(operands)

    def __and__(self, other: Any) -> Expr:
        return combine("and", self, other)

    def __or__(self, other: Any) -> Expr:
        return combine("or", self, other)

    def to_filters(self) -> list[dict[str, Any]]:
        if self._op == "leaf":
            operand = self._operands[0]
            return [dict(operand)]
        if self._op == "and":
            filters: list[dict[str, Any]] = []
            for child in self._operands:
                filters.extend(as_expr(child).to_filters())
            return filters
        if self._op == "or":
            serialized = [as_expr(child).to_filters() for child in self._operands]
            return [{"op": "or", "filters": _flatten(serialized)}]
        raise ValueError(f"Unsupported op: {self._op}")

    def to_order_spec(self) -> dict[str, Any]:
        if self._op != "order":
            raise ValueError("Not an order expression")
        return dict(self._operands[0])


def _flatten(items: Iterable[Iterable[dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for chunk in items:
        out.extend(chunk)
    return out


def as_expr(value: Any) -> Expr:
    if isinstance(value, Expr):
        return value
    if isinstance(value, Mapping):
        return Expr(op="leaf", operands=[value])
    raise TypeError(f"Cannot convert {value!r} to Expr")


def combine(op: str, left: Any, right: Any) -> Expr:
    lhs = as_expr(left)
    rhs = as_expr(right)
    if lhs._op == op:
        operands = list(lhs._operands)
    else:
        operands = [lhs]
    if rhs._op == op:
        operands.extend(rhs._operands)
    else:
        operands.append(rhs)
    return Expr(op=op, operands=operands)


class FieldDescriptor:
    """Descriptor available on generated classes for fluent query building."""

    def __init__(
        self, object_type: str, property_name: str, metadata: dict[str, Any] | None = None
    ):
        self.object_type = object_type
        self.property_name = property_name
        self.metadata = dict(metadata or {})

    def __eq__(self, other: Any) -> Expr:  # type: ignore[override]
        return Expr(op="leaf", operands=[_leaf(self.property_name, _OP_EQ, other)])

    def __ne__(self, other: Any) -> Expr:  # type: ignore[override]
        return Expr(op="leaf", operands=[_leaf(self.property_name, _OP_NE, other)])

    def __gt__(self, other: Any) -> Expr:
        return Expr(op="leaf", operands=[_leaf(self.property_name, _OP_GT, other)])

    def __ge__(self, other: Any) -> Expr:
        return Expr(op="leaf", operands=[_leaf(self.property_name, _OP_GTE, other)])

    def __lt__(self, other: Any) -> Expr:
        return Expr(op="leaf", operands=[_leaf(self.property_name, _OP_LT, other)])

    def __le__(self, other: Any) -> Expr:
        return Expr(op="leaf", operands=[_leaf(self.property_name, _OP_LTE, other)])

    def isin(self, values: Sequence[Any]) -> Expr:
        return Expr(op="leaf", operands=[_leaf(self.property_name, _OP_IN, list(values))])

    def asc(self) -> Expr:
        return Expr(op="order", operands=[{"property": self.property_name, "direction": "asc"}])

    def desc(self) -> Expr:
        return Expr(op="order", operands=[{"property": self.property_name, "direction": "desc"}])


def _leaf(prop: str, op: str, value: Any) -> dict[str, Any]:
    return {"property": prop, "op": op, "value": value}
