"""
test_comprehensive_updated.py
-----------------------------
Updated comprehensive test suite for ontologia with new LinkType model.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine


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


def test_imports():
    """Test 1: Verify all imports work correctly."""
    # Core models

    # Metamodel types

    # Package
    import ontologia

    assert ontologia.__version__ is not None


def test_object_type_creation(session):
    """Test creating an ObjectType."""
    from ontologia.domain.metamodels.types.object_type import ObjectType

    obj_type = ObjectType(
        service="test",
        instance="test",
        api_name="person",
        display_name="Person",
        description="A person entity",
        primary_key_field="id",
    )

    session.add(obj_type)
    session.commit()
    session.refresh(obj_type)

    assert obj_type.rid is not None
    assert obj_type.api_name == "person"
    assert obj_type.primary_key_field == "id"


def test_property_type_creation(session):
    """Test creating a PropertyType."""
    from ontologia.domain.metamodels.types.object_type import ObjectType
    from ontologia.domain.metamodels.types.property_type import PropertyType

    obj_type = ObjectType(
        service="test",
        instance="test",
        api_name="person",
        display_name="Person",
        primary_key_field="id",
    )
    session.add(obj_type)
    session.commit()

    prop_type = PropertyType(
        service="test",
        instance="test",
        api_name="name",
        display_name="Name",
        data_type="string",
        required=True,
        object_type_api_name="person",
    )
    prop_type.link_object_type(session)

    session.add(prop_type)
    session.commit()
    session.refresh(prop_type)

    assert prop_type.rid is not None
    assert prop_type.api_name == "name"
    assert prop_type.data_type == "string"
    assert prop_type.required is True


def test_linktype_creation(session):
    """Test creating a unified LinkType."""
    from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType
    from ontologia.domain.metamodels.types.object_type import ObjectType

    # Create ObjectTypes
    person = ObjectType(
        service="test",
        instance="test",
        api_name="person",
        display_name="Person",
        primary_key_field="id",
    )
    session.add(person)

    address = ObjectType(
        service="test",
        instance="test",
        api_name="address",
        display_name="Address",
        primary_key_field="id",
    )
    session.add(address)
    session.commit()

    person.set_properties(
        [{"api_name": "id", "display_name": "ID", "data_type": "string", "is_primary_key": True}],
        session,
    )

    address.set_properties(
        [{"api_name": "id", "display_name": "ID", "data_type": "string", "is_primary_key": True}],
        session,
    )

    session.commit()

    # Create LinkType
    link = LinkType(
        service="test",
        instance="test",
        api_name="livesAt",
        display_name="Lives At",
        inverse_api_name="residents",
        inverse_display_name="Residents",
        cardinality=Cardinality.MANY_TO_ONE,
        from_object_type_api_name="person",
        to_object_type_api_name="address",
    )

    link.validate_and_resolve_object_types(session)
    session.add(link)
    session.commit()
    session.refresh(link)

    assert link.rid is not None
    assert link.api_name == "livesAt"
    assert link.inverse_api_name == "residents"
    assert link.cardinality == Cardinality.MANY_TO_ONE


def test_linktype_cardinalities():
    """Test all LinkType cardinality options."""
    from ontologia.domain.metamodels.types.link_type import Cardinality

    assert Cardinality.ONE_TO_ONE == "ONE_TO_ONE"
    assert Cardinality.ONE_TO_MANY == "ONE_TO_MANY"
    assert Cardinality.MANY_TO_ONE == "MANY_TO_ONE"
    assert Cardinality.MANY_TO_MANY == "MANY_TO_MANY"


def test_linktype_methods():
    """Test LinkType helper methods."""
    from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType

    link = LinkType(
        service="test",
        instance="test",
        api_name="worksFor",
        display_name="Works For",
        inverse_api_name="employs",
        inverse_display_name="Employs",
        cardinality=Cardinality.MANY_TO_ONE,
        from_object_type_api_name="employee",
        to_object_type_api_name="company",
    )

    forward = link.get_forward_definition()
    assert forward["api_name"] == "worksFor"
    assert forward["cardinality"] == "MANY"
    assert forward["from"] == "employee"
    assert forward["to"] == "company"

    inverse = link.get_inverse_definition()
    assert inverse["api_name"] == "employs"
    assert inverse["cardinality"] == "ONE"
    assert inverse["from"] == "company"
    assert inverse["to"] == "employee"


def test_bidirectional_relationships(session):
    """Test bidirectional navigation between ObjectType and LinkType."""
    from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType
    from ontologia.domain.metamodels.types.object_type import ObjectType

    # Create ObjectTypes
    employee = ObjectType(
        service="test",
        instance="test",
        api_name="employee",
        display_name="Employee",
        primary_key_field="emp_id",
    )
    session.add(employee)

    company = ObjectType(
        service="test",
        instance="test",
        api_name="company",
        display_name="Company",
        primary_key_field="comp_id",
    )
    session.add(company)
    session.commit()

    employee.set_properties(
        [
            {
                "api_name": "emp_id",
                "display_name": "Employee ID",
                "data_type": "string",
                "is_primary_key": True,
            }
        ],
        session,
    )

    company.set_properties(
        [
            {
                "api_name": "comp_id",
                "display_name": "Company ID",
                "data_type": "string",
                "is_primary_key": True,
            }
        ],
        session,
    )

    session.commit()

    # Create LinkType
    link = LinkType(
        service="test",
        instance="test",
        api_name="worksFor",
        display_name="Works For",
        inverse_api_name="employs",
        inverse_display_name="Employs",
        cardinality=Cardinality.MANY_TO_ONE,
        from_object_type_api_name="employee",
        to_object_type_api_name="company",
    )

    link.validate_and_resolve_object_types(session)
    session.add(link)
    session.commit()

    # Refresh to load relationships
    session.refresh(employee)
    session.refresh(company)

    # Test bidirectional navigation
    assert len(employee.outgoing_links) == 1
    assert employee.outgoing_links[0].api_name == "worksFor"

    assert len(company.incoming_links) == 1
    assert company.incoming_links[0].inverse_api_name == "employs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
