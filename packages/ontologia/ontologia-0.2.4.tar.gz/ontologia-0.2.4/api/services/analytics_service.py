"""
services/analytics_service.py
-----------------------------
Minimal analytics service for aggregate queries over object instances.
First version operates in SQL fallback (in-memory) and supports COUNT/SUM/AVG
with optional groupBy. Graph-backed Cypher path can be added later.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from fastapi import HTTPException
from sqlmodel import Session

from api.core.auth import UserPrincipal
from api.repositories.graph_instances_repository import GraphInstancesRepository
from api.repositories.kuzudb_repository import get_kuzu_repo
from api.v2.schemas.search import AggregateRequest, AggregateResponse, AggregateRow
from ontologia.config import use_graph_reads_enabled, use_unified_graph_enabled
from ontologia.domain.instances.repositories import ObjectInstanceRepository
from ontologia.domain.metamodel.repositories import (
    MetamodelRepository as MetamodelRepositoryProtocol,
)
from ontologia.infrastructure.persistence.sql.instances_repository import (
    SQLObjectInstanceRepository,
)
from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(
        self,
        session: Session,
        service: str = "ontology",
        instance: str = "default",
        principal: UserPrincipal | None = None,
        repo: ObjectInstanceRepository | None = None,
        metamodel_repo: MetamodelRepositoryProtocol | None = None,
    ):
        self.session = session
        self.service = service
        self.instance = instance
        self.repo = repo or SQLObjectInstanceRepository(session)
        self.metamodel_repo = metamodel_repo or SQLMetamodelRepository(session)
        self._use_graph_flag = use_graph_reads_enabled()
        self.kuzu_repo = get_kuzu_repo()
        self.principal = principal

    def _use_graph_reads(self) -> bool:
        try:
            return bool(self._use_graph_flag and self.kuzu_repo and self.kuzu_repo.is_available())
        except Exception:
            return False

    def aggregate(self, body: AggregateRequest) -> AggregateResponse:
        ot = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, body.objectTypeApiName
        )
        if not ot or not ot.primary_key_field:
            raise HTTPException(
                status_code=400,
                detail=f"ObjectType '{body.objectTypeApiName}' not found or missing PK",
            )

        # Graph-backed path when enabled
        if self._use_graph_reads():
            # Unified graph path: properties stored as JSON in Object; aggregate in-memory
            if use_unified_graph_enabled():
                try:
                    graph_repo = GraphInstancesRepository(session=self.session)
                    rows = graph_repo.list_by_type(ot.api_name, limit=10_000, offset=0)

                    # Filter
                    def match(props: dict[str, Any]) -> bool:
                        for cond in body.where or []:
                            name, op, val = cond.property, cond.op, cond.value
                            v = props.get(name)
                            if op == "eq" and v != val:
                                return False
                            if op == "ne" and v == val:
                                return False
                            if op == "gt":
                                try:
                                    if not (v > val):
                                        return False
                                except Exception:
                                    return False
                            if op == "gte":
                                try:
                                    if not (v >= val):
                                        return False
                                except Exception:
                                    return False
                            if op == "lt":
                                try:
                                    if not (v < val):
                                        return False
                                except Exception:
                                    return False
                            if op == "lte":
                                try:
                                    if not (v <= val):
                                        return False
                                except Exception:
                                    return False
                            if op == "contains":
                                if str(val).lower() not in str(v).lower():
                                    return False
                            if op == "in":
                                if v not in set(
                                    val if isinstance(val, (list, tuple, set)) else [val]
                                ):
                                    return False
                        return True

                    filtered = [
                        dict(r.get("properties", {}))
                        for r in rows
                        if match(dict(r.get("properties", {})))
                    ]
                    # Group
                    groups: dict[tuple, list[dict]] = defaultdict(list)
                    if body.groupBy:
                        for props in filtered:
                            key = tuple(props.get(g) for g in body.groupBy)
                            groups[key].append(props)
                    else:
                        groups[tuple()].extend(filtered)
                    # Aggregate
                    rows_out: list[AggregateRow] = []
                    for key, bucket in groups.items():
                        group_map: dict[str, Any] = {}
                        if body.groupBy:
                            group_map = {g: key[idx] for idx, g in enumerate(body.groupBy)}
                        metrics_map: dict[str, float | int] = {}
                        for spec in body.metrics or []:
                            if spec.func == "count":
                                metrics_map["count"] = len(bucket)
                            elif spec.func == "sum" and spec.property:
                                s = 0.0
                                for b in bucket:
                                    v = b.get(spec.property)
                                    try:
                                        s += float(v)
                                    except Exception:
                                        pass
                                metrics_map[f"sum({spec.property})"] = s
                            elif spec.func == "avg" and spec.property:
                                vals: list[float] = []
                                for b in bucket:
                                    v = b.get(spec.property)
                                    try:
                                        vals.append(float(v))
                                    except Exception:
                                        pass
                                metrics_map[f"avg({spec.property})"] = (
                                    (sum(vals) / len(vals)) if vals else 0.0
                                )
                        rows_out.append(AggregateRow(group=group_map, metrics=metrics_map))
                    return AggregateResponse(rows=rows_out)
                except Exception:
                    # Fallback to legacy graph path/SQL below
                    pass
            try:
                label = ot.api_name
                # WHERE
                where_parts: list[str] = []
                for cond in body.where or []:
                    prop = f"o.`{cond.property}`"
                    op = str(cond.op)
                    val = cond.value
                    if op == "eq":
                        where_parts.append(f"{prop} = {self._lit(val)}")
                    elif op == "ne":
                        where_parts.append(f"{prop} <> {self._lit(val)}")
                    elif op == "lt":
                        where_parts.append(f"{prop} < {self._lit(val)}")
                    elif op == "lte":
                        where_parts.append(f"{prop} <= {self._lit(val)}")
                    elif op == "gt":
                        where_parts.append(f"{prop} > {self._lit(val)}")
                    elif op == "gte":
                        where_parts.append(f"{prop} >= {self._lit(val)}")
                    elif op == "contains":
                        s = str(val) if val is not None else ""
                        where_parts.append(f"LOWER({prop}) CONTAINS LOWER({self._lit(s)})")
                    elif op == "in":
                        if isinstance(val, (list, tuple)):
                            arr = ", ".join(self._lit(v) for v in val)
                            where_parts.append(f"{prop} IN [{arr}]")
                where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

                # RETURN clauses
                group_aliases: list[tuple[str, str]] = []  # (prop, alias)
                if body.groupBy:
                    for g in body.groupBy:
                        alias = f"g_{g}"
                        group_aliases.append((g, alias))
                metric_aliases: list[tuple[str, str]] = []
                metric_parts: list[str] = []
                for spec in body.metrics or []:
                    if spec.func == "count":
                        metric_aliases.append(("count", "m_count"))
                        metric_parts.append("count(*) AS m_count")
                    elif spec.func == "sum" and spec.property:
                        alias = f"m_sum_{spec.property}"
                        metric_aliases.append((f"sum({spec.property})", alias))
                        metric_parts.append(f"sum(toFloat(o.`{spec.property}`)) AS {alias}")
                    elif spec.func == "avg" and spec.property:
                        alias = f"m_avg_{spec.property}"
                        metric_aliases.append((f"avg({spec.property})", alias))
                        metric_parts.append(f"avg(toFloat(o.`{spec.property}`)) AS {alias}")

                group_parts = [f"o.`{g}` AS {alias}" for (g, alias) in group_aliases]
                return_parts = []
                if group_parts:
                    return_parts.extend(group_parts)
                if metric_parts:
                    return_parts.extend(metric_parts)
                else:
                    # default to count if no metrics specified
                    metric_aliases.append(("count", "m_count"))
                    return_parts.append("count(*) AS m_count")

                query = f"MATCH (o:`{label}`){where_sql} RETURN " + ", ".join(return_parts)
                logger.info("analytics.graph.query %s", query)
                res = self.kuzu_repo.execute(query)
                try:
                    df = res.get_as_df()  # type: ignore[attr-defined]
                    if df is None:
                        raise RuntimeError("no dataframe")
                    rows: list[AggregateRow] = []
                    for _, row in df.iterrows():
                        group_map: dict[str, Any] = {}
                        for g, alias in group_aliases:
                            group_map[g] = row.get(alias)
                        metrics_map: dict[str, float | int] = {}
                        for key, alias in metric_aliases:
                            metrics_map[self._metric_key_to_name(key)] = (
                                row.get(alias) if alias in df.columns else 0
                            )
                        rows.append(AggregateRow(group=group_map, metrics=metrics_map))
                    return AggregateResponse(rows=rows)
                except Exception:
                    # fallback below
                    pass
            except Exception:
                # fallback below
                pass

        # SQL fallback
        items = self.repo.list_object_instances(
            self.service, self.instance, object_type_api_name=ot.api_name, limit=10_000, offset=0
        )

        # Simple where filter (reuse logic inline)
        def match(props: dict[str, Any]) -> bool:
            for cond in body.where or []:
                name, op, val = cond.property, cond.op, cond.value
                v = props.get(name)
                if op == "eq" and v != val:
                    return False
                if op == "ne" and v == val:
                    return False
                if op == "gt":
                    try:
                        if not (v > val):
                            return False
                    except Exception:
                        return False
                if op == "gte":
                    try:
                        if not (v >= val):
                            return False
                    except Exception:
                        return False
                if op == "lt":
                    try:
                        if not (v < val):
                            return False
                    except Exception:
                        return False
                if op == "lte":
                    try:
                        if not (v <= val):
                            return False
                    except Exception:
                        return False
                if op == "contains":
                    if str(val).lower() not in str(v).lower():
                        return False
                if op == "in":
                    if v not in set(val if isinstance(val, (list, tuple, set)) else [val]):
                        return False
            return True

        filtered = [dict(i.data or {}) for i in items if match(dict(i.data or {}))]

        # Group and aggregate
        groups: dict[tuple, list[dict]] = defaultdict(list)
        if body.groupBy:
            for props in filtered:
                key = tuple(props.get(g) for g in body.groupBy)
                groups[key].append(props)
        else:
            groups[tuple()].extend(filtered)

        rows: list[AggregateRow] = []
        for key, bucket in groups.items():
            group_map: dict[str, Any] = {}
            if body.groupBy:
                group_map = {g: key[idx] for idx, g in enumerate(body.groupBy)}
            metrics_map: dict[str, float | int] = {}
            for spec in body.metrics or []:
                if spec.func == "count":
                    metrics_map["count"] = len(bucket)
                elif spec.func == "sum" and spec.property:
                    s = 0.0
                    for b in bucket:
                        v = b.get(spec.property)
                        try:
                            s += float(v)
                        except Exception:
                            pass
                    metrics_map[f"sum({spec.property})"] = s
                elif spec.func == "avg" and spec.property:
                    vals: list[float] = []
                    for b in bucket:
                        v = b.get(spec.property)
                        try:
                            vals.append(float(v))
                        except Exception:
                            pass
                    metrics_map[f"avg({spec.property})"] = (sum(vals) / len(vals)) if vals else 0.0
            rows.append(AggregateRow(group=group_map, metrics=metrics_map))
        return AggregateResponse(rows=rows)

    # Helpers
    def _lit(self, value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        s = str(value).replace("'", "''")
        return f"'{s}'"

    def _metric_key_to_name(self, key: str) -> str:
        # key is like 'count', 'sum(prop)', 'avg(prop)'
        return key
