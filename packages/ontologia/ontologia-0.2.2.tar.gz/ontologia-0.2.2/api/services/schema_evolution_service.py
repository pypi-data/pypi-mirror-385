"""Schema evolution helpers for planning and applying ontology changes."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from sqlmodel import select

from api.services.analytics_service import AnalyticsService
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.metamodel import LinkTypePutRequest, ObjectTypePutRequest
from api.v2.schemas.search import AggregateRequest, AggregateSpec
from ontologia.config import _config_root, load_config


@dataclass(frozen=True)
class SchemaPlanItem:
    kind: str
    api_name: str
    action: str
    dangerous: bool = False
    reasons: list[str] | None = None


class SchemaEvolutionService:
    """Plan and apply schema evolution operations against the metamodel."""

    def __init__(
        self,
        metamodel_service: MetamodelService,
        analytics_service: AnalyticsService | None = None,
        *,
        definitions_dir: Path | None = None,
    ) -> None:
        config_root = _config_root()
        config = load_config(config_root)
        self._definitions_dir = (
            definitions_dir or (config_root / config.project.definitions_dir)
        ).resolve()
        self._metamodel = metamodel_service
        self._analytics = analytics_service

    # ------------------------------------------------------------------
    # Public API

    def plan_schema_changes(
        self,
        *,
        definitions_dir: Path | None = None,
        include_impact: bool = False,
        include_dependencies: bool = False,
    ) -> dict[str, Any]:
        objs_local, links_local = self._collect_local(definitions_dir)
        self._validate_local(objs_local, links_local)
        objs_remote, links_remote = self._fetch_remote_state()
        plan = self._build_plan(objs_local, links_local, objs_remote, links_remote)

        response: dict[str, Any] = {
            "plan": [self._plan_item_to_dict(item) for item in plan],
            "definitions_dir": str(definitions_dir or self._definitions_dir),
        }

        if include_dependencies:
            response["dependencies"] = self._compute_dependencies(plan, links_local, links_remote)

        if include_impact:
            response["impact"] = self._compute_impact(plan)

        return response

    def apply_schema_changes(
        self,
        *,
        definitions_dir: Path | None = None,
        allow_destructive: bool = False,
        regenerate_sdk: bool = False,
    ) -> dict[str, Any]:
        objs_local, links_local = self._collect_local(definitions_dir)
        self._validate_local(objs_local, links_local)
        objs_remote, links_remote = self._fetch_remote_state()
        plan = self._build_plan(objs_local, links_local, objs_remote, links_remote)

        if not plan:
            return {"applied": [], "skipped": [], "regenerated_sdk": False}

        if (
            any(it.dangerous for it in plan) or any(it.action == "delete" for it in plan)
        ) and not allow_destructive:
            raise ValueError(
                "Plan contains destructive operations; pass allow_destructive=True to proceed."
            )

        applied: list[dict[str, Any]] = []
        for item in plan:
            if item.kind == "objectType":
                if item.action == "delete":
                    self._metamodel.delete_object_type(item.api_name)
                else:
                    payload = objs_local[item.api_name]
                    schema = ObjectTypePutRequest(
                        **{k: v for k, v in payload.items() if k != "apiName"}
                    )
                    self._metamodel.upsert_object_type(item.api_name, schema)
            else:  # linkType
                if item.action == "delete":
                    self._metamodel.delete_link_type(item.api_name)
                else:
                    payload = links_local[item.api_name]
                    schema = LinkTypePutRequest(
                        **{k: v for k, v in payload.items() if k != "apiName"}
                    )
                    self._metamodel.upsert_link_type(item.api_name, schema)
            applied.append(self._plan_item_to_dict(item))

        # SDK regeneration is orchestrated by ontologia-cli today; expose flag for parity.
        return {"applied": applied, "skipped": [], "regenerated_sdk": bool(regenerate_sdk)}

    def list_migration_tasks(self, *, status: str | None = None) -> list[dict[str, Any]]:
        from ontologia.domain.metamodels.migrations.migration_task import (
            MigrationTask,
        )

        session = self._metamodel.session
        tasks = list(session.exec(select(MigrationTask)))
        if status:
            tasks = [task for task in tasks if task.status.value == status]
        return [self._serialize_task(task) for task in tasks]

    def update_migration_task(
        self,
        rid: str,
        *,
        status: str,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        from ontologia.domain.metamodels.migrations.migration_task import (
            MigrationTask,
            MigrationTaskStatus,
        )

        session = self._metamodel.session
        task = session.get(MigrationTask, rid)
        if not task:
            raise ValueError(f"MigrationTask '{rid}' not found")

        try:
            new_status = MigrationTaskStatus(status)
        except ValueError as exc:
            raise ValueError("Invalid migration task status") from exc

        task.status = new_status
        task.error_message = error_message
        session.add(task)
        session.commit()
        session.refresh(task)
        return self._serialize_task(task)

    # ------------------------------------------------------------------
    # Helpers

    def _collect_local(
        self,
        definitions_dir: Path | None = None,
    ) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        root = Path(definitions_dir or self._definitions_dir)
        object_dir = root / "object_types"
        link_dir = root / "link_types"
        objects: dict[str, dict[str, Any]] = {}
        links: dict[str, dict[str, Any]] = {}

        for directory, target in ((object_dir, objects), (link_dir, links)):
            if not directory.is_dir():
                continue
            for path in directory.glob("*.y*ml"):
                with path.open(encoding="utf-8") as handle:
                    data = yaml.safe_load(handle) or {}
                api_name = str(data.get("apiName") or path.stem)
                target[api_name] = data

        return objects, links

    def _validate_local(
        self,
        objects: dict[str, dict[str, Any]],
        links: dict[str, dict[str, Any]],
    ) -> None:
        errors: list[str] = []
        for api_name, payload in objects.items():
            try:
                ObjectTypePutRequest(**{k: v for k, v in payload.items() if k != "apiName"})
            except ValidationError as exc:
                errors.append(f"ObjectType '{api_name}' invalid: {exc}")
        for api_name, payload in links.items():
            try:
                LinkTypePutRequest(**{k: v for k, v in payload.items() if k != "apiName"})
            except ValidationError as exc:
                errors.append(f"LinkType '{api_name}' invalid: {exc}")
        if errors:
            raise ValueError("; ".join(errors))

    def _fetch_remote_state(self) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        objects = {
            ot.apiName: ot.model_dump(exclude_none=True)
            for ot in self._metamodel.list_object_types()
        }
        links = {
            lt.apiName: lt.model_dump(exclude_none=True) for lt in self._metamodel.list_link_types()
        }
        return objects, links

    def _build_plan(
        self,
        objs_local: dict[str, dict[str, Any]],
        links_local: dict[str, dict[str, Any]],
        objs_remote: dict[str, dict[str, Any]],
        links_remote: dict[str, dict[str, Any]],
    ) -> list[SchemaPlanItem]:
        plan: list[SchemaPlanItem] = []

        for api_name in objs_local.keys():
            if api_name not in objs_remote:
                plan.append(SchemaPlanItem("objectType", api_name, "create"))
            else:
                local = objs_local[api_name]
                remote = objs_remote[api_name]
                if self._object_differs(local, remote):
                    reasons = self._object_change_reasons(local, remote)
                    plan.append(
                        SchemaPlanItem(
                            "objectType",
                            api_name,
                            "update",
                            dangerous=bool(reasons),
                            reasons=reasons,
                        )
                    )

        for api_name in objs_remote.keys() - objs_local.keys():
            plan.append(
                SchemaPlanItem(
                    "objectType",
                    api_name,
                    "delete",
                    dangerous=True,
                    reasons=["delete"],
                )
            )

        for api_name in links_local.keys():
            if api_name not in links_remote:
                plan.append(SchemaPlanItem("linkType", api_name, "create"))
            else:
                local = links_local[api_name]
                remote = links_remote[api_name]
                if self._link_differs(local, remote):
                    reasons = self._link_change_reasons(local, remote)
                    plan.append(
                        SchemaPlanItem(
                            "linkType",
                            api_name,
                            "update",
                            dangerous=bool(reasons),
                            reasons=reasons,
                        )
                    )

        for api_name in links_remote.keys() - links_local.keys():
            plan.append(
                SchemaPlanItem(
                    "linkType",
                    api_name,
                    "delete",
                    dangerous=True,
                    reasons=["delete"],
                )
            )

        return plan

    def _object_differs(self, local: dict[str, Any], remote: dict[str, Any]) -> bool:
        interesting_fields = {"displayName", "description", "primaryKey", "properties"}
        return any(local.get(field) != remote.get(field) for field in interesting_fields)

    def _object_change_reasons(
        self,
        local: dict[str, Any],
        remote: dict[str, Any],
    ) -> list[str]:
        reasons: list[str] = []
        if local.get("primaryKey") != remote.get("primaryKey"):
            reasons.append("primaryKey change")
        remote_props = dict(remote.get("properties") or {})
        local_props = dict(local.get("properties") or {})
        for prop_name in remote_props.keys() - local_props.keys():
            reasons.append(f"property removed: {prop_name}")
        for prop_name, local_prop in local_props.items():
            if prop_name not in remote_props:
                continue
            remote_prop = remote_props.get(prop_name) or {}
            if (local_prop or {}).get("dataType") != remote_prop.get("dataType"):
                reasons.append(
                    f"property type change: {prop_name} ({remote_prop.get('dataType')}→{(local_prop or {}).get('dataType')})"
                )
        return reasons

    def _link_differs(self, local: dict[str, Any], remote: dict[str, Any]) -> bool:
        fields = [
            "displayName",
            "cardinality",
            "fromObjectType",
            "toObjectType",
            "inverse",
            "description",
            "properties",
            "backingDatasetApiName",
            "fromPropertyMapping",
            "toPropertyMapping",
            "propertyMappings",
            "incrementalField",
        ]
        return any(local.get(field) != remote.get(field) for field in fields)

    def _link_change_reasons(self, local: dict[str, Any], remote: dict[str, Any]) -> list[str]:
        reasons: list[str] = []
        if local.get("fromObjectType") != remote.get("fromObjectType") or local.get(
            "toObjectType"
        ) != remote.get("toObjectType"):
            reasons.append("endpoint change")
        return reasons

    def _plan_item_to_dict(self, item: SchemaPlanItem) -> dict[str, Any]:
        return {
            "kind": item.kind,
            "api_name": item.api_name,
            "action": item.action,
            "dangerous": item.dangerous,
            "reasons": list(item.reasons or []),
        }

    def _compute_dependencies(
        self,
        plan: Iterable[SchemaPlanItem],
        links_local: dict[str, dict[str, Any]],
        links_remote: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        changed_objects = {item.api_name for item in plan if item.kind == "objectType"}
        changed_links = {item.api_name for item in plan if item.kind == "linkType"}
        dependencies: dict[str, Any] = {}
        if changed_objects:
            ot_to_links: dict[str, list[str]] = {}
            for api_name, payload in links_remote.items():
                from_ot = payload.get("fromObjectType")
                to_ot = payload.get("toObjectType")
                if from_ot:
                    ot_to_links.setdefault(str(from_ot), []).append(api_name)
                if to_ot:
                    ot_to_links.setdefault(str(to_ot), []).append(api_name)
            for api_name in changed_objects:
                dependencies.setdefault("objectTypes", {})[api_name] = sorted(
                    set(ot_to_links.get(api_name, []))
                )
        if changed_links:
            for api_name in changed_links:
                payload = links_local.get(api_name) or links_remote.get(api_name) or {}
                dependencies.setdefault("linkTypes", {})[api_name] = {
                    "from": payload.get("fromObjectType"),
                    "to": payload.get("toObjectType"),
                }
        return dependencies

    def _compute_impact(self, plan: Iterable[SchemaPlanItem]) -> dict[str, int]:
        if not self._analytics:
            return {}
        impacted: set[str] = {
            item.api_name
            for item in plan
            if item.kind == "objectType" and item.action in {"update", "delete"}
        }
        counts: dict[str, int] = {}
        for object_type in sorted(impacted):
            try:
                request = AggregateRequest(
                    objectTypeApiName=object_type,
                    metrics=[AggregateSpec(func="count")],
                    groupBy=[],
                    where=[],
                )
                response = self._analytics.aggregate(request)
                rows = response.model_dump().get("rows", [])
                count_val = 0
                if rows:
                    metrics = rows[0].get("metrics") or {}
                    count_val = metrics.get("count") or metrics.get("m_count") or 0
                counts[object_type] = int(count_val)
            except Exception:
                counts[object_type] = -1
        return counts

    def _serialize_task(self, task: Any) -> dict[str, Any]:
        return {
            "rid": task.rid,
            "api_name": task.api_name,
            "objectType": task.object_type_api_name,
            "fromVersion": task.from_version,
            "toVersion": task.to_version,
            "status": task.status.value,
            "plan": dict(task.plan or {}),
            "errorMessage": task.error_message,
            "createdAt": (
                getattr(task, "created_at", None).isoformat()
                if getattr(task, "created_at", None)
                else None
            ),
        }
