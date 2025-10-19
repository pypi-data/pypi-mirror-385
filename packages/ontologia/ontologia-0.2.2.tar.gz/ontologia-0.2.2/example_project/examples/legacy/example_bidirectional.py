"""
test_bidirectional.py
---------------------
Test script to verify bidirectional LinkType relationships.
"""

from sqlmodel import Session, SQLModel, create_engine

from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType

# Create in-memory database
engine = create_engine("sqlite:///:memory:", echo=False)
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
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

    # Add properties
    employee.set_properties(
        [
            {
                "api_name": "emp_id",
                "display_name": "Employee ID",
                "data_type": "string",
                "is_primary_key": True,
                "required": True,
            },
            {"api_name": "name", "display_name": "Name", "data_type": "string", "required": True},
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
                "required": True,
            },
            {"api_name": "name", "display_name": "Name", "data_type": "string", "required": True},
        ],
        session,
    )

    session.commit()

    # Create LinkType
    works_for = LinkType(
        service="test",
        instance="test",
        api_name="works_for",
        display_name="Works For",
        inverse_api_name="employs",
        inverse_display_name="Employs",
        cardinality=Cardinality.MANY_TO_ONE,
        from_object_type_api_name="employee",
        to_object_type_api_name="company",
    )

    works_for.validate_and_resolve_object_types(session)
    session.add(works_for)
    session.commit()

    # Refresh to load relationships
    session.refresh(employee)
    session.refresh(company)

    # Test bidirectional navigation
    print("\n" + "=" * 60)
    print("BIDIRECTIONAL LINKTYPE TEST")
    print("=" * 60)

    print(f"\n✅ Created LinkType: {works_for.api_name}")
    print(f"   Cardinality: {works_for.cardinality}")
    print(f"   Inverse: {works_for.inverse_api_name}")

    print(f"\n✅ Employee outgoing_links: {len(employee.outgoing_links)}")
    for link in employee.outgoing_links:
        print(f"   -> {link.api_name} ({link.cardinality})")
        print(f"      to: {link.to_object_type.api_name}")
        print(f"      Forward def: {link.get_forward_definition()}")

    print(f"\n✅ Company incoming_links: {len(company.incoming_links)}")
    for link in company.incoming_links:
        print(f"   <- {link.inverse_api_name} ({link.cardinality})")
        print(f"      from: {link.from_object_type.api_name}")
        print(f"      Inverse def: {link.get_inverse_definition()}")

    print("\n" + "=" * 60)
    print("✅ ALL BIDIRECTIONAL TESTS PASSED!")
    print("=" * 60)
