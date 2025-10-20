"""
test_datacatalog_integration.py
-------------------------------
Tests for the complete datacatalog + ontologia integration.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine

from datacatalog import Dataset, DatasetBranch, DatasetTransaction, TransactionType
from ontologia import ObjectType, ObjectTypeDataSource


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session


def test_create_dataset(session):
    """Test creating a Dataset."""
    dataset = Dataset(
        service="test",
        instance="test",
        api_name="test_dataset",
        display_name="Test Dataset",
        source_type="parquet_file",
        source_identifier="s3://test-bucket/data.parquet",
        schema_definition={"columns": [{"name": "id", "type": "string"}]},
    )

    session.add(dataset)
    session.commit()
    session.refresh(dataset)

    assert dataset.rid is not None
    assert dataset.api_name == "test_dataset"
    assert dataset.source_type == "parquet_file"


def test_create_transaction(session):
    """Test creating a DatasetTransaction."""
    dataset = Dataset(
        service="test",
        instance="test",
        api_name="test_dataset",
        display_name="Test Dataset",
        source_type="parquet_file",
        source_identifier="s3://test-bucket/data.parquet",
    )
    session.add(dataset)
    session.commit()

    transaction = DatasetTransaction(
        service="test",
        instance="test",
        api_name="test_transaction",
        display_name="Test Transaction",
        dataset_rid=dataset.rid,
        transaction_type=TransactionType.SNAPSHOT,
        commit_message="Initial commit",
    )

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    assert transaction.rid is not None
    assert transaction.transaction_type == TransactionType.SNAPSHOT
    assert transaction.commit_message == "Initial commit"


def test_create_branch(session):
    """Test creating a DatasetBranch."""
    dataset = Dataset(
        service="test",
        instance="test",
        api_name="test_dataset",
        display_name="Test Dataset",
        source_type="parquet_file",
        source_identifier="s3://test-bucket/data.parquet",
    )
    session.add(dataset)
    session.commit()

    transaction = DatasetTransaction(
        service="test",
        instance="test",
        api_name="test_transaction",
        display_name="Test Transaction",
        dataset_rid=dataset.rid,
        transaction_type=TransactionType.SNAPSHOT,
    )
    session.add(transaction)
    session.commit()

    branch = DatasetBranch(
        service="test",
        instance="test",
        api_name="test_branch",
        display_name="Test Branch",
        dataset_rid=dataset.rid,
        branch_name="main",
        head_transaction_rid=transaction.rid,
    )

    session.add(branch)
    session.commit()
    session.refresh(branch)

    assert branch.rid is not None
    assert branch.branch_name == "main"
    assert branch.head_transaction_rid == transaction.rid


def test_link_object_type_to_dataset(session):
    """Test linking an ObjectType to a Dataset."""
    # Create Dataset
    dataset = Dataset(
        service="test",
        instance="test",
        api_name="test_dataset",
        display_name="Test Dataset",
        source_type="parquet_file",
        source_identifier="s3://test-bucket/data.parquet",
        schema_definition={"columns": [{"name": "id", "type": "string"}]},
    )
    session.add(dataset)
    session.commit()

    # Create ObjectType
    object_type = ObjectType(
        service="test",
        instance="test",
        api_name="test_object",
        display_name="Test Object",
        primary_key_field="id",
    )
    session.add(object_type)
    session.commit()

    object_type.set_properties(
        [{"api_name": "id", "display_name": "ID", "data_type": "string", "is_primary_key": True}],
        session,
    )
    session.commit()

    # Link them
    link = ObjectTypeDataSource(
        service="test",
        instance="test",
        api_name="test_link",
        display_name="Test Link",
        object_type_rid=object_type.rid,
        dataset_rid=dataset.rid,
        sync_status="completed",
    )

    session.add(link)
    session.commit()
    session.refresh(link)

    assert link.rid is not None
    assert link.object_type_rid == object_type.rid
    assert link.dataset_rid == dataset.rid
    assert link.sync_status == "completed"


def test_data_lineage(session):
    """Test data lineage tracking from ObjectType to Dataset."""
    # Create Dataset with version control
    dataset = Dataset(
        service="test",
        instance="test",
        api_name="test_dataset",
        display_name="Test Dataset",
        source_type="parquet_file",
        source_identifier="s3://test-bucket/data.parquet",
    )
    session.add(dataset)
    session.commit()

    transaction = DatasetTransaction(
        service="test",
        instance="test",
        api_name="test_transaction",
        display_name="Test Transaction",
        dataset_rid=dataset.rid,
        transaction_type=TransactionType.SNAPSHOT,
        commit_message="Initial load",
    )
    session.add(transaction)
    session.commit()

    branch = DatasetBranch(
        service="test",
        instance="test",
        api_name="test_branch",
        display_name="Test Branch",
        dataset_rid=dataset.rid,
        branch_name="main",
        head_transaction_rid=transaction.rid,
    )
    session.add(branch)
    session.commit()

    dataset.default_branch_rid = branch.rid
    session.add(dataset)
    session.commit()

    # Create ObjectType
    object_type = ObjectType(
        service="test",
        instance="test",
        api_name="test_object",
        display_name="Test Object",
        primary_key_field="id",
    )
    session.add(object_type)
    session.commit()

    object_type.set_properties(
        [{"api_name": "id", "display_name": "ID", "data_type": "string", "is_primary_key": True}],
        session,
    )
    session.commit()

    # Link them
    link = ObjectTypeDataSource(
        service="test",
        instance="test",
        api_name="test_link",
        display_name="Test Link",
        object_type_rid=object_type.rid,
        dataset_rid=dataset.rid,
    )
    session.add(link)
    session.commit()

    # Verify lineage
    session.refresh(object_type)
    session.refresh(dataset)

    # ObjectType → Dataset
    assert len(object_type.data_sources) == 1
    assert object_type.data_sources[0].dataset.api_name == "test_dataset"

    # Dataset → ObjectType
    assert len(dataset.object_type_links) == 1
    assert dataset.object_type_links[0].object_type.api_name == "test_object"

    # Dataset → Branch → Transaction
    assert dataset.default_branch.branch_name == "main"
    assert dataset.default_branch.head_transaction.commit_message == "Initial load"
    assert dataset.default_branch.head_transaction.transaction_type == TransactionType.SNAPSHOT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
