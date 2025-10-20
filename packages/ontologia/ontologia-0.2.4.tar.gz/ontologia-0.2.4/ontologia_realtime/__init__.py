"""Real-time entity management utilities backed by gRPC."""

from .decision import (
    ActionSink,
    Condition,
    DecisionAction,
    DecisionAuditLog,
    DecisionConfig,
    DecisionEngine,
    DecisionResult,
    DecisionRule,
    DecisionService,
    DecisionSimulator,
    InMemoryActionSink,
    JsonlActionSink,
    JsonlDecisionAuditLog,
    LoggingActionSink,
    load_rules_from_file,
)
from .enrichment import RealTimeEnricher
from .entity_manager import EntityManager, EntitySnapshot
from .journal import EntityEvent, EntityJournal, InMemoryEntityJournal, JsonlEntityJournal
from .replication import EntityReplicator, ReplicationConfig, ReplicationPeer, TLSConfig
from .runtime import RealTimeRuntime, RealTimeRuntimeConfig
from .schema import SchemaRegistry
from .server import RealTimeServerConfig, serve
from .storage import SQLiteEntityStore

__all__ = [
    "EntityManager",
    "EntitySnapshot",
    "EntityEvent",
    "EntityJournal",
    "InMemoryEntityJournal",
    "JsonlEntityJournal",
    "ActionSink",
    "Condition",
    "DecisionAction",
    "DecisionAuditLog",
    "DecisionConfig",
    "DecisionEngine",
    "DecisionResult",
    "DecisionRule",
    "DecisionService",
    "DecisionSimulator",
    "InMemoryActionSink",
    "JsonlActionSink",
    "JsonlDecisionAuditLog",
    "LoggingActionSink",
    "load_rules_from_file",
    "EntityReplicator",
    "ReplicationConfig",
    "ReplicationPeer",
    "TLSConfig",
    "SchemaRegistry",
    "RealTimeServerConfig",
    "RealTimeRuntime",
    "RealTimeRuntimeConfig",
    "SQLiteEntityStore",
    "RealTimeEnricher",
    "serve",
]
