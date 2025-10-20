"""Domain event definitions and publishing contract."""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import RLock
from typing import Protocol, TypeVar

logger = logging.getLogger(__name__)

TEvent = TypeVar("TEvent", bound="DomainEvent")
EventHandler = Callable[[TEvent], Awaitable[None] | None]


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    """Base class for all domain events."""

    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def event_name(self) -> str:
        return self.__class__.__name__


# Re-export context-specific events for backward compatibility
from ontologia.domain.instances.events import (  # noqa: E402,F401
    LinkCreated,
    LinkDeleted,
    ObjectInstanceDeleted,
    ObjectInstanceUpserted,
)
from ontologia.domain.metamodel.events import (  # noqa: E402,F401
    ObjectTypeCreated,
    ObjectTypeUpdated,
)


class DomainEventBus(Protocol):
    """Interface for publishing domain events."""

    def publish(self, event: DomainEvent) -> None:  # pragma: no cover - interface
        ...

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self.publish(event)


class NullEventBus:
    """No-op event bus used by default."""

    def publish(self, event: DomainEvent) -> None:
        return None

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        return None


class InMemoryEventBus:
    """Test helper event bus that accumulates events."""

    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    @property
    def events(self) -> list[DomainEvent]:
        return list(self._events)

    def publish(self, event: DomainEvent) -> None:
        self._events.append(event)

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self.publish(event)


class InProcessEventBus:
    """Simple in-process event bus with synchronous and async handler support."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler[DomainEvent]]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event_type: type[TEvent], handler: EventHandler[TEvent]) -> None:
        with self._lock:
            self._handlers[event_type].append(handler)  # type: ignore[arg-type]

    def unsubscribe(self, event_type: type[TEvent], handler: EventHandler[TEvent]) -> None:
        with self._lock:
            handlers = self._handlers.get(event_type)
            if not handlers:
                return
            try:
                handlers.remove(handler)  # type: ignore[arg-type]
            except ValueError:
                return
            if not handlers:
                self._handlers.pop(event_type, None)

    def clear(self) -> None:
        with self._lock:
            self._handlers.clear()

    def publish(self, event: DomainEvent) -> None:
        handlers = self._matching_handlers(type(event))
        for handler in handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    self._dispatch_async(result)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Error handling domain event %s", event.event_name)

    def publish_many(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self.publish(event)

    def _matching_handlers(self, event_cls: type[DomainEvent]) -> list[EventHandler[DomainEvent]]:
        with self._lock:
            handlers: list[EventHandler[DomainEvent]] = []
            for registered_cls, registered_handlers in self._handlers.items():
                if issubclass(event_cls, registered_cls):
                    handlers.extend(registered_handlers)
            return handlers

    def _dispatch_async(self, awaitable: Awaitable[None]) -> None:
        async def _runner() -> None:
            await awaitable

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(_runner())
        else:
            loop.create_task(_runner())
