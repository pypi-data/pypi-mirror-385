"""Hybrid query planner coordinating relational and graph traversals."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session

from api.core.auth import UserPrincipal
from api.services.instances_service import InstancesService
from api.v2.schemas.instances import ObjectListResponse, ObjectReadResponse
from api.v2.schemas.search import ObjectSearchRequest, TraversalStep, WhereCondition


class HybridQueryService:
    """Executes multi-hop queries that span relational storage and link traversals."""

    def __init__(
        self,
        session: Session,
        *,
        service: str,
        instance: str,
        principal: UserPrincipal | None = None,
        cache_ttl: float = 30.0,
    ) -> None:
        self._session = session
        self._service = service
        self._instance = instance
        self._principal = principal
        self._cache_ttl = max(0.0, cache_ttl)
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._instances = InstancesService(
            session,
            service=service,
            instance=instance,
            principal=principal,
        )
        self._logger = logging.getLogger(__name__)

    def search(self, object_type_api_name: str, request: ObjectSearchRequest) -> ObjectListResponse:
        if not request.traverse:
            return self._instances.search_objects_base(object_type_api_name, request)

        cache_key = self._cache_key(object_type_api_name, request)
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached[0]) <= self._cache_ttl:
            return ObjectListResponse.model_validate(cached[1])

        base_request = request.model_copy(update={"traverse": []})
        base_result = self._instances.search_objects_base(object_type_api_name, base_request)
        traversed = self._apply_traversals(
            base_result.data,
            request.traverse,
            as_of=getattr(request, "asOf", None),
        )

        limit = int(request.limit or 100)
        if limit > 0:
            traversed = traversed[:limit]

        response = ObjectListResponse(data=traversed)
        self._logger.debug(
            "hybrid_query.plan",
            extra={
                "service": self._service,
                "instance": self._instance,
                "objectType": object_type_api_name,
                "traverseDepth": len(request.traverse),
                "resultSize": len(traversed),
            },
        )
        if self._cache_ttl > 0:
            self._cache[cache_key] = (time.time(), response.model_dump(mode="json"))
        return response

    def _cache_key(self, object_type: str, request: ObjectSearchRequest) -> str:
        payload = request.model_dump(mode="json")
        return json.dumps({"objectType": object_type, "request": payload}, sort_keys=True)

    def _apply_traversals(
        self,
        base_objects: list[ObjectReadResponse],
        steps: list[TraversalStep],
        *,
        as_of: datetime | None = None,
    ) -> list[ObjectReadResponse]:
        current = list(base_objects)
        for step in steps:
            if step.direction and step.direction.lower() != "forward":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Traversal direction '{step.direction}' not supported",
                )
            next_hop: list[ObjectReadResponse] = []
            for obj in current:
                hop = self._instances.get_linked_objects(
                    obj.objectTypeApiName,
                    obj.pkValue,
                    step.link,
                    limit=int(step.limit or 100),
                    offset=0,
                    valid_at=as_of,
                )
                filtered = self._filter_objects(hop.data, step.where)
                next_hop.extend(filtered)
            current = next_hop
        return current

    def _filter_objects(
        self, objects: list[ObjectReadResponse], where: list[WhereCondition]
    ) -> list[ObjectReadResponse]:
        if not where:
            return objects
        return [obj for obj in objects if self._matches_all(obj, where)]

    def _matches_all(self, obj: ObjectReadResponse, where: list[WhereCondition]) -> bool:
        props = obj.properties or {}
        for cond in where:
            if not self._match(props, cond):
                return False
        return True

    def _match(self, props: dict[str, Any], cond: WhereCondition) -> bool:
        name = cond.property
        op = cond.op
        val = cond.value
        v = props.get(name)

        if op == "eq":
            return v == val
        if op == "ne":
            return v != val
        if op == "lt":
            try:
                return v < val
            except Exception:
                return False
        if op == "lte":
            try:
                return v <= val
            except Exception:
                return False
        if op == "gt":
            try:
                return v > val
            except Exception:
                return False
        if op == "gte":
            try:
                return v >= val
            except Exception:
                return False
        if op == "contains":
            if v is None:
                return False
            return str(val).lower() in str(v).lower()
        if op == "in":
            if not isinstance(val, (list, tuple, set)):
                return False
            return v in set(val)
        if op == "isnull":
            return v is None
        if op == "isnotnull":
            return v is not None
        if op == "between":
            if not (isinstance(val, (list, tuple)) and len(val) == 2):
                return False
            lo, hi = val[0], val[1]
            try:
                return v >= lo and v <= hi
            except Exception:
                return False
        if op == "startswith":
            if v is None:
                return False
            return str(v).lower().startswith(str(val).lower())
        if op == "endswith":
            if v is None:
                return False
            return str(v).lower().endswith(str(val).lower())
        return False
