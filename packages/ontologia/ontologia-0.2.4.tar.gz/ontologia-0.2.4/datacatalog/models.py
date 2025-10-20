"""
datacatalog/models.py
---------------------
Core models for the Data Catalog layer.

This module implements a Foundry-inspired data catalog system with:
- Dataset: Metadata pointer to physical data sources
- DatasetTransaction: Immutable history of dataset changes (like Git commits)
- DatasetBranch: Parallel versions of datasets (like Git branches)

Key Features:
- Versioned data management
- Branch-based workflows
- Immutable transaction history
- Physical data abstraction
"""

import enum
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel

# Import the base for all our resources
from registro import ResourceTypeBaseModel
from sqlmodel import JSON, Column, Field, Relationship

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from ontologia.domain.metamodels.instances.object_type_data_source import ObjectTypeDataSource


# --- Helper Models (Pydantic, not tables) ---


class ColumnSchema(BaseModel):
    """Describes the schema of a single column in a Dataset."""

    name: str
    type: str  # e.g., 'string', 'integer', 'timestamp'


# --- Enums ---


class TransactionType(str, enum.Enum):
    """
    Defines the type of change a transaction represents.
    - SNAPSHOT: Complete data replacement
    - APPEND: Only adding new rows
    """

    SNAPSHOT = "SNAPSHOT"
    APPEND = "APPEND"


# --- Database Models (SQLModel) ---


class DatasetTransaction(ResourceTypeBaseModel, table=True):
    """
    Represents a transaction (a "commit") in a Dataset's history.
    Each Dataset update creates a new transaction.

    Analogous to a Git commit, this provides:
    - Immutable history
    - Time travel capabilities
    - Audit trail
    """

    __resource_type__ = "dataset-transaction"
    __tablename__ = "datasettransaction"

    dataset_rid: str = Field(foreign_key="dataset.rid", index=True)
    dataset: "Dataset" = Relationship(back_populates="transactions")

    transaction_type: TransactionType = Field(...)
    commit_message: str | None = Field(
        None, description="Descriptive message of the change, like a Git commit message."
    )

    # Relationship to know which branches point to this transaction
    branches_at_head: list["DatasetBranch"] = Relationship(back_populates="head_transaction")


class DatasetBranch(ResourceTypeBaseModel, table=True):
    """
    Represents a branch (ramification) of a Dataset, like 'main' or 'develop'.
    Enables parallel data development and production workflows.

    Analogous to Git branches, this allows:
    - Parallel development
    - Production isolation
    - Experimentation without risk
    """

    __resource_type__ = "dataset-branch"
    __tablename__ = "datasetbranch"

    dataset_rid: str = Field(foreign_key="dataset.rid", index=True)
    dataset: "Dataset" = Relationship(
        back_populates="branches",
        sa_relationship_kwargs={"lazy": "joined", "foreign_keys": "[DatasetBranch.dataset_rid]"},
    )

    branch_name: str = Field(..., description="Branch name, e.g., 'main', 'develop'.")

    # The "HEAD" of this branch points to a specific transaction
    head_transaction_rid: str = Field(foreign_key="datasettransaction.rid")
    head_transaction: "DatasetTransaction" = Relationship(
        back_populates="branches_at_head", sa_relationship_kwargs={"lazy": "joined"}
    )

    # Relationship to know if this is the dataset's default branch
    dataset_as_default: Optional["Dataset"] = Relationship(
        back_populates="default_branch",
        sa_relationship_kwargs={"lazy": "joined", "foreign_keys": "[Dataset.default_branch_rid]"},
    )

    # Reverse linkage: ObjectTypes that read from this branch
    object_type_links: list["ObjectTypeDataSource"] = Relationship(
        back_populates="dataset_branch", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Dataset(ResourceTypeBaseModel, table=True):
    """
    Represents a Dataset: a tabular data resource registered in the ontology.
    Acts as a pointer and descriptor for data living in external systems
    (Parquet, DuckDB, etc.), serving as the "source of truth" for ObjectTypes.

    Key Responsibilities:
    - Describe physical data location and format
    - Maintain schema definition
    - Provide versioning and branching
    - Enable data lineage tracking
    """

    __resource_type__ = "dataset"
    __tablename__ = "dataset"

    # --- Physical Data Source Configuration ---
    source_type: str = Field(..., description="Source type (e.g., 'parquet_file', 'duckdb_table')")
    source_identifier: str = Field(..., description="File path or base table name")

    # Store the dataset schema (column names and types)
    schema_definition: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="JSON containing dataset schema (columns and types)",
    )

    # --- Governance Metadata ---
    owner_team: str | None = Field(
        default=None,
        description="Owning team responsible for the dataset",
    )
    contact_email: str | None = Field(
        default=None,
        description="Primary contact email for dataset issues",
    )
    update_frequency: str | None = Field(
        default=None,
        description="Expected cadence of dataset updates (e.g., daily, weekly)",
    )

    # --- Versioning Configuration ---
    default_branch_rid: str | None = Field(default=None, foreign_key="datasetbranch.rid")
    default_branch: Optional["DatasetBranch"] = Relationship(
        back_populates="dataset_as_default",
        sa_relationship_kwargs={"lazy": "joined", "foreign_keys": "[Dataset.default_branch_rid]"},
    )

    # Access to full transaction history and branches
    transactions: list["DatasetTransaction"] = Relationship(
        back_populates="dataset", sa_relationship_kwargs={"lazy": "selectin"}
    )
    branches: list["DatasetBranch"] = Relationship(
        back_populates="dataset",
        sa_relationship_kwargs={"lazy": "selectin", "foreign_keys": "[DatasetBranch.dataset_rid]"},
    )

    # Back-compat: direct linkage from ObjectTypeDataSource.dataset
    object_type_links: list["ObjectTypeDataSource"] = Relationship(
        back_populates="dataset", sa_relationship_kwargs={"lazy": "selectin"}
    )


# --- Resolve Circular References ---
# It's crucial to call model_rebuild() at the end so that relationships
# defined with strings (e.g., "Dataset") are resolved correctly.
DatasetTransaction.model_rebuild()
DatasetBranch.model_rebuild()
Dataset.model_rebuild()
