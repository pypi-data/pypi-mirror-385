"""FastMCP router exposing Ontologia metamodel capabilities to AI agents."""

from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import Depends
from fastmcp import FastMCP
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.core.settings import get_settings
from api.core.temporal import get_temporal_client
from api.dependencies.realtime import ensure_runtime_started, get_runtime
from api.services.actions_service import ActionsService
from api.services.analytics_service import AnalyticsService
from api.services.change_set_service import ChangeSetService
from api.services.data_analysis_service import DataAnalysisService
from api.services.datacatalog_service import DataCatalogService
from api.services.instances_service import InstancesService
from api.services.linked_objects_service import LinkedObjectsService
from api.services.metamodel_service import MetamodelService
from api.services.migration_execution_service import MigrationExecutionService
from api.services.schema_evolution_service import SchemaEvolutionService
from api.v2.schemas.actions import ActionExecuteRequest
from api.v2.schemas.change_sets import ChangeSetApproveRequest, ChangeSetCreateRequest
from api.v2.schemas.datasets import DatasetPutRequest
from api.v2.schemas.instances import ObjectUpsertRequest
from api.v2.schemas.linked_objects import LinkCreateRequest
from api.v2.schemas.metamodel import (
    LinkTypePutRequest,
    ObjectTypePutRequest,
)
from api.v2.schemas.search import AggregateRequest, ObjectSearchRequest

DEFAULT_SERVICE = "ontology"
DEFAULT_INSTANCE = "default"


mcp = FastMCP("ontologia-mcp")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_root(env_value: str | None, default_relative: Path) -> Path:
    if env_value:
        candidate = Path(env_value)
        if not candidate.is_absolute():
            candidate = (_project_root() / candidate).resolve()
        else:
            candidate = candidate.resolve()
        return candidate
    return (_project_root() / default_relative).resolve()


def _data_root() -> Path:
    return _resolve_root(os.getenv("ONTOLOGIA_AGENT_DATA_ROOT"), Path("data/uploads"))


def _dbt_models_root() -> Path:
    return _resolve_root(
        os.getenv("ONTOLOGIA_DBT_MODELS_ROOT"),
        Path("example_project/dbt_project/models"),
    )


def _resolve_path_in_root(path_str: str, root: Path) -> Path:
    root_resolved = root.resolve()
    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = (root_resolved / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(
            f"Path '{candidate}' is outside the allowed directory '{root_resolved}'."
        ) from exc
    return candidate


@contextmanager
def _engine(connection_url: str) -> Iterator[Engine]:
    engine = create_engine(connection_url)
    try:
        yield engine
    finally:  # pragma: no cover - defensive cleanup
        engine.dispose()


def _run_sync(coro):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        asyncio.set_event_loop(None)
        loop.close()


def _serialize_realtime_event(event) -> dict[str, Any]:
    return {
        "sequence": event.sequence,
        "eventType": event.event_type,
        "entityId": event.entity_id,
        "objectType": event.object_type,
        "provenance": event.provenance,
        "updatedAt": event.updated_at.isoformat() if event.updated_at else None,
        "expiresAt": event.expires_at.isoformat() if event.expires_at else None,
        "components": {key: dict(value) for key, value in event.components.items()},
        "metadata": dict(event.metadata),
    }


async def _collect_realtime_events(
    duration_seconds: float,
    max_events: int,
    object_types: set[str] | None,
    entity_ids: set[str] | None,
) -> list[dict[str, Any]]:
    await ensure_runtime_started()
    runtime = get_runtime()
    queue = runtime.subscribe_events()
    events: list[dict[str, Any]] = []
    loop = asyncio.get_running_loop()
    deadline = loop.time() + max(duration_seconds, 0)
    try:
        while len(events) < max_events:
            timeout = deadline - loop.time()
            if timeout <= 0:
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=timeout)
            except TimeoutError:
                break
            if object_types and event.object_type not in object_types:
                continue
            if entity_ids and event.entity_id not in entity_ids:
                continue
            events.append(_serialize_realtime_event(event))
    finally:
        runtime.unsubscribe_events(queue)
    return events


def _service(principal: UserPrincipal | None) -> tuple[str, str]:
    # In the future this can be resolved from the principal or request context.
    _ = principal
    return DEFAULT_SERVICE, DEFAULT_INSTANCE


def _metamodel_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> MetamodelService:
    service, instance = _service(principal)
    return MetamodelService(session, service=service, instance=instance, principal=principal)


def _instances_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> InstancesService:
    service, instance = _service(principal)
    return InstancesService(session, service=service, instance=instance, principal=principal)


def _instances_editor_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> InstancesService:
    service, instance = _service(principal)
    return InstancesService(session, service=service, instance=instance, principal=principal)


def _datacatalog_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> DataCatalogService:
    service, instance = _service(principal)
    return DataCatalogService(session, service=service, instance=instance, principal=principal)


def _datacatalog_read_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> DataCatalogService:
    service, instance = _service(principal)
    return DataCatalogService(session, service=service, instance=instance, principal=principal)


def _linked_objects_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> LinkedObjectsService:
    service, instance = _service(principal)
    return LinkedObjectsService(session, service=service, instance=instance, principal=principal)


def _linked_objects_editor_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> LinkedObjectsService:
    service, instance = _service(principal)
    return LinkedObjectsService(session, service=service, instance=instance, principal=principal)


def _data_analysis_service() -> DataAnalysisService:
    return DataAnalysisService()


def _change_sets_editor_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> ChangeSetService:
    service, instance = _service(principal)
    return ChangeSetService(session, service=service, instance=instance, principal=principal)


def _change_sets_admin_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
) -> ChangeSetService:
    service, instance = _service(principal)
    return ChangeSetService(session, service=service, instance=instance, principal=principal)


def _serialize_change_set(service: ChangeSetService, record) -> dict[str, Any]:
    dataset = service._dataset_by_rid(record.dataset_rid)
    dataset_api_name = dataset.api_name if dataset else record.api_name
    return {
        "apiName": record.api_name,
        "rid": record.rid,
        "name": record.name,
        "status": record.status,
        "targetObjectType": record.target_object_type,
        "baseBranch": record.base_branch,
        "description": record.description,
        "datasetApiName": dataset_api_name,
        "createdAt": record.created_at.isoformat(),
        "createdBy": record.created_by,
        "approvedAt": record.approved_at.isoformat() if record.approved_at else None,
        "payload": dict(record.payload or {}),
    }


def _analytics_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> AnalyticsService:
    service, instance = _service(principal)
    return AnalyticsService(session, service=service, instance=instance, principal=principal)


def _schema_evolution_service(
    metamodel: MetamodelService = Depends(_metamodel_service),
    analytics: AnalyticsService = Depends(_analytics_service),
) -> SchemaEvolutionService:
    return SchemaEvolutionService(metamodel, analytics_service=analytics)


def _migration_execution_context(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
):
    service_name, instance = _service(principal)
    return MigrationExecutionService(session), service_name, instance


def _actions_viewer_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> ActionsService:
    service, instance = _service(principal)
    return ActionsService(session, service=service, instance=instance, principal=principal)


def _actions_editor_service(
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
    temporal_client=Depends(get_temporal_client),
) -> ActionsService:
    service, instance = _service(principal)
    return ActionsService(
        session,
        service=service,
        instance=instance,
        temporal_client=temporal_client,
        principal=principal,
    )


@mcp.tool()
def upsert_object_type(
    api_name: str,
    schema: ObjectTypePutRequest,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Create or update an ObjectType definition."""

    result = service.upsert_object_type(api_name, schema)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def delete_object_type(
    api_name: str,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Delete an ObjectType by apiName."""

    service.delete_object_type(api_name)
    return {"status": "deleted", "apiName": api_name}


@mcp.tool()
def get_object_type(
    api_name: str,
    version: int | None = None,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Fetch a single ObjectType definition."""

    result = service.get_object_type(api_name, version=version)
    if result is None:
        raise ValueError(f"ObjectType '{api_name}' not found")
    return result.model_dump(exclude_none=True)


@mcp.tool()
def upsert_link_type(
    api_name: str,
    schema: LinkTypePutRequest,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Create or update a LinkType definition."""

    result = service.upsert_link_type(api_name, schema)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def delete_link_type(
    api_name: str,
    service=Depends(_metamodel_service),
) -> dict[str, Any]:
    """Delete a LinkType by apiName."""

    service.delete_link_type(api_name)
    return {"status": "deleted", "apiName": api_name}


@mcp.tool()
def list_object_types(
    service=Depends(_metamodel_service),
) -> list[dict[str, Any]]:
    """List all ObjectTypes available in the current ontology."""

    items = service.list_object_types()
    return [item.model_dump(exclude_none=True) for item in items]


@mcp.tool()
def list_link_types(
    service=Depends(_metamodel_service),
) -> list[dict[str, Any]]:
    """List all LinkTypes available in the current ontology."""

    items = service.list_link_types()
    return [item.model_dump(exclude_none=True) for item in items]


@mcp.tool()
def list_objects(
    object_type_api_name: str | None = None,
    limit: int = 100,
    offset: int = 0,
    as_of: str | None = None,
    service=Depends(_instances_service),
) -> dict[str, Any]:
    """List object instances with optional filtering by ObjectType."""

    as_of_dt = None
    if as_of:
        try:
            as_of_dt = datetime.fromisoformat(as_of)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Invalid 'as_of' timestamp; expected ISO 8601 format") from exc
    result = service.list_objects(
        object_type_api_name,
        limit=limit,
        offset=offset,
        valid_at=as_of_dt,
    )
    return result.model_dump(exclude_none=True)


@mcp.tool()
def create_change_set(
    name: str,
    target_object_type: str,
    description: str | None = None,
    base_branch: str | None = None,
    changes: list[dict[str, Any]] | None = None,
    service=Depends(_change_sets_editor_service),
) -> dict[str, Any]:
    """Create a change set for scenario-based write-backs."""

    request = ChangeSetCreateRequest(
        name=name,
        targetObjectType=target_object_type,
        description=description,
        baseBranch=base_branch,
        changes=list(changes or []),
    )
    record = service.create_change_set(request)
    return _serialize_change_set(service, record)


@mcp.tool()
def list_change_sets(
    status: str | None = None,
    service=Depends(_change_sets_editor_service),
) -> list[dict[str, Any]]:
    """List change sets with optional status filter."""

    items = service.list_change_sets(status)
    return [_serialize_change_set(service, it) for it in items]


@mcp.tool()
def approve_change_set(
    change_set_rid: str,
    commit_message: str | None = None,
    approved_by: str | None = None,
    service=Depends(_change_sets_admin_service),
) -> dict[str, Any]:
    """Approve a change set and advance its dataset branch."""

    request = ChangeSetApproveRequest(approvedBy=approved_by, commitMessage=commit_message)
    record = service.approve_change_set(change_set_rid, request)
    return _serialize_change_set(service, record)


@mcp.tool()
def get_object(
    object_type_api_name: str,
    pk_value: str,
    service=Depends(_instances_service),
) -> dict[str, Any]:
    """Fetch a single object instance by ObjectType and primary key."""

    result = service.get_object(object_type_api_name, pk_value)
    if result is None:
        raise ValueError(f"Object '{object_type_api_name}:{pk_value}' not found")
    return result.model_dump(exclude_none=True)


@mcp.tool()
def upsert_object(
    object_type_api_name: str,
    pk_value: str,
    body: ObjectUpsertRequest,
    service=Depends(_instances_editor_service),
) -> dict[str, Any]:
    """Create or update an object instance with the provided properties."""

    result = service.upsert_object(object_type_api_name, pk_value, body)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def delete_object(
    object_type_api_name: str,
    pk_value: str,
    service=Depends(_instances_editor_service),
) -> dict[str, Any]:
    """Delete an object instance identified by ObjectType and primary key."""

    deleted = service.delete_object(object_type_api_name, pk_value)
    if not deleted:
        raise ValueError(f"Object '{object_type_api_name}:{pk_value}' not found")
    return {"status": "deleted", "objectType": object_type_api_name, "pkValue": pk_value}


@mcp.tool()
def create_link(
    link_type_api_name: str,
    body: LinkCreateRequest,
    service=Depends(_linked_objects_editor_service),
) -> dict[str, Any]:
    """Create a link between two objects following the LinkType definition."""

    result = service.create_link(link_type_api_name, body)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def get_link(
    link_type_api_name: str,
    from_pk: str,
    to_pk: str,
    as_of: str | None = None,
    service=Depends(_linked_objects_service),
) -> dict[str, Any]:
    """Fetch a specific link between two objects."""

    as_of_dt = None
    if as_of:
        try:
            as_of_dt = datetime.fromisoformat(as_of)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Invalid 'as_of' timestamp; expected ISO 8601 format") from exc

    result = service.get_link(link_type_api_name, from_pk, to_pk, valid_at=as_of_dt)
    if result is None:
        raise ValueError(f"Link '{link_type_api_name}' from '{from_pk}' to '{to_pk}' not found")
    return result.model_dump(exclude_none=True)


@mcp.tool()
def list_links(
    link_type_api_name: str,
    from_pk: str | None = None,
    to_pk: str | None = None,
    as_of: str | None = None,
    service=Depends(_linked_objects_service),
) -> dict[str, Any]:
    """List links of a LinkType, optionally filtered by endpoints."""

    as_of_dt = None
    if as_of:
        try:
            as_of_dt = datetime.fromisoformat(as_of)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Invalid 'as_of' timestamp; expected ISO 8601 format") from exc

    result = service.list_links(link_type_api_name, from_pk=from_pk, to_pk=to_pk, valid_at=as_of_dt)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def delete_link(
    link_type_api_name: str,
    from_pk: str,
    to_pk: str,
    service=Depends(_linked_objects_editor_service),
) -> dict[str, Any]:
    """Delete a link between two objects."""

    deleted = service.delete_link(link_type_api_name, from_pk, to_pk)
    if not deleted:
        raise ValueError(f"Link '{link_type_api_name}' from '{from_pk}' to '{to_pk}' not found")
    return {
        "status": "deleted",
        "linkType": link_type_api_name,
        "fromPk": from_pk,
        "toPk": to_pk,
    }


@mcp.tool()
def search_objects(
    object_type_api_name: str,
    body: ObjectSearchRequest,
    service=Depends(_instances_service),
) -> dict[str, Any]:
    """Search for object instances using the Ontologia query DSL."""

    result = service.search_objects(object_type_api_name, body)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def aggregate_objects(
    body: AggregateRequest,
    service=Depends(_analytics_service),
) -> dict[str, Any]:
    """Run aggregate metrics (count/sum/avg) with optional grouping over objects."""

    result = service.aggregate(body)
    return result.model_dump(exclude_none=True)


@mcp.tool()
def upsert_dataset(
    api_name: str,
    schema: DatasetPutRequest,
    service=Depends(_datacatalog_service),
) -> dict[str, Any]:
    """Create or update a dataset in the Data Catalog."""

    dataset = service.upsert_dataset(
        api_name,
        source_type=schema.sourceType,
        source_identifier=schema.sourceIdentifier,
        display_name=schema.displayName,
        schema_definition=schema.schemaDefinition,
    )
    return dataset.model_dump(exclude_none=True)


@mcp.tool()
def list_datasets(
    service=Depends(_datacatalog_read_service),
) -> list[dict[str, Any]]:
    """List datasets registered in the Data Catalog for the current ontology."""

    datasets = service.list_datasets()
    return [ds.model_dump(exclude_none=True) for ds in datasets]


@mcp.tool()
def list_actions(
    object_type_api_name: str,
    pk_value: str,
    service=Depends(_actions_viewer_service),
) -> list[dict[str, Any]]:
    """List available Actions for a specific object instance."""

    context = {
        "user": {
            "id": service.principal.user_id if service.principal else "agent",
            "roles": service.principal.roles if service.principal else [],
            "tenants": service.principal.tenants if service.principal else {},
        }
    }
    actions = service.list_available_actions(object_type_api_name, pk_value, context=context)
    out: list[dict[str, Any]] = []
    for act in actions:
        params = {
            key: {
                "dataType": str(value.get("dataType")),
                "displayName": str(value.get("displayName")),
                "description": value.get("description"),
                "required": bool(value.get("required", True)),
            }
            for key, value in (act.parameters or {}).items()
        }
        out.append(
            {
                "apiName": act.api_name,
                "rid": getattr(act, "rid", None),
                "displayName": getattr(act, "display_name", act.api_name),
                "description": getattr(act, "description", None),
                "targetObjectType": act.target_object_type_api_name,
                "parameters": params,
            }
        )
    return out


@mcp.tool()
async def execute_action(
    object_type_api_name: str,
    pk_value: str,
    action_api_name: str,
    body: ActionExecuteRequest,
    service=Depends(_actions_editor_service),
) -> dict[str, Any]:
    """Execute an Action for an object, honoring Temporal configuration when enabled."""

    settings = get_settings()
    use_temporal = settings.use_temporal_actions or os.getenv("USE_TEMPORAL_ACTIONS", "0") in (
        "1",
        "true",
        "True",
    )
    params = dict(body.parameters or {})
    user_ctx = {
        "id": service.principal.user_id if service.principal else "agent",
        "roles": service.principal.roles if service.principal else [],
        "tenants": service.principal.tenants if service.principal else {},
    }
    if use_temporal:
        result = await service.execute_action_async(
            object_type_api_name,
            pk_value,
            action_api_name,
            params,
            user=user_ctx,
        )
    else:
        result = service.execute_action(
            object_type_api_name,
            pk_value,
            action_api_name,
            params,
            user=user_ctx,
        )
    return result


def _relative_to_project(path: Path) -> str:
    project = _project_root()
    try:
        return str(path.relative_to(project))
    except ValueError:  # pragma: no cover - defensive
        return str(path)


def _pipeline_command() -> list[str]:
    override = os.getenv("ONTOLOGIA_PIPELINE_COMMAND")
    if override:
        return override.split()
    return ["ontologia-cli", "pipeline", "run"]


def _write_text_file(path: Path, content: str) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.rstrip("\n") + "\n"
    path.write_text(normalized, encoding="utf-8")
    return {
        "path": _relative_to_project(path),
        "bytes_written": len(normalized.encode("utf-8")),
    }


@mcp.tool()
def analyze_relational_schema(
    connection_url: str,
    *,
    schema: str | None = None,
    include_views: bool = False,
) -> dict[str, Any]:
    """Inspect relational schema metadata (tables + foreign keys).

    Parameters
    ----------
    connection_url: SQLAlchemy connection URL (e.g. sqlite:///file.db).
    schema: Optional schema/catalog to scope inspection.
    include_views: Whether to enumerate view names in the response.
    """

    try:
        with _engine(connection_url) as engine:
            inspector = inspect(engine)

            tables: dict[str, list[str]] = {}
            for table_name in inspector.get_table_names(schema=schema):
                cols = inspector.get_columns(table_name, schema=schema)
                tables[table_name] = [str(col.get("name")) for col in cols]

            views: dict[str, list[str]] = {}
            if include_views:
                for view_name in inspector.get_view_names(schema=schema):
                    cols = inspector.get_columns(view_name, schema=schema)
                    views[view_name] = [str(col.get("name")) for col in cols]

            foreign_keys: list[dict[str, Any]] = []
            for table_name in tables:
                for fk in inspector.get_foreign_keys(table_name, schema=schema):
                    foreign_keys.append(
                        {
                            "fromTable": table_name,
                            "fromColumns": list(fk.get("constrained_columns") or []),
                            "toTable": fk.get("referred_table"),
                            "toColumns": list(fk.get("referred_columns") or []),
                            "name": fk.get("name"),
                            "schema": schema,
                            "referredSchema": fk.get("referred_schema"),
                        }
                    )

            payload: dict[str, Any] = {
                "tables": tables,
                "foreignKeys": foreign_keys,
            }
            if include_views:
                payload["views"] = views
            return payload
    except Exception as exc:  # pragma: no cover - defensive error mapping
        raise ValueError(f"Failed to analyze relational schema: {exc}") from exc


@mcp.tool()
def stream_ontology_events(
    duration_seconds: float = 5.0,
    *,
    max_events: int = 100,
    object_types: list[str] | None = None,
    entity_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Collect real-time events from the in-memory runtime for a bounded window."""

    if max_events <= 0:
        return {
            "events": [],
            "count": 0,
            "durationSeconds": duration_seconds,
            "objectTypes": object_types or [],
            "entityIds": entity_ids or [],
        }

    object_type_set = {str(item) for item in object_types} if object_types else None
    entity_id_set = {str(item) for item in entity_ids} if entity_ids else None

    events = _run_sync(
        _collect_realtime_events(duration_seconds, max_events, object_type_set, entity_id_set)
    )
    return {
        "events": events,
        "count": len(events),
        "durationSeconds": duration_seconds,
        "objectTypes": sorted(object_type_set) if object_type_set else [],
        "entityIds": sorted(entity_id_set) if entity_id_set else [],
    }


@mcp.tool()
def analyze_data_source(
    source_path: str,
    sample_size: int = 100,
    service=Depends(_data_analysis_service),
) -> dict[str, Any]:
    """Profile a tabular data source (CSV/TSV/Parquet) for ontology planning."""

    resolved_root = _data_root()
    resolved_path = _resolve_path_in_root(source_path, resolved_root)
    profile = service.profile_source(resolved_path, sample_size=sample_size)
    profile.update(
        {
            "base_directory": str(resolved_root),
            "resolved_path": str(resolved_path),
        }
    )
    return profile


@mcp.tool()
def analyze_sql_table(
    connection_url: str,
    table_name: str,
    sample_size: int = 100,
    service=Depends(_data_analysis_service),
) -> dict[str, Any]:
    """Profile a relational database table accessible via SQLAlchemy."""

    return service.profile_sql_table(
        connection_url,
        table_name,
        sample_size=sample_size,
    )


@mcp.tool()
def analyze_rest_endpoint(
    url: str,
    sample_size: int = 100,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    array_path: str | None = None,
    timeout_seconds: float = 30.0,
    service=Depends(_data_analysis_service),
) -> dict[str, Any]:
    """Profile JSON responses served by REST endpoints."""

    return service.profile_rest_endpoint(
        url,
        sample_size=sample_size,
        method=method,
        headers=headers,
        array_path=array_path,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def plan_schema_changes(
    definitions_dir: str | None = None,
    *,
    include_impact: bool = False,
    include_dependencies: bool = False,
    service=Depends(_schema_evolution_service),
) -> dict[str, Any]:
    path = Path(definitions_dir).resolve() if definitions_dir else None
    return service.plan_schema_changes(
        definitions_dir=path,
        include_impact=include_impact,
        include_dependencies=include_dependencies,
    )


@mcp.tool()
def apply_schema_changes(
    definitions_dir: str | None = None,
    *,
    allow_destructive: bool = False,
    regenerate_sdk: bool = False,
    service=Depends(_schema_evolution_service),
) -> dict[str, Any]:
    path = Path(definitions_dir).resolve() if definitions_dir else None
    return service.apply_schema_changes(
        definitions_dir=path,
        allow_destructive=allow_destructive,
        regenerate_sdk=regenerate_sdk,
    )


@mcp.tool()
def list_migration_tasks(
    status: str | None = None,
    service=Depends(_schema_evolution_service),
) -> list[dict[str, Any]]:
    return service.list_migration_tasks(status=status)


@mcp.tool()
def update_migration_task(
    task_rid: str,
    status: str,
    error_message: str | None = None,
    service=Depends(_schema_evolution_service),
) -> dict[str, Any]:
    return service.update_migration_task(task_rid, status=status, error_message=error_message)


@mcp.tool()
def run_migration_task(
    task_rid: str,
    *,
    dry_run: bool = False,
    batch_size: int | None = None,
    ctx=Depends(_migration_execution_context),
) -> dict[str, Any]:
    service, tenant_service, tenant_instance = ctx
    return service.run_task(
        service=tenant_service,
        instance=tenant_instance,
        task_rid=task_rid,
        dry_run=dry_run,
        batch_size=batch_size,
    )


@mcp.tool()
def run_pending_migrations(
    *,
    dry_run: bool = False,
    limit: int | None = None,
    batch_size: int | None = None,
    ctx=Depends(_migration_execution_context),
) -> list[dict[str, Any]]:
    service, tenant_service, tenant_instance = ctx
    return service.run_pending_tasks(
        service=tenant_service,
        instance=tenant_instance,
        dry_run=dry_run,
        limit=limit,
        batch_size=batch_size,
    )


@mcp.tool()
def write_dbt_model(
    model_path: str,
    sql: str,
) -> dict[str, Any]:
    """Write or overwrite a dbt model file within the project models directory."""

    root = _dbt_models_root()
    resolved = _resolve_path_in_root(model_path, root)
    return _write_text_file(resolved, sql)


@mcp.tool()
def write_dbt_schema(
    schema_path: str,
    yaml: str,
) -> dict[str, Any]:
    """Write or overwrite a dbt schema.yml file within the project models directory."""

    root = _dbt_models_root()
    resolved = _resolve_path_in_root(schema_path, root)
    if resolved.suffix not in {".yml", ".yaml"}:
        raise ValueError("dbt schema files must end with .yml or .yaml")
    return _write_text_file(resolved, yaml)


@mcp.tool()
def run_pipeline(timeout_seconds: int = 1800) -> dict[str, Any]:
    """Execute the Ontologia data pipeline and return captured logs."""

    command = _pipeline_command()
    env = os.environ.copy()
    env.setdefault("ONTOLOGIA_CONFIG_ROOT", str(_project_root()))
    try:
        result = subprocess.run(  # noqa: S603
            command,
            cwd=_project_root(),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - defensive
        raise RuntimeError(
            f"Unable to execute pipeline command {' '.join(command)}: executable not found"
        ) from exc
    except subprocess.TimeoutExpired as exc:  # pragma: no cover - defensive
        raise TimeoutError(
            f"Pipeline command {' '.join(command)} timed out after {timeout_seconds}s"
        ) from exc

    status = "ok" if result.returncode == 0 else "error"
    return {
        "status": status,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": command,
    }


app = mcp.http_app()
