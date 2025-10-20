"""
test_sync_service.py
-------------------
Testes para o OntologySyncService.

Nota: Estes testes verificam a estrutura e lógica do serviço.
Para testes end-to-end completos, execute sync.py
(requer: pip install kuzu duckdb polars)
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine

from datacatalog import Dataset
from ontologia import ObjectType, ObjectTypeDataSource
from ontologia.application import SyncMetrics


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


def test_sync_metrics():
    """Test SyncMetrics tracking."""
    metrics = SyncMetrics()

    # Test initialization
    assert metrics.start_time is None
    assert metrics.end_time is None
    assert len(metrics.nodes_created) == 0
    assert len(metrics.rels_created) == 0

    # Test start/finish
    metrics.start()
    assert metrics.start_time is not None

    metrics.finish()
    assert metrics.end_time is not None
    assert metrics.duration() > 0

    # Test node tracking
    metrics.add_nodes("customer", 100)
    metrics.add_nodes("order", 50)
    assert metrics.nodes_created["customer"] == 100
    assert metrics.nodes_created["order"] == 50

    # Test relation tracking
    metrics.add_rels("places_order", 75)
    assert metrics.rels_created["places_order"] == 75

    # Test warnings and errors
    metrics.add_warning("Test warning")
    metrics.add_error("Test error")
    assert len(metrics.warnings) == 1
    assert len(metrics.errors) == 1

    # Test summary
    summary = metrics.summary()
    assert "SYNC METRICS SUMMARY" in summary
    assert "customer: 100" in summary
    assert "order: 50" in summary


def test_sync_service_imports():
    """Test that the sync service can be imported."""
    try:
        from ontologia.application import OntologySyncService

        assert OntologySyncService is not None
    except ImportError as e:
        pytest.skip(f"Dependencies not installed: {e}")


def test_sync_service_initialization(session):
    """Test OntologySyncService initialization."""
    try:
        from ontologia.application import OntologySyncService

        # Initialize without kuzu/duckdb (should work)
        service = OntologySyncService(metadata_session=session, kuzu_conn=None, duckdb_conn=None)

        assert service.meta_db == session
        assert service.kuzu is None
        assert service.duckdb is None
        assert service.metrics is not None
        assert isinstance(service.type_mapping, dict)

    except ImportError:
        pytest.skip("Dependencies not installed")


def test_control_plane_setup(session):
    """Test that we can set up the control plane for sync."""
    # Create ObjectType
    customer = ObjectType(
        service="test",
        instance="test",
        api_name="customer",
        display_name="Customer",
        primary_key_field="id",
    )
    session.add(customer)
    session.commit()

    customer.set_properties(
        [
            {"api_name": "id", "display_name": "ID", "data_type": "string", "is_primary_key": True},
            {"api_name": "name", "display_name": "Name", "data_type": "string"},
        ],
        session,
    )
    session.commit()

    # Create Dataset
    dataset = Dataset(
        service="test",
        instance="test",
        api_name="customer_data",
        display_name="Customer Data",
        source_type="duckdb_table",
        source_identifier="customers",
    )
    session.add(dataset)
    session.commit()

    # Link them
    link = ObjectTypeDataSource(
        service="test",
        instance="test",
        api_name="link",
        display_name="Link",
        object_type_rid=customer.rid,
        dataset_rid=dataset.rid,
        sync_status="pending",
    )
    session.add(link)
    session.commit()

    # Verify setup
    session.refresh(customer)
    assert len(customer.data_sources) == 1
    assert customer.data_sources[0].dataset.api_name == "customer_data"
    assert customer.data_sources[0].dataset.source_type == "duckdb_table"


def test_type_mapping():
    """Test data type mappings."""
    try:
        from sqlmodel import Session, create_engine

        from ontologia.application import OntologySyncService

        engine = create_engine("sqlite:///:memory:")
        with Session(engine) as session:
            service = OntologySyncService(session, None, None)

            # Test mappings
            assert service.type_mapping.get("string") == "STRING"
            assert service.type_mapping.get("integer") == "INT64"
            assert service.type_mapping.get("double") == "DOUBLE"
            assert service.type_mapping.get("boolean") == "BOOL"
            assert service.type_mapping.get("date") == "DATE"
            assert service.type_mapping.get("timestamp") == "TIMESTAMP"

    except ImportError:
        pytest.skip("Dependencies not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
