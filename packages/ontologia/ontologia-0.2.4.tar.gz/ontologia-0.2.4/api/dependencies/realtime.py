from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path

from sqlmodel import Session

from api.core.database import engine
from api.services.instances_service import InstancesService
from ontologia_realtime.decision import DecisionConfig
from ontologia_realtime.enrichment import RealTimeEnricher
from ontologia_realtime.entity_manager import EntityManager
from ontologia_realtime.replication import ReplicationConfig, ReplicationPeer, TLSConfig
from ontologia_realtime.runtime import RealTimeRuntime, RealTimeRuntimeConfig
from ontologia_realtime.schema import SchemaRegistry


class GraphContextProvider:
    """Fetches historical state from the analytical store."""

    def __init__(
        self,
        session_factory: Callable[[], Session],
        *,
        service: str | None = None,
        instance: str | None = None,
        component_name: str = "historical",
    ) -> None:
        self._session_factory = session_factory
        self._service = service or os.getenv("REALTIME_ONTOLOGY_SERVICE", "ontology")
        self._instance = instance or os.getenv("REALTIME_ONTOLOGY_INSTANCE", "default")
        self._component = component_name

    async def fetch(self, snapshot):
        def _load():
            with self._session_factory() as session:
                svc = InstancesService(
                    session,
                    service=self._service,
                    instance=self._instance,
                )
                obj = svc.get_object(snapshot.object_type, snapshot.entity_id)
                if obj is None:
                    return {}
                return {self._component: dict(obj.properties or {})}

        return await asyncio.to_thread(_load)


@lru_cache(maxsize=1)
def get_schema_registry() -> SchemaRegistry:
    return SchemaRegistry()


def _parse_peers(raw: str) -> tuple[ReplicationPeer, ...]:
    peers: list[ReplicationPeer] = []
    for item in [entry.strip() for entry in raw.split(",") if entry.strip()]:
        if ":" in item:
            host, port_raw = item.split(":", 1)
            peers.append(ReplicationPeer(host=host, port=int(port_raw)))
        else:
            peers.append(ReplicationPeer(host=item, port=19090))
    return tuple(peers)


def _load_tls_config() -> TLSConfig | None:
    if os.getenv("REALTIME_TLS_ENABLED", "0") not in {"1", "true", "True"}:
        return None
    return TLSConfig(
        root_cert=os.getenv("REALTIME_TLS_ROOT_CERT"),
        client_cert=os.getenv("REALTIME_TLS_CLIENT_CERT"),
        client_key=os.getenv("REALTIME_TLS_CLIENT_KEY"),
    )


def _load_decision_config() -> DecisionConfig | None:
    rules_path = os.getenv("REALTIME_DECISION_RULES_PATH")
    if not rules_path:
        return None
    audit_path = os.getenv("REALTIME_DECISION_AUDIT_PATH")
    actions_path = os.getenv("REALTIME_DECISION_ACTIONS_PATH")
    webhook_url = os.getenv("REALTIME_DECISION_WEBHOOK_URL")
    webhook_timeout_raw = os.getenv("REALTIME_DECISION_WEBHOOK_TIMEOUT", "5")
    try:
        webhook_timeout = float(webhook_timeout_raw)
    except ValueError:
        webhook_timeout = 5.0
    ignore_replicated = os.getenv("REALTIME_DECISION_IGNORE_REPLICATED", "1").lower() not in {
        "0",
        "false",
        "no",
    }
    return DecisionConfig(
        rules_path=Path(rules_path),
        audit_log_path=Path(audit_path) if audit_path else None,
        actions_log_path=Path(actions_path) if actions_path else None,
        webhook_url=webhook_url,
        webhook_timeout=webhook_timeout,
        ignore_replicated_events=ignore_replicated,
    )


@lru_cache(maxsize=1)
def get_runtime() -> RealTimeRuntime:
    node_id = os.getenv("REALTIME_NODE_ID") or os.getenv("HOSTNAME") or "default-node"
    store_path = Path(os.getenv("REALTIME_STORE_PATH", "data/realtime/store.db"))
    journal_path = Path(os.getenv("REALTIME_JOURNAL_PATH", "data/realtime/journal.jsonl"))
    prune_interval = int(os.getenv("REALTIME_PRUNE_INTERVAL", "5"))
    peers_raw = os.getenv("REALTIME_PEERS", "")
    peers = _parse_peers(peers_raw)
    replication = ReplicationConfig(node_id=node_id, peers=peers) if peers else None
    config = RealTimeRuntimeConfig(
        node_id=node_id,
        store_path=store_path,
        journal_path=journal_path,
        prune_interval_seconds=prune_interval,
        replication=replication,
        tls=_load_tls_config(),
        decision=_load_decision_config(),
    )
    return RealTimeRuntime(config, schema_registry=get_schema_registry())


@lru_cache(maxsize=1)
def get_entity_manager() -> EntityManager:
    return get_runtime().manager


@lru_cache(maxsize=1)
def get_context_provider() -> GraphContextProvider:
    return GraphContextProvider(lambda: Session(engine))


async def ensure_runtime_started() -> None:
    runtime = get_runtime()
    await runtime.start()


async def shutdown_runtime() -> None:
    runtime = get_runtime()
    await runtime.stop()


async def run_realtime_enricher(stop_event: asyncio.Event) -> None:
    await ensure_runtime_started()
    manager = get_entity_manager()
    provider = get_context_provider()
    enricher = RealTimeEnricher(manager, provider)
    await enricher.run(stop_event)
