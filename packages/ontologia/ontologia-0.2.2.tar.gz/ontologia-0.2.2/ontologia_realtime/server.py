from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import grpc
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from ontologia_realtime.entity_manager import EntityManager, EntitySnapshot
from ontologia_realtime.proto import realtime_pb2, realtime_pb2_grpc
from ontologia_realtime.schema import SchemaRegistry

logger = logging.getLogger(__name__)


def _dict_to_struct(data: dict) -> Struct:
    struct = Struct()
    struct.update(data)
    return struct


def _snapshot_to_proto(
    snapshot: EntitySnapshot, *, tombstone: bool = False
) -> realtime_pb2.EntityUpdate:
    msg = realtime_pb2.EntityUpdate()
    msg.entity_id = snapshot.entity_id
    msg.object_type = snapshot.object_type
    msg.provenance = snapshot.provenance
    msg.expires_at.FromDatetime(snapshot.expires_at)
    msg.updated_at.FromDatetime(snapshot.updated_at)
    msg.tombstone = tombstone or snapshot.components == {}
    if msg.tombstone:
        msg.metadata["tombstone"] = "true"
    ttl_seconds = max((snapshot.expires_at - snapshot.updated_at).total_seconds(), 0.0)
    msg.metadata["ttl_seconds"] = f"{ttl_seconds:.6f}"
    for name, payload in snapshot.components.items():
        msg.components[name].CopyFrom(_dict_to_struct(payload))
    return msg


def _proto_components_to_dict(components: dict[str, Struct]) -> dict[str, dict[str, object]]:
    return {
        name: json_format.MessageToDict(struct_pb, preserving_proto_field_name=True)
        for name, struct_pb in components.items()
    }


def _ttl_from_request(ttl_seconds: float) -> timedelta:
    if ttl_seconds <= 0:
        raise grpc.RpcError(grpc.StatusCode.INVALID_ARGUMENT, "ttl_seconds must be positive")
    return timedelta(seconds=ttl_seconds)


class RealTimeEntityService(realtime_pb2_grpc.RealTimeEntityServiceServicer):
    def __init__(self, manager: EntityManager) -> None:
        self._manager = manager

    async def UpsertEntity(  # type: ignore[override]  # noqa: N802
        self, request: realtime_pb2.UpsertEntityRequest, context: grpc.aio.ServicerContext
    ) -> realtime_pb2.EntityAck:
        components = _proto_components_to_dict(dict(request.components))
        ttl = _ttl_from_request(request.ttl_seconds)
        metadata = dict(request.metadata)
        snapshot = await self._manager.upsert(
            request.entity_id,
            object_type=request.object_type,
            provenance=request.provenance,
            ttl=ttl,
            components=components,
            metadata=metadata,
        )
        ack = realtime_pb2.EntityAck(entity_id=request.entity_id)
        ack.updated_at.FromDatetime(snapshot.updated_at)
        return ack

    async def RemoveEntity(  # type: ignore[override]  # noqa: N802
        self, request: realtime_pb2.RemoveEntityRequest, context: grpc.aio.ServicerContext
    ) -> realtime_pb2.EntityAck:
        metadata = dict(request.metadata)
        await self._manager.remove(request.entity_id, metadata=metadata)
        ack = realtime_pb2.EntityAck(entity_id=request.entity_id)
        ack.updated_at.FromDatetime(datetime.now(UTC))
        return ack

    async def StreamEntities(  # type: ignore[override]  # noqa: N802
        self, request: realtime_pb2.StreamEntitiesRequest, context: grpc.aio.ServicerContext
    ) -> AsyncIterator[realtime_pb2.EntityUpdate]:
        object_types = set(request.object_types) if request.object_types else None
        subscriber_id, queue = self._manager.subscribe(object_types=object_types)
        try:
            while True:
                snapshot = await queue.get()
                if snapshot is None:
                    break
                yield _snapshot_to_proto(snapshot)
        finally:
            self._manager.unsubscribe(subscriber_id)

    async def ListEntities(  # type: ignore[override]  # noqa: N802
        self, request: realtime_pb2.ListEntitiesRequest, context: grpc.aio.ServicerContext
    ) -> realtime_pb2.ListEntitiesResponse:
        object_types = set(request.object_types) if request.object_types else None
        entities = await self._manager.list_entities()
        response = realtime_pb2.ListEntitiesResponse()
        for snapshot in entities:
            if object_types and snapshot.object_type not in object_types:
                continue
            response.entities.append(_snapshot_to_proto(snapshot))
        return response


@dataclass
class RealTimeServerConfig:
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 19090
    prune_interval_seconds: int = 5


async def _prune_loop(manager: EntityManager, interval: int) -> None:
    while True:
        try:
            pruned = await manager.prune_expired()
            if pruned:
                logger.debug("Pruned %s expired entities", pruned)
        except Exception:  # pragma: no cover - safety guard for background task
            logger.exception("Error pruning expired entities")
        await asyncio.sleep(interval)


async def serve(
    config: RealTimeServerConfig,
    *,
    manager: EntityManager | None = None,
    schema_registry: SchemaRegistry | None = None,
) -> None:
    server = grpc.aio.server()
    manager = manager or EntityManager(schema_registry=schema_registry)
    realtime_pb2_grpc.add_RealTimeEntityServiceServicer_to_server(
        RealTimeEntityService(manager), server
    )
    listen_addr = f"{config.host}:{config.port}"
    server.add_insecure_port(listen_addr)
    logger.info("Starting real-time gRPC server on %s", listen_addr)
    await server.start()
    prune_task = asyncio.create_task(_prune_loop(manager, config.prune_interval_seconds))
    try:
        await server.wait_for_termination()
    finally:
        prune_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await prune_task
