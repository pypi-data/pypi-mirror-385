from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

import grpc
from google.protobuf.struct_pb2 import Struct

from ontologia_realtime.journal import EntityEvent, EventStreamJournal
from ontologia_realtime.proto import realtime_pb2, realtime_pb2_grpc

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class TLSConfig:
    root_cert: str | None = None
    client_cert: str | None = None
    client_key: str | None = None


@dataclass(slots=True, frozen=True)
class ReplicationPeer:
    host: str
    port: int
    priority: int = 0
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass(slots=True, frozen=True)
class ReplicationConfig:
    node_id: str
    peers: Sequence[ReplicationPeer] = ()
    connect_timeout_seconds: float = 5.0
    send_timeout_seconds: float = 5.0
    metadata: Mapping[str, str] = field(default_factory=dict)


class PeerTransport:
    def __init__(self, peer: ReplicationPeer, tls: TLSConfig | None) -> None:
        self._peer = peer
        self._tls = tls
        self._channel: grpc.aio.Channel | None = None
        self._stub: realtime_pb2_grpc.RealTimeEntityServiceStub | None = None

    async def _ensure_stub(self) -> realtime_pb2_grpc.RealTimeEntityServiceStub:
        if self._stub is not None:
            return self._stub
        self._channel = await self._create_channel()
        self._stub = realtime_pb2_grpc.RealTimeEntityServiceStub(self._channel)
        return self._stub

    async def _create_channel(self) -> grpc.aio.Channel:
        if self._tls and (self._tls.root_cert or self._tls.client_cert):
            root_cert = None
            client_crt = None
            client_key = None
            if self._tls.root_cert:
                with open(self._tls.root_cert, "rb") as fh:
                    root_cert = fh.read()
            if self._tls.client_cert and self._tls.client_key:
                with open(self._tls.client_cert, "rb") as fh:
                    client_crt = fh.read()
                with open(self._tls.client_key, "rb") as fh:
                    client_key = fh.read()
            creds = grpc.ssl_channel_credentials(
                root_certificates=root_cert, private_key=client_key, certificate_chain=client_crt
            )
            return grpc.aio.secure_channel(self._peer.address, creds)
        return grpc.aio.insecure_channel(self._peer.address)

    async def upsert(self, request: realtime_pb2.UpsertEntityRequest) -> None:
        stub = await self._ensure_stub()
        await stub.UpsertEntity(request)

    async def remove(self, request: realtime_pb2.RemoveEntityRequest) -> None:
        stub = await self._ensure_stub()
        await stub.RemoveEntity(request)

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()


class EntityReplicator:
    def __init__(
        self,
        event_stream: EventStreamJournal,
        config: ReplicationConfig,
        *,
        tls: TLSConfig | None = None,
        transport_factory: (
            Callable[[ReplicationPeer, TLSConfig | None], PeerTransport] | None
        ) = None,
    ) -> None:
        self._event_stream = event_stream
        self._queue = event_stream.queue()
        self._config = config
        self._tls = tls
        self._transport_factory = transport_factory or PeerTransport
        self._task: asyncio.Task[None] | None = None
        self._transports: dict[str, PeerTransport] = {}
        self._stopped = asyncio.Event()

    async def start(self) -> None:
        if self._task is not None:
            return
        if not self._config.peers:
            return
        self._stopped.clear()
        self._task = asyncio.create_task(self._run(), name="realtime-replicator")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None
        self._stopped.set()
        await asyncio.gather(
            *(transport.close() for transport in self._transports.values()), return_exceptions=True
        )
        self._transports.clear()
        self._event_stream.unsubscribe(self._queue)

    async def _run(self) -> None:
        try:
            while True:
                event = await self._queue.get()
                if event.metadata.get("replicated_from") is not None:
                    continue
                await self._replicate(event)
        except asyncio.CancelledError:  # pragma: no cover - shutdown path
            raise
        except Exception:  # pragma: no cover - resilience guard
            logger.exception("Replication loop crashed")

    async def _replicate(self, event: EntityEvent) -> None:
        if not self._config.peers:
            return
        ttl_seconds = max((event.expires_at - event.updated_at).total_seconds(), 0.0)
        metadata = {
            "replicated_from": self._config.node_id,
            "sequence": str(event.sequence),
        }
        metadata.update({str(k): str(v) for k, v in self._config.metadata.items()})
        metadata.update({str(k): str(v) for k, v in event.metadata.items()})

        tasks = []
        for peer in sorted(self._config.peers, key=lambda p: p.priority, reverse=True):
            transport = await self._get_transport(peer)
            if event.event_type in {"remove", "expire"}:
                request = realtime_pb2.RemoveEntityRequest(entity_id=event.entity_id)
                request.metadata.update(metadata)
                tasks.append(self._send_remove(transport, request, peer))
            else:
                request = realtime_pb2.UpsertEntityRequest(
                    entity_id=event.entity_id,
                    object_type=event.object_type,
                    provenance=event.provenance,
                    ttl_seconds=ttl_seconds,
                )
                request.metadata.update(metadata)
                for name, payload in event.components.items():
                    struct = Struct()
                    struct.update(payload)
                    request.components[name].CopyFrom(struct)
                tasks.append(self._send_upsert(transport, request, peer))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _get_transport(self, peer: ReplicationPeer) -> PeerTransport:
        transport = self._transports.get(peer.address)
        if transport is None:
            transport = self._transport_factory(peer, self._tls)
            self._transports[peer.address] = transport
        return transport

    async def _send_upsert(
        self,
        transport: PeerTransport,
        request: realtime_pb2.UpsertEntityRequest,
        peer: ReplicationPeer,
    ) -> None:
        try:
            await asyncio.wait_for(
                transport.upsert(request), timeout=self._config.send_timeout_seconds
            )
        except Exception as exc:  # pragma: no cover - network guard
            logger.warning(
                "Failed to replicate entity %s to %s: %s", request.entity_id, peer.address, exc
            )

    async def _send_remove(
        self,
        transport: PeerTransport,
        request: realtime_pb2.RemoveEntityRequest,
        peer: ReplicationPeer,
    ) -> None:
        try:
            await asyncio.wait_for(
                transport.remove(request), timeout=self._config.send_timeout_seconds
            )
        except Exception as exc:  # pragma: no cover - network guard
            logger.warning(
                "Failed to replicate removal of %s to %s: %s", request.entity_id, peer.address, exc
            )


__all__ = [
    "EntityReplicator",
    "ReplicationConfig",
    "ReplicationPeer",
    "TLSConfig",
]
