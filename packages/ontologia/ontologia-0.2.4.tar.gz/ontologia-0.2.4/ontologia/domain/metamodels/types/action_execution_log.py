from __future__ import annotations

import datetime as dt
from typing import Any

from sqlmodel import JSON, Column, Field, SQLModel


class ActionExecutionLog(SQLModel, table=True):
    """Audit log for Action executions.

    Stores execution outcome, parameters and result payloads (JSON),
    and basic timings for observability.
    """

    __tablename__ = "action_execution_log"

    id: int | None = Field(default=None, primary_key=True)

    # Multi-tenant scope
    service: str = Field(index=True)
    instance: str = Field(index=True)

    # Identity
    action_api_name: str = Field(index=True)
    target_object_type_api_name: str = Field(index=True)
    target_pk: str = Field(index=True)

    # Outcome
    status: str = Field(description="success|error")
    error_message: str | None = None

    # Payloads (stored as JSON)
    parameters: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    result: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    # Timings
    started_at: dt.datetime = Field()
    finished_at: dt.datetime = Field()
    duration_ms: int = Field(description="Execution duration in milliseconds")

    # Idempotency & async tracking
    idempotency_key: str | None = Field(default=None, index=True)
    workflow_id: str | None = Field(default=None, index=True)
    run_id: str | None = Field(default=None, index=True)
