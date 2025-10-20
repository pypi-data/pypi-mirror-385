from __future__ import annotations

import asyncio
import contextlib
from datetime import timedelta

import pytest
from google.protobuf.struct_pb2 import Struct

from api.services.hybrid_snapshot_service import HybridSnapshotService
from api.v2.schemas.instances import ObjectReadResponse
from ontologia_realtime.enrichment import RealTimeEnricher
from ontologia_realtime.entity_manager import EntityManager, EntitySnapshot
from ontologia_realtime.journal import InMemoryEntityJournal
from ontologia_realtime.proto import realtime_pb2
from ontologia_realtime.schema import ComponentSchema, SchemaRegistry
from ontologia_realtime.server import RealTimeEntityService


class _DummyContext:
    async def abort(self, code, details):  # pragma: no cover - should not be called in tests
        raise AssertionError((code, details))


def _run(coro):
    return asyncio.run(coro)


def test_entity_manager_upsert_notifies_subscribers():
    async def scenario():
        manager = EntityManager()
        subscriber_id, queue = manager.subscribe()
        try:
            snapshot = await manager.upsert(
                "entity-1",
                object_type="widget",
                provenance="ingest",
                ttl=timedelta(seconds=10),
                components={"core": {"value": 1}},
            )
            received = await asyncio.wait_for(queue.get(), timeout=0.1)
            assert received == snapshot
        finally:
            manager.unsubscribe(subscriber_id)

    _run(scenario())


def test_entity_manager_prune_sends_tombstone():
    async def scenario():
        manager = EntityManager()
        subscriber_id, queue = manager.subscribe()
        try:
            await manager.upsert(
                "entity-1",
                object_type="widget",
                provenance="ingest",
                ttl=timedelta(milliseconds=5),
                components={"core": {"value": 1}},
            )
            await asyncio.wait_for(queue.get(), timeout=0.1)
            await asyncio.sleep(0.01)
            pruned = await manager.prune_expired()
            assert pruned == 1
            tombstone = await asyncio.wait_for(queue.get(), timeout=0.1)
            assert tombstone.components == {}
            assert tombstone.provenance == "system"
        finally:
            manager.unsubscribe(subscriber_id)

    _run(scenario())


def test_schema_registry_normalizes_and_enforces_required_components():
    registry = SchemaRegistry()

    def normalizer(payload):
        return {"normalized": payload["raw"].upper()}

    registry.register(
        "widget",
        components={
            "core": ComponentSchema(required=True),
            "metrics": normalizer,
        },
    )

    normalized = registry.normalize_components(
        "widget",
        {
            "core": {"value": 1},
            "metrics": {"raw": "abc"},
        },
    )
    assert normalized["core"] == {"value": 1}
    assert normalized["metrics"] == {"normalized": "ABC"}


def test_schema_registry_missing_required_component():
    registry = SchemaRegistry()
    registry.register("widget", components={"core": ComponentSchema(required=True)})

    with pytest.raises(ValueError, match="Missing required components"):
        registry.normalize_components("widget", {})


def test_realtime_service_upsert_roundtrip():
    async def scenario():
        manager = EntityManager()
        service = RealTimeEntityService(manager)
        request = realtime_pb2.UpsertEntityRequest(
            entity_id="entity-1",
            object_type="widget",
            provenance="ingest",
            ttl_seconds=5,
        )
        struct = Struct()
        struct.update({"foo": "bar"})
        request.components["core"].CopyFrom(struct)

        ack = await service.UpsertEntity(request, _DummyContext())
        stored = await manager.get_entity("entity-1")
        assert stored is not None
        assert stored.components["core"]["foo"] == "bar"
        assert ack.entity_id == "entity-1"
        ack_dt = ack.updated_at.ToDatetime().replace(tzinfo=stored.updated_at.tzinfo)
        assert ack_dt == stored.updated_at

    _run(scenario())


def test_realtime_service_list_filters_object_types():
    async def scenario():
        manager = EntityManager()
        service = RealTimeEntityService(manager)
        await manager.upsert(
            "entity-1",
            object_type="widget",
            provenance="ingest",
            ttl=timedelta(seconds=5),
            components={},
        )
        await manager.upsert(
            "entity-2",
            object_type="gadget",
            provenance="ingest",
            ttl=timedelta(seconds=5),
            components={},
        )

        response = await service.ListEntities(
            realtime_pb2.ListEntitiesRequest(object_types=["widget"]),
            _DummyContext(),
        )
        assert len(response.entities) == 1
        assert response.entities[0].entity_id == "entity-1"

    _run(scenario())


def test_entity_manager_journal_and_patch_flow():
    async def scenario():
        journal = InMemoryEntityJournal()
        manager = EntityManager(journal=journal)
        await manager.upsert(
            "entity-1",
            object_type="widget",
            provenance="ingest",
            ttl=timedelta(seconds=5),
            components={"core": {"value": 1}},
        )
        await manager.apply_component_patch(
            "entity-1",
            components={"metrics": {"score": 95}},
            provenance="enrichment",
        )
        await manager.remove("entity-1")
        events = journal.events
        assert [event.event_type for event in events] == ["upsert", "patch", "remove"]
        assert events[1].components["metrics"]["score"] == 95

    _run(scenario())


def test_realtime_enricher_merges_context():
    async def scenario():
        journal = InMemoryEntityJournal()
        manager = EntityManager(journal=journal)

        enriched_event = asyncio.Event()

        class _Provider:
            async def fetch(self, snapshot):
                enriched_event.set()
                return {"historical": {"score": 10}}

        stop_event = asyncio.Event()
        enricher = RealTimeEnricher(manager, _Provider())
        task = asyncio.create_task(enricher.run(stop_event))
        try:
            await asyncio.sleep(0)
            await manager.upsert(
                "entity-1",
                object_type="widget",
                provenance="ingest",
                ttl=timedelta(seconds=5),
                components={"core": {"value": 1}},
            )

            await asyncio.wait_for(enriched_event.wait(), timeout=1.0)

            async def _wait_for_enrichment() -> EntitySnapshot | None:
                while True:
                    snap = await manager.get_entity("entity-1")
                    if snap and "historical" in snap.components:
                        return snap
                    await asyncio.sleep(0.02)

            snapshot = await asyncio.wait_for(_wait_for_enrichment(), timeout=1.0)
            assert snapshot is not None
            assert snapshot.components["historical"]["score"] == 10
        finally:
            stop_event.set()
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    _run(scenario())


def test_hybrid_snapshot_service_merges_historical_context():
    async def scenario():
        manager = EntityManager()

        class _Instances:
            def get_object(self, object_type_api_name, pk_value, *, as_of=None):
                return ObjectReadResponse(
                    rid=f"{object_type_api_name}:{pk_value}",
                    objectTypeApiName=object_type_api_name,
                    pkValue=pk_value,
                    properties={"legacy": 42},
                )

        service = HybridSnapshotService(manager, _Instances())
        await manager.upsert(
            "entity-1",
            object_type="widget",
            provenance="ingest",
            ttl=timedelta(seconds=5),
            components={"core": {"value": 1}},
        )
        view = await service.get_entity("entity-1")
        assert view is not None
        assert view.historical == {"legacy": 42}
        assert view.components["historical"]["legacy"] == 42

    _run(scenario())
