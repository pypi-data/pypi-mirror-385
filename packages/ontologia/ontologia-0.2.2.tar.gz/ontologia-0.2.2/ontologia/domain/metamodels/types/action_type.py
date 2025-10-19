"""
action_type.py
----------------
Defines ActionType (a first-class metamodel entity) to model user-triggered Actions
on objects, aligned with the Palantir Foundry-style ontology Actions concept.

Design principles:
- Metadata-only definition in SQLModel (control plane)
- No storage of executable code; execution is mapped via a safe registry key
- Parameters and rules serialized as JSON
"""

from registro import ResourceTypeBaseModel
from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Column, Field


class ActionType(ResourceTypeBaseModel, table=True):
    """
    Defines an Action in the ontology metamodel. Pure metadata resource.
    Execution logic is referenced via `executor_key` and resolved in backend registry.
    """

    __resource_type__ = "action-type"
    __tablename__ = "actiontype"
    __table_args__ = (
        UniqueConstraint("executor_key", "version", name="uq_actiontype_executor_version"),
        UniqueConstraint("api_name", "version", name="uq_actiontype_api_version"),
    )

    # Scope target: which ObjectType this Action applies to (Interface support in future)
    target_object_type_api_name: str = Field(index=True)

    # Parameters UI should render for user input (api_name -> definition)
    # Stored as plain dicts for JSON column compatibility
    parameters: dict[str, dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Rules for availability
    submission_criteria: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # Rules for parameter/business validation
    validation_rules: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # Implementation key mapping to Python function in backend registry
    executor_key: str = Field(index=True, description="Maps to a registered Python function")

    version: int = Field(default=1, ge=1, description="Schema version", index=True)
    is_latest: bool = Field(default=True, description="Latest version flag", index=True)


# Rebuild model to resolve forward references if any
ActionType.model_rebuild()
