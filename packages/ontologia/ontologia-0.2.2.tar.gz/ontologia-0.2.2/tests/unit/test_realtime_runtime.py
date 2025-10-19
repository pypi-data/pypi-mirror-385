from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from ontologia_realtime.entity_manager import EntityManager
from ontologia_realtime.journal import (
    CompositeEntityJournal,
    EntityEvent,
    EntityStoreJournal,
    EventStreamJournal,
)
from ontologia_realtime.replication import EntityReplicator, ReplicationConfig, ReplicationPeer
from ontologia_realtime.runtime import RealTimeRuntime, RealTimeRuntimeConfig
from ontologia_realtime.storage import SQLiteEntityStore

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_sqlite_entity_store_persists_state(tmp_path):
    store_path = tmp_path / "store.db"
    store = SQLiteEntityStore(store_path)
    journal = CompositeEntityJournal([EntityStoreJournal(store)])
    manager = EntityManager(journal=journal)

    await manager.upsert(
        "entity-1",
        object_type="widget",
        provenance="ingest",
        ttl=timedelta(seconds=30),
        components={"core": {"value": 1}},
    )

    snapshots = await store.load_snapshots()
    assert len(snapshots) == 1
    assert snapshots[0].components["core"]["value"] == 1

    await manager.remove("entity-1")
    snapshots = await store.load_snapshots()
    assert snapshots == []

    await manager.upsert(
        "entity-1",
        object_type="widget",
        provenance="ingest",
        ttl=timedelta(seconds=30),
        components={"core": {"value": 1}},
    )

    new_store = SQLiteEntityStore(store_path)
    new_manager = EntityManager(journal=CompositeEntityJournal([EntityStoreJournal(new_store)]))
    persisted = await new_store.load_snapshots()
    await new_manager.load_snapshots(persisted)
    entity = await new_manager.get_entity("entity-1")
    assert entity is not None
    assert entity.components["core"]["value"] == 1


class _FakeTransport:
    def __init__(self, peer: ReplicationPeer, tls):
        self.peer = peer
        self.tls = tls
        self.upserts: list[tuple[str, float]] = []
        self.removals: list[str] = []
        self._upsert_event = asyncio.Event()

    async def upsert(self, request):
        self.upserts.append((request.entity_id, request.ttl_seconds))
        self._upsert_event.set()

    async def remove(self, request):
        self.removals.append(request.entity_id)

    async def close(self) -> None:
        return None

    async def wait_for_upsert(self) -> None:
        await asyncio.wait_for(self._upsert_event.wait(), timeout=1)
        self._upsert_event.clear()


async def test_entity_replicator_respects_replication_metadata():
    stream = EventStreamJournal(maxsize=16)
    peer = ReplicationPeer(host="localhost", port=19090)
    config = ReplicationConfig(node_id="node-a", peers=(peer,), send_timeout_seconds=0.5)
    fake_transport = _FakeTransport(peer, None)

    replicator = EntityReplicator(
        stream,
        config,
        transport_factory=lambda _peer, _tls: fake_transport,
    )
    await replicator.start()

    now = datetime.now(UTC)
    event = EntityEvent(
        sequence=1,
        event_type="upsert",
        entity_id="entity-1",
        object_type="widget",
        provenance="ingest",
        components={"core": {"value": 1}},
        expires_at=now + timedelta(seconds=30),
        updated_at=now,
        metadata={},
    )
    await stream.record(event)
    await fake_transport.wait_for_upsert()
    assert fake_transport.upserts

    remote_event = EntityEvent(
        sequence=2,
        event_type="upsert",
        entity_id="entity-2",
        object_type="widget",
        provenance="replica",
        components={"core": {"value": 2}},
        expires_at=now + timedelta(seconds=60),
        updated_at=now,
        metadata={"replicated_from": "node-b"},
    )
    await stream.record(remote_event)
    await asyncio.sleep(0.05)
    assert all(entity_id != "entity-2" for entity_id, _ttl in fake_transport.upserts)

    await replicator.stop()


async def test_event_stream_distributes_to_multiple_subscribers():
    stream = EventStreamJournal(maxsize=4)
    queue_a = stream.queue()
    queue_b = stream.queue()

    now = datetime.now(UTC)
    event = EntityEvent(
        sequence=1,
        event_type="upsert",
        entity_id="entity-1",
        object_type="widget",
        provenance="ingest",
        components={"core": {"value": 1}},
        expires_at=now + timedelta(seconds=30),
        updated_at=now,
        metadata={},
    )
    await stream.record(event)
    received_a = await asyncio.wait_for(queue_a.get(), timeout=1)
    received_b = await asyncio.wait_for(queue_b.get(), timeout=1)
    assert received_a.sequence == event.sequence
    assert received_b.sequence == event.sequence

    stream.unsubscribe(queue_a)
    follow_up = event.__class__(
        sequence=2,
        event_type="upsert",
        entity_id="entity-2",
        object_type="widget",
        provenance="ingest",
        components={"core": {"value": 2}},
        expires_at=now + timedelta(seconds=40),
        updated_at=now,
        metadata={},
    )
    await stream.record(follow_up)
    received_b_follow_up = await asyncio.wait_for(queue_b.get(), timeout=1)
    assert received_b_follow_up.sequence == 2


async def test_runtime_recent_events_and_subscription(tmp_path):
    config = RealTimeRuntimeConfig(
        node_id="node-test",
        store_path=tmp_path / "store.db",
        journal_path=tmp_path / "journal.jsonl",
    )
    runtime = RealTimeRuntime(config)

    queue = runtime.subscribe_events()
    await runtime.manager.upsert(
        "entity-1",
        object_type="widget",
        provenance="ingest",
        ttl=timedelta(seconds=60),
        components={"core": {"value": 1}},
    )

    event = await asyncio.wait_for(queue.get(), timeout=1)
    assert event.entity_id == "entity-1"

    runtime.unsubscribe_events(queue)

    events = await runtime.get_recent_events(limit=5)
    assert events
    ids = {item.entity_id for item in events}
    assert "entity-1" in ids
