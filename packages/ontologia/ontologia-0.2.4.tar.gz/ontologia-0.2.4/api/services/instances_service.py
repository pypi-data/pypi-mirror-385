"""
services/instances_service.py
------------------------------
Camada de serviço para lógica de negócio das instâncias (Objects).
"""

import ast
import logging
from collections.abc import Callable
from datetime import date, datetime
from time import perf_counter
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session

from api.core.auth import UserPrincipal
from api.repositories.graph_instances_repository import GraphInstancesRepository
from api.repositories.kuzudb_repository import get_kuzu_repo
from api.v2.schemas.bulk import ObjectBulkLoadRequest
from api.v2.schemas.instances import (
    ObjectListResponse,
    ObjectReadResponse,
    ObjectUpsertRequest,
)
from api.v2.schemas.search import ObjectSearchRequest
from ontologia.config import use_graph_reads_enabled
from ontologia.domain.change_sets.models_sql import ChangeSet
from ontologia.domain.events import DomainEventBus, NullEventBus
from ontologia.domain.instances.events import ObjectInstanceDeleted, ObjectInstanceUpserted
from ontologia.domain.instances.repositories import ObjectInstanceRepository
from ontologia.domain.metamodel.aggregates import ObjectTypeAggregate
from ontologia.domain.metamodel.repositories import (
    MetamodelRepository as MetamodelRepositoryProtocol,
)
from ontologia.domain.metamodels.instances.dtos import ObjectInstanceDTO
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.infrastructure.persistence.sql.instances_repository import (
    SQLObjectInstanceRepository,
)
from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository,
)

logger = logging.getLogger(__name__)


class _InstancesServiceBase:
    def __init__(
        self,
        *,
        session: Session,
        service: str,
        instance: str,
        repo: ObjectInstanceRepository,
        metamodel_repo: MetamodelRepositoryProtocol,
        graph_repo: GraphInstancesRepository | None,
        kuzu_repo,
        principal: UserPrincipal | None,
        event_bus: DomainEventBus,
        use_graph_reads: Callable[[], bool] | None = None,
        use_graph_writes: Callable[[], bool] | None = None,
    ) -> None:
        self.session = session
        self.service = service
        self.instance = instance
        self.repo = repo
        self.metamodel_repo = metamodel_repo
        self.graph_repo = graph_repo
        self.kuzu_repo = kuzu_repo
        self.principal = principal
        self._event_bus = event_bus
        self._use_graph_reads = use_graph_reads or (lambda: False)
        self._use_graph_writes = use_graph_writes or (lambda: False)
        self._change_set_cache: dict[str, dict[str, Any]] = {}

    def _object_type_aggregate(self, object_type_api_name: str) -> ObjectTypeAggregate:
        ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, object_type_api_name
        )
        if not ot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ObjectType '{object_type_api_name}' not found",
            )
        if not ot.primary_key_field:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ObjectType '{object_type_api_name}' has no primary key configured",
            )
        return ObjectTypeAggregate.from_model(ot)

    def _to_object_response(self, inst: ObjectInstance) -> ObjectReadResponse:
        props = dict(inst.data or {})
        try:
            self._apply_derivations(inst.object_type_api_name, props)
        except Exception:
            pass
        return ObjectReadResponse(
            rid=inst.rid,
            objectTypeApiName=inst.object_type_api_name,
            pkValue=inst.pk_value,
            properties=props,
        )

    def _to_object_dto(self, inst: ObjectInstance) -> ObjectInstanceDTO:
        return ObjectInstanceDTO.from_model(inst)

    def _apply_derivations(self, object_type_api_name: str, props: dict[str, Any]) -> None:
        ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, object_type_api_name
        )
        if not ot:
            return
        for p in getattr(ot, "property_types", []) or []:
            script = getattr(p, "derivation_script", None)
            if script:
                val = self._safe_eval_derivation(str(script), props)
                if val is not None:
                    props[p.api_name] = val

    def _safe_eval_derivation(self, expr: str, props: dict[str, Any]) -> Any:
        try:
            tree = ast.parse(expr, mode="eval")
        except Exception:
            return None

        def eval_node(node):
            if isinstance(node, ast.Expression):
                return eval_node(node.body)
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.Name):
                if node.id == "props":
                    return props
                return None
            if isinstance(node, ast.Subscript):
                base = eval_node(node.value)
                key = eval_node(node.slice) if not isinstance(node.slice, ast.Slice) else None
                try:
                    return base[key]
                except Exception:
                    return None
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd, ast.Not)):
                v = eval_node(node.operand)
                try:
                    if isinstance(node.op, ast.USub):
                        return -v
                    if isinstance(node.op, ast.UAdd):
                        return +v
                    return not bool(v)
                except Exception:
                    return None
            if isinstance(node, ast.BinOp) and isinstance(
                node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)
            ):
                left_val = eval_node(node.left)
                right_val = eval_node(node.right)
                try:
                    if isinstance(node.op, ast.Add):
                        return left_val + right_val
                    if isinstance(node.op, ast.Sub):
                        return left_val - right_val
                    if isinstance(node.op, ast.Mult):
                        return left_val * right_val
                    return left_val / right_val
                except Exception:
                    return None
            if isinstance(node, ast.BoolOp):
                vals = [bool(eval_node(v)) for v in node.values]
                if isinstance(node.op, ast.And):
                    return all(vals)
                if isinstance(node.op, ast.Or):
                    return any(vals)
                return None
            if isinstance(node, ast.Compare):
                left = eval_node(node.left)
                for op, comp in zip(node.ops, node.comparators, strict=False):
                    right = eval_node(comp)
                    try:
                        if isinstance(op, ast.Eq) and not (left == right):
                            return False
                        if isinstance(op, ast.NotEq) and not (left != right):
                            return False
                        if isinstance(op, ast.Lt) and not (left < right):
                            return False
                        if isinstance(op, ast.LtE) and not (left <= right):
                            return False
                        if isinstance(op, ast.Gt) and not (left > right):
                            return False
                        if isinstance(op, ast.GtE) and not (left >= right):
                            return False
                    except Exception:
                        return False
                    left = right
                return True
            if isinstance(node, ast.IfExp):
                cond = eval_node(node.test)
                return eval_node(node.body) if cond else eval_node(node.orelse)
            return None

        try:
            return eval_node(tree)
        except Exception:
            return None

    def _parse_validity_timestamp(self, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        try:
            text = str(value).strip()
            if not text:
                return None
            return datetime.fromisoformat(text)
        except Exception:
            return None

    def _is_valid_at(self, properties: dict[str, Any], as_of: datetime | None) -> bool:
        if as_of is None:
            return True
        start_raw = (
            properties.get("valid_from")
            or properties.get("validFrom")
            or properties.get("__valid_from")
        )
        end_raw = (
            properties.get("valid_to") or properties.get("validTo") or properties.get("__valid_to")
        )
        start = self._parse_validity_timestamp(start_raw)
        end = self._parse_validity_timestamp(end_raw)
        if start and as_of < start:
            return False
        if end and as_of >= end:
            return False
        return True

    def _apply_object_validity_filter(
        self, objects: list[ObjectReadResponse], as_of: datetime | None
    ) -> list[ObjectReadResponse]:
        if as_of is None:
            return objects
        filtered: list[ObjectReadResponse] = []
        for obj in objects:
            props = dict(obj.properties or {})
            if self._is_valid_at(props, as_of):
                filtered.append(obj)
        return filtered

    def _kuzu_literal(self, value):
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        s = str(value).replace("'", "''")
        return f"'{s}'"


class ObjectInstanceCommandService(_InstancesServiceBase):
    def upsert_object(
        self,
        object_type_api_name: str,
        pk_value: str,
        body: ObjectUpsertRequest,
    ) -> ObjectReadResponse:
        instance, _ = self._upsert_instance(object_type_api_name, pk_value, body)
        return self._to_object_response(instance)

    def upsert_object_dto(
        self,
        object_type_api_name: str,
        pk_value: str,
        body: ObjectUpsertRequest,
    ) -> ObjectInstanceDTO:
        instance, _ = self._upsert_instance(object_type_api_name, pk_value, body)
        return self._to_object_dto(instance)

    def delete_object(self, object_type_api_name: str, pk_value: str) -> bool:
        pk_field = ""
        try:
            aggregate = self._object_type_aggregate(object_type_api_name)
            pk_field = aggregate.object_type.primary_key_field or ""
        except HTTPException:
            pk_field = ""
        ok = self.repo.delete_object_instance(
            self.service, self.instance, object_type_api_name, pk_value
        )
        if ok:
            try:
                self._event_bus.publish(
                    ObjectInstanceDeleted(
                        service=self.service,
                        instance=self.instance,
                        object_type_api_name=object_type_api_name,
                        primary_key_field=pk_field,
                        primary_key_value=str(pk_value),
                    )
                )
            except Exception:
                pass
        return ok

    def bulk_load_objects(
        self, object_type_api_name: str, body: ObjectBulkLoadRequest
    ) -> ObjectListResponse:
        aggregate = self._object_type_aggregate(object_type_api_name)
        responses: list[ObjectReadResponse] = []
        for item in body.items or []:
            instance, normalized = self._upsert_instance(
                object_type_api_name,
                item.pk,
                ObjectUpsertRequest(properties=dict(item.properties or {})),
                aggregate=aggregate,
            )
            responses.append(self._to_object_response(instance))
        return ObjectListResponse(data=responses)

    def _upsert_instance(
        self,
        object_type_api_name: str,
        pk_value: str,
        body: ObjectUpsertRequest,
        *,
        aggregate: ObjectTypeAggregate | None = None,
    ) -> tuple[ObjectInstance, dict[str, Any]]:
        agg = aggregate or self._object_type_aggregate(object_type_api_name)
        try:
            normalized = agg.normalize_instance_properties(pk_value, dict(body.properties or {}))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        existing = self.repo.get_object_instance(
            self.service, self.instance, object_type_api_name, pk_value
        )
        if existing:
            inst = existing
            inst.data = normalized
        else:
            inst = ObjectInstance(
                service=self.service,
                instance=self.instance,
                api_name=f"{object_type_api_name}_{pk_value}",
                display_name=f"{object_type_api_name}:{pk_value}",
                object_type_api_name=object_type_api_name,
                object_type_rid=agg.object_type.rid,
                pk_value=str(pk_value),
                data=normalized,
            )
            self.session.add(inst)

        saved = self.repo.save_object_instance(inst)
        try:
            self._event_bus.publish(
                ObjectInstanceUpserted(
                    service=self.service,
                    instance=self.instance,
                    object_type_api_name=object_type_api_name,
                    primary_key_field=agg.object_type.primary_key_field,
                    primary_key_value=str(pk_value),
                    payload=dict(normalized),
                )
            )
        except Exception:
            pass
        return saved, dict(normalized)


class ObjectInstanceQueryService(_InstancesServiceBase):
    def _change_set_cache_key(self, object_type_api_name: str | None, change_set_rid: str) -> str:
        name = object_type_api_name or "__all__"
        return f"{name}:{change_set_rid}"

    def _load_change_set(
        self, object_type_api_name: str | None, change_set_rid: str | None
    ) -> dict[str, Any]:
        if not change_set_rid:
            return {
                "updates": {},
                "creates": {},
                "deletes": set(),
                "defaultObjectType": object_type_api_name,
            }
        key = self._change_set_cache_key(object_type_api_name, change_set_rid)
        cached = self._change_set_cache.get(key)
        if cached is not None:
            return cached

        change_set = self.session.get(ChangeSet, change_set_rid)
        if (
            not change_set
            or change_set.service != self.service
            or change_set.instance != self.instance
        ):
            data = {
                "updates": {},
                "creates": {},
                "deletes": set(),
                "defaultObjectType": object_type_api_name,
            }
            self._change_set_cache[key] = data
            return data

        payload_changes = list(change_set.payload.get("changes", []))
        updates: dict[str, dict[str, Any]] = {}
        creates: dict[str, dict[str, Any]] = {}
        deletes: set[str] = set()

        for entry in payload_changes:
            if not isinstance(entry, dict):
                continue
            target_type = entry.get("objectType") or change_set.target_object_type
            if object_type_api_name and target_type != object_type_api_name:
                continue
            pk_val = entry.get("pk")
            op = entry.get("op")
            props = entry.get("properties", {})
            if not isinstance(pk_val, str) or not op:
                continue
            if op in {"update", "upsert"}:
                updates[str(pk_val)] = dict(props or {})
                deletes.discard(str(pk_val))
            elif op == "create":
                creates[str(pk_val)] = dict(props or {})
                deletes.discard(str(pk_val))
            elif op == "delete":
                deletes.add(str(pk_val))
                updates.pop(str(pk_val), None)
                creates.pop(str(pk_val), None)

        data = {
            "updates": updates,
            "creates": creates,
            "deletes": deletes,
            "defaultObjectType": object_type_api_name or change_set.target_object_type,
        }
        self._change_set_cache[key] = data
        return data

    def _lookup_change_set_update(
        self, object_type_api_name: str, pk_value: str, change_set_rid: str | None
    ) -> dict[str, Any] | None:
        overlay = self._load_change_set(object_type_api_name, change_set_rid)
        if pk_value in overlay["deletes"]:
            return None
        if pk_value in overlay["creates"]:
            return overlay["creates"][pk_value]
        if pk_value in overlay["updates"]:
            return overlay["updates"][pk_value]
        return None

    def _apply_overlay_to_properties(
        self,
        object_type_api_name: str,
        pk_value: str,
        base_props: dict[str, Any],
        overlay: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        if pk_value in overlay.get("deletes", set()):
            return base_props, True
        if pk_value in overlay.get("updates", {}):
            merged = self._merge_overlay_properties(base_props, overlay["updates"][pk_value])
            return merged, False
        return base_props, False

    def _merge_overlay_properties(
        self, base_props: dict[str, Any], overlay_props: dict[str, Any]
    ) -> dict[str, Any]:
        merged = dict(base_props)
        for key, value in overlay_props.items():
            merged[key] = value
        return merged

    def _apply_change_set_overlay_list(
        self,
        object_type_api_name: str | None,
        responses: list[ObjectReadResponse],
        overlay: dict[str, Any],
    ) -> list[ObjectReadResponse]:
        updated: list[ObjectReadResponse] = []
        deletes = overlay.get("deletes", set())
        updates = overlay.get("updates", {})
        creates = overlay.get("creates", {})
        for resp in responses:
            pk_val = str(resp.pkValue)
            if pk_val in deletes:
                continue
            props = dict(resp.properties or {})
            if pk_val in updates:
                props = self._merge_overlay_properties(props, updates[pk_val])
            updated.append(
                ObjectReadResponse(
                    rid=resp.rid,
                    objectTypeApiName=resp.objectTypeApiName,
                    pkValue=resp.pkValue,
                    properties=props,
                )
            )

        ot_api = object_type_api_name or overlay.get("defaultObjectType") or ""
        for pk_val, props in creates.items():
            updated.append(
                ObjectReadResponse(
                    rid=f"{ot_api}:{pk_val}",
                    objectTypeApiName=ot_api,
                    pkValue=str(pk_val),
                    properties=dict(props),
                )
            )
        return updated

    def get_object(
        self,
        object_type_api_name: str,
        pk_value: str,
        *,
        as_of: datetime | None = None,
        change_set_rid: str | None = None,
    ) -> ObjectReadResponse | None:
        ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, object_type_api_name
        )
        if not ot or not ot.primary_key_field:
            return None
        item = (
            self.graph_repo.get_by_pk(object_type_api_name, ot.primary_key_field, pk_value)
            if self.graph_repo
            else None
        )
        if item:
            props = dict(item.get("properties", {}))
            if change_set_rid:
                overlay_data = self._load_change_set(object_type_api_name, change_set_rid)
                props, _ = self._apply_overlay_to_properties(
                    object_type_api_name,
                    pk_value,
                    props,
                    overlay_data,
                )
            try:
                self._apply_derivations(object_type_api_name, props)
            except Exception:
                pass
            response = ObjectReadResponse(
                rid=f"{object_type_api_name}:{pk_value}",
                objectTypeApiName=item["objectTypeApiName"],
                pkValue=str(pk_value),
                properties=props,
            )
            if self._is_valid_at(props, as_of):
                return response
            return None
        inst = self.repo.get_object_instance(
            self.service, self.instance, object_type_api_name, pk_value
        )
        overlay_data = (
            self._load_change_set(object_type_api_name, change_set_rid) if change_set_rid else None
        )
        if not inst:
            if not overlay_data:
                return None
            props = overlay_data["creates"].get(pk_value) or overlay_data["updates"].get(pk_value)
            if props is None or pk_value in overlay_data["deletes"]:
                return None
            resp = ObjectReadResponse(
                rid=f"{object_type_api_name}:{pk_value}",
                objectTypeApiName=object_type_api_name,
                pkValue=str(pk_value),
                properties=dict(props),
            )
            if self._is_valid_at(dict(resp.properties or {}), as_of):
                return resp
            return None
        resp = self._to_object_response(inst)
        if overlay_data:
            merged_props, deleted = self._apply_overlay_to_properties(
                object_type_api_name,
                pk_value,
                dict(resp.properties or {}),
                overlay_data,
            )
            if deleted:
                return None
            resp = ObjectReadResponse(
                rid=resp.rid,
                objectTypeApiName=resp.objectTypeApiName,
                pkValue=resp.pkValue,
                properties=merged_props,
            )
        if self._is_valid_at(dict(resp.properties or {}), as_of):
            return resp
        return None

    def get_object_dto(self, object_type_api_name: str, pk_value: str) -> ObjectInstanceDTO | None:
        inst = self.repo.get_object_instance(
            self.service, self.instance, object_type_api_name, pk_value
        )
        if not inst:
            return None
        return self._to_object_dto(inst)

    def list_objects(
        self,
        object_type_api_name: str | None = None,
        *,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
        change_set_rid: str | None = None,
    ) -> ObjectListResponse:
        if object_type_api_name:
            ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
                self.service, self.instance, object_type_api_name
            )
            if ot and ot.primary_key_field and self.graph_repo:
                rows = self.graph_repo.list_by_type(
                    object_type_api_name, limit=limit, offset=offset
                )
                data: list[ObjectReadResponse] = []
                for row in rows:
                    props = dict(row.get("properties", {}))
                    pkv = str(props.get(ot.primary_key_field, ""))
                    if change_set_rid:
                        overlay_data = self._load_change_set(object_type_api_name, change_set_rid)
                        props, deleted = self._apply_overlay_to_properties(
                            object_type_api_name, pkv, props, overlay_data
                        )
                        if deleted:
                            continue
                    try:
                        self._apply_derivations(object_type_api_name, props)
                    except Exception:
                        pass
                    data.append(
                        ObjectReadResponse(
                            rid=f"{object_type_api_name}:{pkv}",
                            objectTypeApiName=object_type_api_name,
                            pkValue=pkv,
                            properties=props,
                        )
                    )
                filtered = self._apply_object_validity_filter(data, valid_at)
                return ObjectListResponse(data=filtered)
            try:
                itf = self.metamodel_repo.get_interface_type_by_api_name(
                    self.service, self.instance, object_type_api_name
                )
            except Exception:
                itf = None
            if itf and getattr(itf, "object_types", None) and self.graph_repo:
                rows = self.graph_repo.list_by_interface(
                    object_type_api_name, limit=limit, offset=offset
                )
                out: list[ObjectReadResponse] = []
                for row in rows:
                    ot_api = str(row.get("objectTypeApiName", ""))
                    props = dict(row.get("properties", {}))
                    pkv = str(row.get("pkValue", ""))
                    if change_set_rid:
                        overlay_data = self._load_change_set(ot_api, change_set_rid)
                        props, deleted = self._apply_overlay_to_properties(
                            ot_api, pkv, props, overlay_data
                        )
                        if deleted:
                            continue
                    try:
                        self._apply_derivations(ot_api, props)
                    except Exception:
                        pass
                    out.append(
                        ObjectReadResponse(
                            rid=f"{ot_api}:{pkv}",
                            objectTypeApiName=ot_api,
                            pkValue=pkv,
                            properties=props,
                        )
                    )
                filtered = self._apply_object_validity_filter(out, valid_at)
                return ObjectListResponse(data=filtered)

        items = self.repo.list_object_instances(
            self.service,
            self.instance,
            object_type_api_name=object_type_api_name,
            limit=limit,
            offset=offset,
        )
        responses = [self._to_object_response(i) for i in items]
        if change_set_rid:
            overlay = self._load_change_set(object_type_api_name, change_set_rid)
            responses = self._apply_change_set_overlay_list(
                object_type_api_name, responses, overlay
            )
        responses = self._apply_object_validity_filter(responses, valid_at)
        return ObjectListResponse(data=responses)

    def list_objects_dto(
        self, object_type_api_name: str | None = None, *, limit: int = 100, offset: int = 0
    ) -> list[ObjectInstanceDTO]:
        items = self.repo.list_object_instances(
            self.service,
            self.instance,
            object_type_api_name=object_type_api_name,
            limit=limit,
            offset=offset,
        )
        return [self._to_object_dto(i) for i in items]

    def search_objects(
        self,
        object_type_api_name: str,
        body: ObjectSearchRequest,
        *,
        change_set_rid: str | None = None,
    ) -> ObjectListResponse:
        as_of = getattr(body, "asOf", None)
        if getattr(body, "traverse", None):
            from api.services.query_service import HybridQueryService

            planner = HybridQueryService(
                self.session,
                service=self.service,
                instance=self.instance,
                principal=self.principal,
            )
            result = planner.search(object_type_api_name, body)
            result.data = self._apply_object_validity_filter(result.data, as_of)
            return result
        result = self.search_objects_base(object_type_api_name, body, change_set_rid=change_set_rid)
        result.data = self._apply_object_validity_filter(result.data, as_of)
        return result

    def search_objects_base(
        self,
        object_type_api_name: str,
        body: ObjectSearchRequest,
        *,
        change_set_rid: str | None = None,
    ) -> ObjectListResponse:
        limit = int(body.limit or 100)
        offset = int(body.offset or 0)
        as_of = getattr(body, "asOf", None)

        if self.graph_repo:
            try:
                itf = self.metamodel_repo.get_interface_type_by_api_name(
                    self.service, self.instance, object_type_api_name
                )
            except Exception:
                itf = None
            if itf and getattr(itf, "object_types", None):
                combined_rows: list[dict] = []
                for impl in itf.object_types:
                    if not getattr(impl, "primary_key_field", None):
                        continue
                    rows = self.graph_repo.list_by_type(impl.api_name, limit=10_000, offset=0)
                    for row in rows:
                        row_props = dict(row.get("properties", {}))
                        combined_rows.append({"impl": impl, "props": row_props})

                def match(props: dict, name: str, op: str, val: Any) -> bool:
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

                filtered_rows = []
                for entry in combined_rows:
                    props = entry["props"]
                    ok = True
                    for cond in body.where or []:
                        if not match(props, cond.property, cond.op, cond.value):
                            ok = False
                            break
                    if ok:
                        filtered_rows.append(entry)
                if body.orderBy:
                    reverse = (body.orderBy[0].direction or "asc").lower() == "desc"
                    key_name = body.orderBy[0].property
                    filtered_rows.sort(key=lambda e: e["props"].get(key_name), reverse=reverse)
                start = max(0, offset)
                end = start + max(0, limit) if limit > 0 else len(filtered_rows)
                page = filtered_rows[start:end]
                out: list[ObjectReadResponse] = []
                for entry in page:
                    impl = entry["impl"]
                    props = dict(entry["props"])
                    pk_field = getattr(impl, "primary_key_field", None)
                    pkv = str(props.get(pk_field or ""))
                    if change_set_rid:
                        overlay_data = self._load_change_set(impl.api_name, change_set_rid)
                        props, deleted = self._apply_overlay_to_properties(
                            impl.api_name, pkv, props, overlay_data
                        )
                        if deleted:
                            continue
                    try:
                        self._apply_derivations(impl.api_name, props)
                    except Exception:
                        props = dict(entry["props"])
                    out.append(
                        ObjectReadResponse(
                            rid=f"{impl.api_name}:{pkv}",
                            objectTypeApiName=impl.api_name,
                            pkValue=pkv,
                            properties=props,
                        )
                    )
                filtered = self._apply_object_validity_filter(out, as_of)
                return ObjectListResponse(data=filtered)

            ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
                self.service, self.instance, object_type_api_name
            )
            if not ot or not ot.primary_key_field:
                return ObjectListResponse(data=[])

            if self.graph_repo:
                fetch_limit = min(10_000, max(limit + offset, 100))
                rows = self.graph_repo.list_by_type(ot.api_name, limit=fetch_limit, offset=0)

                def match_local(props: dict, name: str, op: str, val: Any) -> bool:
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

                filtered_rows: list[dict] = []
                for row in rows:
                    props = dict(row.get("properties", {}))
                    ok = True
                    for cond in body.where or []:
                        if not match_local(props, cond.property, cond.op, cond.value):
                            ok = False
                            break
                    if ok:
                        filtered_rows.append({"props": props})
                if body.orderBy:
                    reverse = (body.orderBy[0].direction or "asc").lower() == "desc"
                    key_name = body.orderBy[0].property
                    filtered_rows.sort(key=lambda e: e["props"].get(key_name), reverse=reverse)
                start = max(0, offset)
                end = start + max(0, limit) if limit > 0 else len(filtered_rows)
                page = filtered_rows[start:end]
                out: list[ObjectReadResponse] = []
                for entry in page:
                    props = dict(entry["props"])
                    pkv = str(props.get(ot.primary_key_field, ""))
                    if change_set_rid:
                        overlay_data = self._load_change_set(ot.api_name, change_set_rid)
                        props, deleted = self._apply_overlay_to_properties(
                            ot.api_name, pkv, props, overlay_data
                        )
                        if deleted:
                            continue
                    try:
                        self._apply_derivations(ot.api_name, props)
                    except Exception:
                        pass
                    out.append(
                        ObjectReadResponse(
                            rid=f"{ot.api_name}:{pkv}",
                            objectTypeApiName=ot.api_name,
                            pkValue=pkv,
                            properties=props,
                        )
                    )
                filtered = self._apply_object_validity_filter(out, as_of)
                return ObjectListResponse(data=filtered)

                where_clauses: list[str] = []
                for cond in body.where or []:
                    prop = f"o.`{cond.property}`"
                    op = cond.op
                    val = cond.value
                    if op == "eq":
                        where_clauses.append(f"{prop} = {self._kuzu_literal(val)}")
                    elif op == "ne":
                        where_clauses.append(f"{prop} <> {self._kuzu_literal(val)}")
                    elif op == "lt":
                        where_clauses.append(f"{prop} < {self._kuzu_literal(val)}")
                    elif op == "lte":
                        where_clauses.append(f"{prop} <= {self._kuzu_literal(val)}")
                    elif op == "gt":
                        where_clauses.append(f"{prop} > {self._kuzu_literal(val)}")
                    elif op == "gte":
                        where_clauses.append(f"{prop} >= {self._kuzu_literal(val)}")
                    elif op == "contains":
                        s = str(val) if val is not None else ""
                        where_clauses.append(
                            f"LOWER({prop}) CONTAINS LOWER({self._kuzu_literal(s)})"
                        )
                    elif op == "in":
                        if isinstance(val, (list, tuple)):
                            arr = ", ".join(self._kuzu_literal(v) for v in val)
                            where_clauses.append(f"{prop} IN [{arr}]")
                    elif op == "isnull":
                        where_clauses.append(f"{prop} IS NULL")
                    elif op == "isnotnull":
                        where_clauses.append(f"{prop} IS NOT NULL")
                    elif op == "between":
                        if isinstance(val, (list, tuple)) and len(val) == 2:
                            lo, hi = val[0], val[1]
                            where_clauses.append(
                                f"{prop} >= {self._kuzu_literal(lo)} AND {prop} <= {self._kuzu_literal(hi)}"
                            )
                    elif op == "startswith":
                        s = str(val) if val is not None else ""
                        where_clauses.append(
                            f"LOWER({prop}) STARTS WITH LOWER({self._kuzu_literal(s)})"
                        )
                    elif op == "endswith":
                        s = str(val) if val is not None else ""
                        where_clauses.append(
                            f"LOWER({prop}) ENDS WITH LOWER({self._kuzu_literal(s)})"
                        )
                where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

                order_parts: list[str] = []
                for ob in body.orderBy or []:
                    p = f"o.`{ob.property}`"
                    d = "DESC" if (ob.direction or "asc").lower() == "desc" else "ASC"
                    order_parts.append(f"{p} {d}")
                order_sql = (" ORDER BY " + ", ".join(order_parts)) if order_parts else ""

                fetch_limit = limit + offset if offset > 0 else limit
                query = (
                    f"MATCH (o:`{ot.api_name}`){where_sql} RETURN o{order_sql} LIMIT {fetch_limit}"
                )
                try:
                    res = self.graph_repo.kuzu.execute(query)  # type: ignore[attr-defined]
                    try:
                        df = res.get_as_df()  # type: ignore[attr-defined]
                        if df is None or len(df) == 0:
                            return ObjectListResponse(data=[])
                        data: list[ObjectReadResponse] = []
                        start = offset if offset > 0 else 0
                        end = start + limit if limit > 0 else len(df)
                        for idx in range(start, min(end, len(df))):
                            row = df.iloc[idx]
                            props = {}
                            for col in df.columns:
                                if col.startswith("o."):
                                    props[col[2:]] = row[col]
                            if not props:
                                props = {col: row[col] for col in df.columns if col != "o"}
                            try:
                                self._apply_derivations(ot.api_name, props)
                            except Exception:
                                pass
                            pkv = str(props.get(ot.primary_key_field, ""))
                            data.append(
                                ObjectReadResponse(
                                    rid=f"{ot.api_name}:{pkv}",
                                    objectTypeApiName=ot.api_name,
                                    pkValue=pkv,
                                    properties=props,
                                )
                            )
                        filtered = self._apply_object_validity_filter(data, as_of)
                        return ObjectListResponse(data=filtered)
                    except Exception as e:
                        logger.debug(
                            "graph dataframe extraction failed; falling back to SQL: %s", e
                        )
                except Exception as e:
                    logger.debug("graph query failed; falling back to SQL: %s", e)

        items = self.repo.list_object_instances(
            self.service,
            self.instance,
            object_type_api_name=object_type_api_name,
            limit=10_000,
            offset=0,
        )

        def match_cond(props: dict, name: str, op: str, val: Any) -> bool:
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

        filtered = []
        for it in items:
            props = dict(it.data or {})
            try:
                self._apply_derivations(it.object_type_api_name, props)
            except Exception:
                pass
            ok = True
            for cond in body.where or []:
                if not match_cond(props, cond.property, cond.op, cond.value):
                    ok = False
                    break
            if ok:
                filtered.append(it)

        def key_for(it):
            props = dict(it.data or {})
            keys = []
            for ob in body.orderBy or []:
                keys.append(props.get(ob.property))
            return tuple(keys) if keys else 0

        if body.orderBy:
            reverse = (body.orderBy[0].direction or "asc").lower() == "desc"
            filtered.sort(key=key_for, reverse=reverse)

        start = max(0, offset)
        end = start + max(0, limit) if limit > 0 else len(filtered)
        page = filtered[start:end]
        responses = [self._to_object_response(i) for i in page]
        if change_set_rid:
            overlay = self._load_change_set(object_type_api_name, change_set_rid)
            responses = self._apply_change_set_overlay_list(
                object_type_api_name, responses, overlay
            )
        responses = self._apply_object_validity_filter(responses, as_of)
        return ObjectListResponse(data=responses)

    def get_linked_objects(
        self,
        from_object_type_api_name: str,
        pk_value: str,
        link_type_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
    ) -> ObjectListResponse:
        t0 = perf_counter()
        lt = self.metamodel_repo.get_link_type_by_api_name(
            self.service, self.instance, link_type_api_name
        )
        if not lt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkType '{link_type_api_name}' not found",
            )

        if lt.from_object_type_api_name == from_object_type_api_name:
            to_api = lt.to_object_type_api_name
            edge_label = lt.api_name
            direction = "forward"
        elif lt.to_object_type_api_name == from_object_type_api_name:
            to_api = lt.from_object_type_api_name
            edge_label = lt.inverse_api_name or lt.api_name
            direction = "inverse"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"ObjectType '{from_object_type_api_name}' is not part of LinkType '{link_type_api_name}'"
                ),
            )

        from_ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, from_object_type_api_name
        )
        to_ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, to_api
        )
        if not from_ot or not to_ot or not from_ot.primary_key_field:
            return ObjectListResponse(data=[])

        if self.graph_repo:
            rows = self.graph_repo.get_linked_objects(
                from_label=from_ot.api_name,
                from_pk_field=from_ot.primary_key_field,
                from_pk_value=str(pk_value),
                link_label=edge_label,
                to_label=to_ot.api_name,
                direction=direction,
                limit=limit,
                offset=offset,
            )
            data: list[ObjectReadResponse] = []
            for row in rows:
                props = dict(row.get("properties", {}))
                try:
                    self._apply_derivations(to_ot.api_name, props)
                except Exception:
                    pass
                pkv = str(props.get(to_ot.primary_key_field, ""))
                data.append(
                    ObjectReadResponse(
                        rid=f"{to_ot.api_name}:{pkv}",
                        objectTypeApiName=to_ot.api_name,
                        pkValue=pkv,
                        properties=props,
                    )
                )
            dt = perf_counter() - t0
            try:
                logger.info(
                    "graph.traversal source=graph service=%s instance=%s from_type=%s from_pk=%s link=%s direction=%s limit=%d offset=%d count=%d duration=%.4fs",
                    self.service,
                    self.instance,
                    from_object_type_api_name,
                    pk_value,
                    link_type_api_name,
                    direction,
                    int(limit),
                    int(offset),
                    len(data),
                    dt,
                )
            except Exception as e:
                logger.debug("traversal logging failed: %s", e)
            filtered = self._apply_object_validity_filter(data, valid_at)
            return ObjectListResponse(data=filtered)
        return ObjectListResponse(data=[])


class InstancesService:
    """
    Serviço de negócio para objetos (instâncias de ObjectType).
    """

    def __init__(
        self,
        session: Session,
        service: str = "api",
        instance: str = "default",
        graph_repo: GraphInstancesRepository | None = None,
        principal: UserPrincipal | None = None,
        event_bus: DomainEventBus | None = None,
        repo: ObjectInstanceRepository | None = None,
        metamodel_repo: MetamodelRepositoryProtocol | None = None,
    ):
        self.session = session
        self.service = service
        self.instance = instance
        self.repo = repo or SQLObjectInstanceRepository(session)
        self.metamodel_repo = metamodel_repo or SQLMetamodelRepository(session)
        self.principal = principal
        # Graph-First: always initialize graph repository; availability is checked per call
        self.graph_repo = (
            graph_repo if graph_repo is not None else GraphInstancesRepository(session=self.session)
        )
        self._use_graph_reads_flag = use_graph_reads_enabled()
        self.kuzu_repo = get_kuzu_repo()
        self._event_bus = event_bus or NullEventBus()
        self._commands = ObjectInstanceCommandService(
            session=self.session,
            service=self.service,
            instance=self.instance,
            repo=self.repo,
            metamodel_repo=self.metamodel_repo,
            graph_repo=self.graph_repo,
            kuzu_repo=self.kuzu_repo,
            principal=self.principal,
            event_bus=self._event_bus,
            use_graph_reads=self._use_graph_reads,
        )
        self._queries = ObjectInstanceQueryService(
            session=self.session,
            service=self.service,
            instance=self.instance,
            repo=self.repo,
            metamodel_repo=self.metamodel_repo,
            graph_repo=self.graph_repo,
            kuzu_repo=self.kuzu_repo,
            principal=self.principal,
            event_bus=self._event_bus,
            use_graph_reads=self._use_graph_reads,
        )

    def _use_graph_reads(self) -> bool:
        """Graph-First: reads are served from graph when available."""
        try:
            return bool(
                self._use_graph_reads_flag and self.graph_repo and self.graph_repo.is_available()
            )
        except Exception:
            return False

    @property
    def command_service(self) -> ObjectInstanceCommandService:
        return self._commands

    @property
    def query_service(self) -> ObjectInstanceQueryService:
        return self._queries

    # --- Objects ---

    def upsert_object(
        self,
        object_type_api_name: str,
        pk_value: str,
        body: ObjectUpsertRequest,
    ) -> ObjectReadResponse:
        return self._commands.upsert_object(object_type_api_name, pk_value, body)

    # --- DTO Variants (non-breaking helpers) ---

    def upsert_object_dto(
        self,
        object_type_api_name: str,
        pk_value: str,
        body: ObjectUpsertRequest,
    ) -> ObjectInstanceDTO:
        return self._commands.upsert_object_dto(object_type_api_name, pk_value, body)

    def get_object(
        self,
        object_type_api_name: str,
        pk_value: str,
        *,
        as_of: datetime | None = None,
        change_set_rid: str | None = None,
    ) -> ObjectReadResponse | None:
        return self._queries.get_object(
            object_type_api_name,
            pk_value,
            as_of=as_of,
            change_set_rid=change_set_rid,
        )
        # Always query graph repository; it can fallback to SQLModel internally if graph is unavailable
        ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, object_type_api_name
        )
        if not ot or not ot.primary_key_field:
            return None
        item = (
            self.graph_repo.get_by_pk(object_type_api_name, ot.primary_key_field, pk_value)
            if self.graph_repo
            else None
        )
        if item:
            props = dict(item.get("properties", {}))
            # Apply derived properties on read
            try:
                self._apply_derivations(object_type_api_name, props)
            except Exception:
                pass
            response = ObjectReadResponse(
                rid=f"{object_type_api_name}:{pk_value}",
                objectTypeApiName=item["objectTypeApiName"],
                pkValue=str(pk_value),
                properties=props,
            )
            if self._is_valid_at(props, as_of):
                return response
            return None
        inst = self.repo.get_object_instance(
            self.service, self.instance, object_type_api_name, pk_value
        )
        if not inst:
            return None
        resp = self._to_object_response(inst)
        if self._is_valid_at(dict(resp.properties or {}), as_of):
            return resp
        return None

    def get_object_dto(self, object_type_api_name: str, pk_value: str) -> ObjectInstanceDTO | None:
        return self._queries.get_object_dto(object_type_api_name, pk_value)

    def delete_object(self, object_type_api_name: str, pk_value: str) -> bool:
        return self._commands.delete_object(object_type_api_name, pk_value)

    def list_objects(
        self,
        object_type_api_name: str | None = None,
        *,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
        change_set_rid: str | None = None,
    ) -> ObjectListResponse:
        return self._queries.list_objects(
            object_type_api_name,
            limit=limit,
            offset=offset,
            valid_at=valid_at,
            change_set_rid=change_set_rid,
        )

    def search_objects(
        self,
        object_type_api_name: str,
        body: ObjectSearchRequest,
        *,
        change_set_rid: str | None = None,
    ) -> ObjectListResponse:
        return self._queries.search_objects(
            object_type_api_name,
            body,
            change_set_rid=change_set_rid,
        )

    def list_objects_dto(
        self, object_type_api_name: str | None = None, *, limit: int = 100, offset: int = 0
    ) -> list[ObjectInstanceDTO]:
        return self._queries.list_objects_dto(object_type_api_name, limit=limit, offset=offset)

    def search_objects_base(
        self,
        object_type_api_name: str,
        body: ObjectSearchRequest,
        *,
        change_set_rid: str | None = None,
    ) -> ObjectListResponse:
        """
        Search objects by properties. Graph-backed when enabled; SQL fallback otherwise.
        """
        return self._queries.search_objects_base(
            object_type_api_name,
            body,
            change_set_rid=change_set_rid,
        )
        # Pagination
        limit = int(body.limit or 100)
        offset = int(body.offset or 0)
        as_of = getattr(body, "asOf", None)

        # Graph-First: attempt graph; repository can fallback to SQLModel list_by_type
        if self.graph_repo:
            # Interface union path first
            try:
                itf = self.metamodel_repo.get_interface_type_by_api_name(self.service, self.instance, object_type_api_name)  # type: ignore[attr-defined]
            except Exception:
                itf = None
            if itf and getattr(itf, "object_types", None):
                # Fallback-friendly: use list_by_type per implementer and filter/order in memory
                combined_rows: list[dict] = []
                for impl in itf.object_types:
                    if not getattr(impl, "primary_key_field", None):
                        continue
                    rows = self.graph_repo.list_by_type(impl.api_name, limit=10_000, offset=0)
                    for row in rows:
                        row_props = dict(row.get("properties", {}))
                        combined_rows.append(
                            {
                                "impl": impl,
                                "props": row_props,
                            }
                        )

                # Apply filtering
                def match(props: dict, name: str, op: str, val: Any) -> bool:
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

                filtered_rows = []
                for entry in combined_rows:
                    props = entry["props"]
                    ok = True
                    for cond in body.where or []:
                        if not match(props, cond.property, cond.op, cond.value):
                            ok = False
                            break
                    if ok:
                        filtered_rows.append(entry)
                # Order
                if body.orderBy:
                    reverse = (body.orderBy[0].direction or "asc").lower() == "desc"
                    key_name = body.orderBy[0].property
                    filtered_rows.sort(key=lambda e: e["props"].get(key_name), reverse=reverse)
                # Page and map
                start = max(0, offset)
                end = start + max(0, limit) if limit > 0 else len(filtered_rows)
                page = filtered_rows[start:end]
                out: list[ObjectReadResponse] = []
                for entry in page:
                    impl = entry["impl"]
                    props = entry["props"]
                    try:
                        self._apply_derivations(impl.api_name, props)
                    except Exception:
                        props = entry["props"]
                    pkv = str(props.get(impl.primary_key_field, ""))
                    out.append(
                        ObjectReadResponse(
                            rid=f"{impl.api_name}:{pkv}",
                            objectTypeApiName=impl.api_name,
                            pkValue=pkv,
                            properties=props,
                        )
                    )
                filtered = self._apply_object_validity_filter(out, as_of)
                return ObjectListResponse(data=filtered)

            # Otherwise treat as ObjectType
            ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
                self.service, self.instance, object_type_api_name
            )
            if not ot or not ot.primary_key_field:
                return ObjectListResponse(data=[])

            # Unified graph path: list then filter in memory (properties are JSON)
            if self.graph_repo:
                # Fetch a generous page and apply filters/orders locally
                fetch_limit = min(10_000, max(limit + offset, 100))
                rows = self.graph_repo.list_by_type(ot.api_name, limit=fetch_limit, offset=0)

                # Reuse simple match logic
                def match_local(props: dict, name: str, op: str, val: Any) -> bool:
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

                filtered_rows: list[dict] = []
                for row in rows:
                    props = dict(row.get("properties", {}))
                    ok = True
                    for cond in body.where or []:
                        if not match_local(props, cond.property, cond.op, cond.value):
                            ok = False
                            break
                    if ok:
                        filtered_rows.append({"props": props})
                # Order
                if body.orderBy:
                    reverse = (body.orderBy[0].direction or "asc").lower() == "desc"
                    key_name = body.orderBy[0].property
                    filtered_rows.sort(key=lambda e: e["props"].get(key_name), reverse=reverse)
                # Page & map
                start = max(0, offset)
                end = start + max(0, limit) if limit > 0 else len(filtered_rows)
                page = filtered_rows[start:end]
                out: list[ObjectReadResponse] = []
                for entry in page:
                    props = entry["props"]
                    try:
                        self._apply_derivations(ot.api_name, props)
                    except Exception:
                        pass
                    pkv = str(props.get(ot.primary_key_field, ""))
                    out.append(
                        ObjectReadResponse(
                            rid=f"{ot.api_name}:{pkv}",
                            objectTypeApiName=ot.api_name,
                            pkValue=pkv,
                            properties=props,
                        )
                    )
                filtered = self._apply_object_validity_filter(out, as_of)
                return ObjectListResponse(data=filtered)

            # Build Cypher query with quoting and simple WHERE/ORDER BY (when graph available and legacy per-type tables)
            where_clauses: list[str] = []
            for cond in body.where or []:
                prop = f"o.`{cond.property}`"
                op = cond.op
                val = cond.value
                if op == "eq":
                    where_clauses.append(f"{prop} = {self._kuzu_literal(val)}")
                elif op == "ne":
                    where_clauses.append(f"{prop} <> {self._kuzu_literal(val)}")
                elif op == "lt":
                    where_clauses.append(f"{prop} < {self._kuzu_literal(val)}")
                elif op == "lte":
                    where_clauses.append(f"{prop} <= {self._kuzu_literal(val)}")
                elif op == "gt":
                    where_clauses.append(f"{prop} > {self._kuzu_literal(val)}")
                elif op == "gte":
                    where_clauses.append(f"{prop} >= {self._kuzu_literal(val)}")
                elif op == "contains":
                    s = str(val) if val is not None else ""
                    # case-insensitive contains
                    where_clauses.append(f"LOWER({prop}) CONTAINS LOWER({self._kuzu_literal(s)})")
                elif op == "in":
                    if isinstance(val, (list, tuple)):
                        arr = ", ".join(self._kuzu_literal(v) for v in val)
                        where_clauses.append(f"{prop} IN [{arr}]")
                elif op == "isnull":
                    where_clauses.append(f"{prop} IS NULL")
                elif op == "isnotnull":
                    where_clauses.append(f"{prop} IS NOT NULL")
                elif op == "between":
                    if isinstance(val, (list, tuple)) and len(val) == 2:
                        lo, hi = val[0], val[1]
                        where_clauses.append(
                            f"{prop} >= {self._kuzu_literal(lo)} AND {prop} <= {self._kuzu_literal(hi)}"
                        )
                elif op == "startswith":
                    s = str(val) if val is not None else ""
                    where_clauses.append(
                        f"LOWER({prop}) STARTS WITH LOWER({self._kuzu_literal(s)})"
                    )
                elif op == "endswith":
                    s = str(val) if val is not None else ""
                    where_clauses.append(f"LOWER({prop}) ENDS WITH LOWER({self._kuzu_literal(s)})")
            where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

            order_parts: list[str] = []
            for ob in body.orderBy or []:
                p = f"o.`{ob.property}`"
                d = "DESC" if (ob.direction or "asc").lower() == "desc" else "ASC"
                order_parts.append(f"{p} {d}")
            order_sql = (" ORDER BY " + ", ".join(order_parts)) if order_parts else ""

            fetch_limit = limit + offset if offset > 0 else limit
            query = f"MATCH (o:`{ot.api_name}`){where_sql} RETURN o{order_sql} LIMIT {fetch_limit}"
            try:
                res = self.graph_repo.kuzu.execute(query)  # type: ignore[attr-defined]
                try:
                    df = res.get_as_df()  # type: ignore[attr-defined]
                    if df is None or len(df) == 0:
                        return ObjectListResponse(data=[])
                    data: list[ObjectReadResponse] = []
                    start = offset if offset > 0 else 0
                    end = start + limit if limit > 0 else len(df)
                    for idx in range(start, min(end, len(df))):
                        row = df.iloc[idx]
                        props = {}
                        for col in df.columns:
                            if col.startswith("o."):
                                props[col[2:]] = row[col]
                        if not props:
                            props = {col: row[col] for col in df.columns if col != "o"}
                        try:
                            self._apply_derivations(ot.api_name, props)
                        except Exception:
                            pass
                        pkv = str(props.get(ot.primary_key_field, ""))
                        data.append(
                            ObjectReadResponse(
                                rid=f"{ot.api_name}:{pkv}",
                                objectTypeApiName=ot.api_name,
                                pkValue=pkv,
                                properties=props,
                            )
                        )
                    filtered = self._apply_object_validity_filter(data, as_of)
                    return ObjectListResponse(data=filtered)
                except Exception as e:
                    # If DataFrame extraction fails, fallback to SQL path below
                    logger.debug("graph dataframe extraction failed; falling back to SQL: %s", e)
            except Exception as e:
                # If query fails, fallback to SQL path
                logger.debug("graph query failed; falling back to SQL: %s", e)

        # SQL fallback: filter in memory on ObjectInstance.data
        items = self.repo.list_object_instances(
            self.service,
            self.instance,
            object_type_api_name=object_type_api_name,
            limit=10_000,
            offset=0,
        )

        def match_cond(props: dict, name: str, op: str, val: Any) -> bool:
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

        filtered = []
        for it in items:
            props = dict(it.data or {})
            try:
                self._apply_derivations(self._get_object_type_api_name_for_instance(it), props)
            except Exception:
                pass
            ok = True
            for cond in body.where or []:
                if not match_cond(props, cond.property, cond.op, cond.value):
                    ok = False
                    break
            if ok:
                filtered.append(it)

        # Order
        def key_for(it):
            props = dict(it.data or {})
            keys = []
            for ob in body.orderBy or []:
                keys.append(props.get(ob.property))
            return tuple(keys) if keys else 0

        if body.orderBy:
            # Support single-direction sorting across all keys (use first spec)
            reverse = (body.orderBy[0].direction or "asc").lower() == "desc"
            filtered.sort(key=key_for, reverse=reverse)

        start = max(0, offset)
        end = start + max(0, limit) if limit > 0 else len(filtered)
        page = filtered[start:end]
        responses = [self._to_object_response(i) for i in page]
        responses = self._apply_object_validity_filter(responses, as_of)
        return ObjectListResponse(data=responses)

    def get_linked_objects(
        self,
        from_object_type_api_name: str,
        pk_value: str,
        link_type_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
        valid_at: datetime | None = None,
    ) -> ObjectListResponse:
        """
        Traverse the graph from a starting object via a LinkType and return connected objects.
        Returns ObjectListResponse for consistency with listing endpoints.
        """
        return self._queries.get_linked_objects(
            from_object_type_api_name,
            pk_value,
            link_type_api_name,
            limit=limit,
            offset=offset,
            valid_at=valid_at,
        )
        t0 = perf_counter()
        # Validate LinkType and involved ObjectTypes
        lt = self.metamodel_repo.get_link_type_by_api_name(
            self.service, self.instance, link_type_api_name
        )
        if not lt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkType '{link_type_api_name}' not found",
            )

        # Determine traversal direction and destination type
        if lt.from_object_type_api_name == from_object_type_api_name:
            to_api = lt.to_object_type_api_name
            edge_label = lt.api_name
            direction = "forward"
        elif lt.to_object_type_api_name == from_object_type_api_name:
            to_api = lt.from_object_type_api_name
            # Use inverse label for inverse traversal to match materialized edge direction
            edge_label = lt.inverse_api_name or lt.api_name
            direction = "inverse"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ObjectType '{from_object_type_api_name}' is not part of LinkType '{link_type_api_name}'",
            )

        from_ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, from_object_type_api_name
        )
        to_ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, to_api
        )
        if not from_ot or not to_ot or not from_ot.primary_key_field:
            return ObjectListResponse(data=[])

        # Graph-First traversal via repository (with internal SQL fallback)
        if self.graph_repo:
            rows = self.graph_repo.get_linked_objects(
                from_label=from_ot.api_name,
                from_pk_field=from_ot.primary_key_field,
                from_pk_value=str(pk_value),
                link_label=edge_label,
                to_label=to_ot.api_name,
                direction=direction,
                limit=limit,
                offset=offset,
            )
            data: list[ObjectReadResponse] = []
            for row in rows:
                props = dict(row.get("properties", {}))
                try:
                    self._apply_derivations(to_ot.api_name, props)
                except Exception:
                    pass
                pkv = str(props.get(to_ot.primary_key_field, ""))
                data.append(
                    ObjectReadResponse(
                        rid=f"{to_ot.api_name}:{pkv}",
                        objectTypeApiName=to_ot.api_name,
                        pkValue=pkv,
                        properties=props,
                    )
                )
            dt = perf_counter() - t0
            try:
                logger.info(
                    "graph.traversal source=graph service=%s instance=%s from_type=%s from_pk=%s link=%s direction=%s limit=%d offset=%d count=%d duration=%.4fs",
                    self.service,
                    self.instance,
                    from_object_type_api_name,
                    pk_value,
                    link_type_api_name,
                    direction,
                    int(limit),
                    int(offset),
                    len(data),
                    dt,
                )
            except Exception as e:
                logger.debug("traversal logging failed: %s", e)
            filtered = self._apply_object_validity_filter(data, valid_at)
            return ObjectListResponse(data=filtered)
        # Graph repo not initialized (unlikely) -> empty
        return ObjectListResponse(data=[])

    # --- Bulk ---
    def bulk_load_objects(
        self, object_type_api_name: str, body: ObjectBulkLoadRequest
    ) -> ObjectListResponse:
        return self._commands.bulk_load_objects(object_type_api_name, body)

    # --- Helpers ---

    def _validate_and_normalize_props(self, ot: ObjectType, pk_value: str, props: dict) -> dict:
        # Build property definition map
        defs: dict[str, Any] = {p.api_name: p for p in getattr(ot, "property_types", [])}

        # Unknown properties
        unknown = [k for k in props.keys() if k not in defs]
        if unknown:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown properties for '{ot.api_name}': {unknown}",
            )

        # Enforce required properties (besides PK which we will inject)
        required = [p.api_name for p in ot.property_types if p.required]
        # Add PK explicitly to required list if marked required in schema
        if ot.primary_key_field not in required:
            required.append(ot.primary_key_field)

        # Set PK value from path and ensure present
        props[ot.primary_key_field] = pk_value

        missing = [name for name in required if name not in props or props[name] is None]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required properties for '{ot.api_name}': {missing}",
            )

        # Type validation/coercion
        normalized: dict = {}
        for name, value in props.items():
            pdef = defs.get(name)
            if not pdef:
                # Ignore silently (shouldn't happen due to unknown check)
                continue
            normalized[name] = self._coerce_type(value, pdef.data_type)

        return normalized

    def _coerce_type(self, value, data_type: str):
        if value is None:
            return None
        dt = (data_type or "string").lower()
        try:
            if dt == "string":
                return str(value)
            if dt in ("integer", "int", "long"):
                if isinstance(value, bool):
                    # avoid True->1 for boolean props
                    raise ValueError("boolean provided for integer")
                if isinstance(value, int):
                    return value
                if isinstance(value, str):
                    return int(value)
                if isinstance(value, float):
                    if value.is_integer():
                        return int(value)
                    raise ValueError("float not integral")
                raise ValueError("unsupported type for integer")
            if dt in ("double", "float"):
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    return float(value)
                raise ValueError("unsupported type for double")
            if dt in ("boolean", "bool"):
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    v = value.strip().lower()
                    if v in ("true", "1", "yes"):
                        return True
                    if v in ("false", "0", "no"):
                        return False
                raise ValueError("unsupported type for boolean")
            if dt in ("date", "timestamp"):
                # Accept ISO strings; do minimal normalization to str
                return str(value)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid value '{value}' for type '{data_type}'",
            ) from err
        # default
        return value

    def _kuzu_literal(self, value):
        """Converts Python values into Kùzu Cypher-compatible literals."""
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        # Escape single quotes in strings
        s = str(value).replace("'", "''")
        return f"'{s}'"

    # --- Validity helpers ---

    def _parse_validity_timestamp(self, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        try:
            text = str(value).strip()
            if not text:
                return None
            # Support date-only strings by relying on fromisoformat
            return datetime.fromisoformat(text)
        except Exception:
            return None

    def _is_valid_at(self, properties: dict[str, Any], as_of: datetime | None) -> bool:
        if as_of is None:
            return True
        start_raw = (
            properties.get("valid_from")
            or properties.get("validFrom")
            or properties.get("__valid_from")
        )
        end_raw = (
            properties.get("valid_to") or properties.get("validTo") or properties.get("__valid_to")
        )
        start = self._parse_validity_timestamp(start_raw)
        end = self._parse_validity_timestamp(end_raw)
        if start and as_of < start:
            return False
        if end and as_of >= end:
            return False
        return True

    def _apply_object_validity_filter(
        self, objects: list[ObjectReadResponse], as_of: datetime | None
    ) -> list[ObjectReadResponse]:
        if as_of is None:
            return objects
        filtered: list[ObjectReadResponse] = []
        for obj in objects:
            props = dict(obj.properties or {})
            if self._is_valid_at(props, as_of):
                filtered.append(obj)
        return filtered

    def _to_object_response(self, inst: ObjectInstance) -> ObjectReadResponse:
        props = dict(inst.data or {})
        try:
            self._apply_derivations(inst.object_type_api_name, props)
        except Exception:
            pass
        return ObjectReadResponse(
            rid=inst.rid,
            objectTypeApiName=inst.object_type_api_name,
            pkValue=inst.pk_value,
            properties=props,
        )

    def _to_object_dto(self, inst: ObjectInstance) -> ObjectInstanceDTO:
        return ObjectInstanceDTO.from_model(inst)

    # --- Derivations ---

    def _safe_eval_derivation(self, expr: str, props: dict[str, Any]) -> Any:
        """Safely evaluate a derivation expression against props using a restricted AST.

        Allowed constructs: constants, props[...] indexing, bool ops, unary not, comparisons,
        binary ops (+,-,*,/), if-expr. Disallows calls and attribute access.
        """
        try:
            tree = ast.parse(expr, mode="eval")
        except Exception:
            return None

        def eval_node(node):
            if isinstance(node, ast.Expression):
                return eval_node(node.body)
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.Name):
                if node.id == "props":
                    return props
                return None
            if isinstance(node, ast.Subscript):
                base = eval_node(node.value)
                key = eval_node(node.slice) if not isinstance(node.slice, ast.Slice) else None
                try:
                    return base[key]
                except Exception:
                    return None
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd, ast.Not)):
                v = eval_node(node.operand)
                try:
                    if isinstance(node.op, ast.USub):
                        return -v
                    if isinstance(node.op, ast.UAdd):
                        return +v
                    return not bool(v)
                except Exception:
                    return None
            if isinstance(node, ast.BinOp) and isinstance(
                node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)
            ):
                left_val = eval_node(node.left)
                right_val = eval_node(node.right)
                try:
                    if isinstance(node.op, ast.Add):
                        return left_val + right_val
                    if isinstance(node.op, ast.Sub):
                        return left_val - right_val
                    if isinstance(node.op, ast.Mult):
                        return left_val * right_val
                    return left_val / right_val
                except Exception:
                    return None
            if isinstance(node, ast.BoolOp):
                vals = [bool(eval_node(v)) for v in node.values]
                if isinstance(node.op, ast.And):
                    return all(vals)
                if isinstance(node.op, ast.Or):
                    return any(vals)
                return None
            if isinstance(node, ast.Compare):
                left = eval_node(node.left)
                for op, comp in zip(node.ops, node.comparators, strict=False):
                    right = eval_node(comp)
                    try:
                        if isinstance(op, ast.Eq) and not (left == right):
                            return False
                        if isinstance(op, ast.NotEq) and not (left != right):
                            return False
                        if isinstance(op, ast.Lt) and not (left < right):
                            return False
                        if isinstance(op, ast.LtE) and not (left <= right):
                            return False
                        if isinstance(op, ast.Gt) and not (left > right):
                            return False
                        if isinstance(op, ast.GtE) and not (left >= right):
                            return False
                    except Exception:
                        return False
                    left = right
                return True
            if isinstance(node, ast.IfExp):
                cond = eval_node(node.test)
                return eval_node(node.body) if cond else eval_node(node.orelse)
            # Disallow Call, Attribute, etc.
            return None

        try:
            return eval_node(tree)
        except Exception:
            return None

    def _apply_derivations(self, object_type_api_name: str, props: dict[str, Any]) -> None:
        ot: ObjectType | None = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, object_type_api_name
        )
        if not ot:
            return
        for p in getattr(ot, "property_types", []) or []:
            script = getattr(p, "derivation_script", None)
            if script:
                val = self._safe_eval_derivation(str(script), props)
                if val is not None:
                    props[p.api_name] = val

    def _get_object_type_api_name_for_instance(self, inst: ObjectInstance) -> str:
        return inst.object_type_api_name
