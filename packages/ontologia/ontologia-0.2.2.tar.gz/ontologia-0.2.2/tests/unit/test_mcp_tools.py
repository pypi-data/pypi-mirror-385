import asyncio
import importlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

import pytest
import yaml
from sqlmodel import Session, select

from api.services.data_analysis_service import DataAnalysisService
from api.services.instances_service import InstancesService
from api.services.metamodel_service import MetamodelService
from api.services.migration_execution_service import MigrationExecutionService
from api.services.schema_evolution_service import SchemaEvolutionService
from api.v2.schemas.instances import ObjectUpsertRequest
from api.v2.schemas.metamodel import ObjectTypePutRequest, PropertyDefinition
from ontologia.domain.metamodels.migrations.migration_task import MigrationTask, MigrationTaskStatus


@pytest.fixture
def reload_mcp(monkeypatch):
    def _reload(**env: Any):
        for key, value in env.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, str(value))
        import api.mcp_router as mcp_router

        return importlib.reload(mcp_router)

    return _reload


def test_analyze_data_source_uses_authorized_root(tmp_path: Path, reload_mcp) -> None:
    module = reload_mcp(ONTOLOGIA_AGENT_DATA_ROOT=tmp_path)
    data_path = tmp_path / "sales.csv"
    data_path.write_text(
        "transaction_id,product_sku\n1,SKU-1\n2,SKU-2\n",
        encoding="utf-8",
    )

    profile = module.analyze_data_source.fn(
        source_path="sales.csv",
        sample_size=10,
        service=DataAnalysisService(),
    )

    assert profile["resolved_path"] == str(data_path)
    assert profile["rows_profiled"] == 2
    assert {col["name"] for col in profile["columns"]} == {"transaction_id", "product_sku"}


def test_analyze_data_source_rejects_escape(tmp_path: Path, reload_mcp) -> None:
    module = reload_mcp(ONTOLOGIA_AGENT_DATA_ROOT=tmp_path)
    with pytest.raises(ValueError):
        module.analyze_data_source.fn(
            source_path="../outside.csv",
            sample_size=5,
            service=DataAnalysisService(),
        )


def test_analyze_relational_schema_tool(tmp_path: Path, reload_mcp) -> None:
    db_path = tmp_path / "rel.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT
        );
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            total REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
        );
        """
    )
    conn.close()

    module = reload_mcp()
    payload = module.analyze_relational_schema.fn(
        connection_url=f"sqlite:///{db_path}",
    )

    assert payload["tables"]["customers"] == ["customer_id", "name"]
    assert payload["tables"]["orders"] == ["order_id", "customer_id", "total"]
    fk = payload["foreignKeys"][0]
    assert fk["fromTable"] == "orders"
    assert fk["fromColumns"] == ["customer_id"]
    assert fk["toTable"] == "customers"
    assert fk["toColumns"] == ["customer_id"]


def test_stream_ontology_events_tool(monkeypatch, reload_mcp) -> None:
    module = reload_mcp()

    class DummyEvent:
        sequence = 1
        event_type = "UPSERT"
        entity_id = "customer:1"
        object_type = "customer"
        provenance = {"source": "test"}
        updated_at = datetime.now(UTC)
        expires_at = None
        components = {"properties": {"name": "Alice"}}
        metadata = {"foo": "bar"}

    class FakeRuntime:
        def __init__(self) -> None:
            self.unsubscribed = False

        def subscribe_events(self):  # noqa: D401
            queue = asyncio.Queue()
            queue.put_nowait(DummyEvent())
            self._queue = queue
            return queue

        def unsubscribe_events(self, queue):  # noqa: D401
            if queue is getattr(self, "_queue", None):
                self.unsubscribed = True

    async def fake_ensure_runtime_started():  # noqa: D401
        return None

    runtime = FakeRuntime()
    monkeypatch.setattr(module, "ensure_runtime_started", fake_ensure_runtime_started)
    monkeypatch.setattr(module, "get_runtime", lambda: runtime)

    result = module.stream_ontology_events.fn(duration_seconds=0.1, max_events=5)

    assert result["count"] == 1
    assert result["events"][0]["entityId"] == "customer:1"
    assert runtime.unsubscribed is True


def test_write_dbt_model_and_schema(tmp_path: Path, reload_mcp) -> None:
    module = reload_mcp(ONTOLOGIA_DBT_MODELS_ROOT=tmp_path)

    result_model = module.write_dbt_model.fn("gold/sales.sql", "select 1;")
    written_model = tmp_path / "gold" / "sales.sql"
    assert written_model.read_text(encoding="utf-8") == "select 1;\n"
    assert result_model["path"].endswith("gold/sales.sql")

    result_schema = module.write_dbt_schema.fn("gold/schema.yml", "version: 2")
    written_schema = tmp_path / "gold" / "schema.yml"
    assert written_schema.read_text(encoding="utf-8") == "version: 2\n"
    assert result_schema["path"].endswith("gold/schema.yml")

    with pytest.raises(ValueError):
        module.write_dbt_schema.fn("gold/schema.txt", "version: 2")


def test_run_pipeline_captures_output(monkeypatch, reload_mcp) -> None:
    module = reload_mcp()

    def fake_run(cmd, cwd, env, capture_output, text, timeout, check):  # noqa: D401
        assert cmd == module._pipeline_command()
        assert Path(cwd) == module._project_root()
        return CompletedProcess(cmd, 0, stdout="ok", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    result = module.run_pipeline.fn(timeout_seconds=5)
    assert result["status"] == "ok"
    assert result["stdout"] == "ok"


def test_analyze_sql_table_tool(tmp_path: Path, reload_mcp) -> None:
    module = reload_mcp()

    db_path = tmp_path / "example.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, code TEXT)")
        conn.executemany("INSERT INTO items (code) VALUES (?)", [("A",), ("B",)])
        conn.commit()
    finally:
        conn.close()

    profile = module.analyze_sql_table.fn(
        connection_url=f"sqlite:///{db_path}",
        table_name="items",
        sample_size=5,
        service=DataAnalysisService(),
    )

    assert profile["rows_profiled"] == 2
    assert {col["name"] for col in profile["columns"]} == {"id", "code"}


def test_analyze_rest_endpoint_tool(monkeypatch, reload_mcp) -> None:
    module = reload_mcp()

    class FakeResponse:
        def raise_for_status(self) -> None:  # noqa: D401 - simple stub
            return None

        def json(self) -> list[dict[str, Any]]:
            return [{"id": 1}, {"id": 2}, {"id": 3}]

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args, **kwargs) -> None:
            return None

        def request(self, method, url, headers=None):
            assert method == "GET"
            assert url == "https://example.com/items"
            return FakeResponse()

    monkeypatch.setattr(
        "api.services.data_analysis_service.httpx.Client",
        FakeClient,
    )

    profile = module.analyze_rest_endpoint.fn(
        url="https://example.com/items",
        sample_size=2,
        service=DataAnalysisService(),
    )

    assert profile["rows_profiled"] == 2


def test_plan_schema_changes_tool(tmp_path: Path, reload_mcp, session) -> None:
    module = reload_mcp()
    definitions_dir = tmp_path / "defs"
    definitions_dir.mkdir(parents=True, exist_ok=True)
    (definitions_dir / "object_types").mkdir()
    customer_path = definitions_dir / "object_types" / "customer.yml"
    with customer_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            {
                "apiName": "customer",
                "displayName": "Customer",
                "primaryKey": "id",
                "properties": {"id": {"dataType": "string", "displayName": "ID", "required": True}},
                "implements": [],
            },
            handle,
        )

    metamodel = MetamodelService(session, service="ontology", instance="default")
    evolution = SchemaEvolutionService(metamodel, definitions_dir=definitions_dir)

    plan = module.plan_schema_changes.fn(
        definitions_dir=str(definitions_dir),
        include_impact=False,
        include_dependencies=False,
        service=evolution,
    )

    assert plan["plan"]
    assert plan["plan"][0]["action"] == "create"


def test_apply_schema_changes_tool(tmp_path: Path, reload_mcp, session) -> None:
    module = reload_mcp()
    definitions_dir = tmp_path / "defs"
    (definitions_dir / "object_types").mkdir(parents=True, exist_ok=True)
    widget_path = definitions_dir / "object_types" / "widget.yml"
    with widget_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            {
                "apiName": "widget",
                "displayName": "Widget",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                    "name": {"dataType": "string", "displayName": "Name"},
                },
                "implements": [],
            },
            handle,
        )

    metamodel = MetamodelService(session, service="ontology", instance="default")
    evolution = SchemaEvolutionService(metamodel, definitions_dir=definitions_dir)

    result = module.apply_schema_changes.fn(
        definitions_dir=str(definitions_dir),
        allow_destructive=True,
        service=evolution,
    )

    assert result["applied"]
    assert metamodel.get_object_type("widget") is not None


def _prepare_migration_task(session: Session) -> MigrationTask:
    metamodel = MetamodelService(session, service="ontology", instance="default")
    instances = InstancesService(session, service="ontology", instance="default")

    metamodel.upsert_object_type(
        "customer",
        ObjectTypePutRequest(
            displayName="Customer",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "age": PropertyDefinition(dataType="integer", displayName="Age"),
            },
            implements=[],
        ),
    )

    instances.upsert_object(
        "customer",
        "100",
        ObjectUpsertRequest(properties={"age": 30}),
    )

    metamodel.upsert_object_type(
        "customer",
        ObjectTypePutRequest(
            displayName="Customer",
            description="",
            primaryKey="id",
            properties={
                "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
                "age": PropertyDefinition(dataType="string", displayName="Age"),
            },
            implements=[],
        ),
    )

    task = session.exec(select(MigrationTask)).first()
    assert task is not None
    return task


def test_run_migration_task_tool(session, reload_mcp) -> None:
    module = reload_mcp()
    task = _prepare_migration_task(session)

    executor = MigrationExecutionService(session)

    dry = module.run_migration_task.fn(
        task_rid=task.rid,
        dry_run=True,
        ctx=(executor, "ontology", "default"),
    )
    assert dry["failedCount"] == 0

    applied = module.run_migration_task.fn(
        task_rid=task.rid,
        dry_run=False,
        ctx=(executor, "ontology", "default"),
    )
    assert applied["failedCount"] == 0

    session.refresh(task)
    assert task.status == MigrationTaskStatus.COMPLETED


def test_run_pending_migrations_tool(session, reload_mcp) -> None:
    module = reload_mcp()
    task = _prepare_migration_task(session)
    executor = MigrationExecutionService(session)

    dry_results = module.run_pending_migrations.fn(
        dry_run=True,
        ctx=(executor, "ontology", "default"),
    )
    assert len(dry_results) == 1
    assert dry_results[0]["failedCount"] == 0

    applied_results = module.run_pending_migrations.fn(
        dry_run=False,
        ctx=(executor, "ontology", "default"),
    )
    assert len(applied_results) == 1
    assert applied_results[0]["failedCount"] == 0

    session.refresh(task)
    assert task.status == MigrationTaskStatus.COMPLETED
