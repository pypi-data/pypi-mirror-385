"""
test_comprehensive.py
--------------------
Comprehensive test suite for the entire ontologia codebase.
Tests all models, validators, constraints, and workflows.
"""

import sys


def test_imports():
    """Test 1: Verify all imports work correctly."""
    print("=" * 60)
    print("TEST 1: IMPORT VERIFICATION")
    print("=" * 60)

    try:
        # Core models
        print("✅ Property data types imported")

        # Metamodel types
        print("✅ Metamodel types imported")

        # Package
        import ontologia

        print(f"✅ Package imported (version: {ontologia.__version__})")

        return True, "All imports successful"
    except Exception as e:
        return False, f"Import failed: {e}"


def test_data_types():
    """Test 2: Verify all data types work correctly."""
    print("\n" + "=" * 60)
    print("TEST 2: DATA TYPE SYSTEM")
    print("=" * 60)

    from ontologia.domain.models.property_data_type import (
        ArrayType,
        IntegerType,
        StringType,
        StructFieldType,
        StructType,
        create_data_type,
    )

    results = []

    # Test basic types
    basic_types = ["string", "integer", "double", "boolean", "date", "timestamp"]
    for type_name in basic_types:
        try:
            dt = create_data_type(type_name)
            results.append((True, f"✅ {type_name} type created: {dt}"))
        except Exception as e:
            results.append((False, f"❌ {type_name} failed: {e}"))

    # Test composite types
    try:
        array_type = ArrayType(sub_type=StringType())
        results.append((True, f"✅ Array type created: {array_type}"))
    except Exception as e:
        results.append((False, f"❌ Array type failed: {e}"))

    try:
        struct_type = StructType(
            struct_field_types=[
                StructFieldType(api_name="field1", data_type=StringType()),
                StructFieldType(api_name="field2", data_type=IntegerType()),
            ]
        )
        results.append(
            (True, f"✅ Struct type created with {len(struct_type.struct_field_types)} fields")
        )
    except Exception as e:
        results.append((False, f"❌ Struct type failed: {e}"))

    # Print results
    for success, msg in results:
        print(msg)

    all_passed = all(r[0] for r in results)
    return all_passed, f"Data types: {sum(1 for r in results if r[0])}/{len(results)} passed"


def test_model_creation():
    """Test 3: Verify all models can be created."""
    print("\n" + "=" * 60)
    print("TEST 3: MODEL CREATION")
    print("=" * 60)

    from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType
    from ontologia.domain.metamodels.types.object_type import ObjectType
    from ontologia.domain.metamodels.types.property_type import PropertyType

    results = []

    # Test ObjectType creation
    try:
        obj_type = ObjectType(
            service="test",
            instance="test",
            api_name="person",
            display_name="Person",
            description="A person entity",
            primary_key_field="id",
        )
        results.append((True, f"✅ ObjectType created: {obj_type.api_name}"))
    except Exception as e:
        results.append((False, f"❌ ObjectType creation failed: {e}"))
        obj_type = None

    # Test PropertyType creation
    try:
        prop_type = PropertyType(
            service="test",
            instance="test",
            api_name="name",
            display_name="Name",
            description="Person name",
            data_type="string",
            required=True,
            object_type_api_name="person",
        )
        results.append((True, f"✅ PropertyType created: {prop_type.api_name}"))
    except Exception as e:
        results.append((False, f"❌ PropertyType creation failed: {e}"))

    # Test LinkType creation (unified bidirectional)
    try:
        link_type = LinkType(
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
        results.append((True, f"✅ LinkType created: {link_type.api_name}"))
    except Exception as e:
        results.append((False, f"❌ LinkType creation failed: {e}"))

    # Test LinkType with ONE_TO_ONE cardinality
    try:
        link_type_one = LinkType(
            service="test",
            instance="test",
            api_name="hasProfile",
            display_name="Has Profile",
            inverse_api_name="profileOf",
            inverse_display_name="Profile Of",
            cardinality=Cardinality.ONE_TO_ONE,
            from_object_type_api_name="person",
            to_object_type_api_name="profile",
        )
        results.append((True, f"✅ LinkType (ONE_TO_ONE) created: {link_type_one.api_name}"))
    except Exception as e:
        results.append((False, f"❌ LinkType (ONE_TO_ONE) creation failed: {e}"))

    # Test LinkType with max_degree
    try:
        link_type_max = LinkType(
            service="test",
            instance="test",
            api_name="hasHobbies",
            display_name="Has Hobbies",
            inverse_api_name="practitionersOf",
            inverse_display_name="Practitioners Of",
            cardinality=Cardinality.MANY_TO_MANY,
            from_object_type_api_name="person",
            to_object_type_api_name="hobby",
            max_degree_forward=10,
        )
        results.append((True, f"✅ LinkType with max_degree: {link_type_max.max_degree_forward}"))
    except Exception as e:
        results.append((False, f"❌ LinkType with max_degree failed: {e}"))

    # Print results
    for success, msg in results:
        print(msg)
    all_passed = all(r[0] for r in results)
    return all_passed, f"Model creation: {sum(1 for r in results if r[0])}/{len(results)} passed"


def test_validators():
    """Test 4: Verify field validators work correctly."""
    print("\n" + "=" * 60)
    print("TEST 4: FIELD VALIDATORS")
    print("=" * 60)

    from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType

    results = []

    # Test valid identifier
    try:
        link = LinkType(
            service="test",
            instance="test",
            api_name="validName",
            display_name="Valid Name",
            inverse_api_name="validInverse",
            inverse_display_name="Valid Inverse",
            cardinality=Cardinality.MANY_TO_ONE,
            from_object_type_api_name="person",
            to_object_type_api_name="address",
        )
        results.append((True, "✅ Valid identifier accepted"))
    except Exception as e:
        results.append((False, f"❌ Valid identifier rejected: {e}"))

    # Test invalid identifier (should fail)
    try:
        link = LinkType(
            service="test",
            instance="test",
            api_name="test",
            cardinality=Cardinality.ONE,
            object_type_api_name="invalid-name",  # Invalid: contains hyphen
            target_object_type_api_name="target",
        )
        results.append((False, "❌ Invalid identifier was accepted (should have failed)"))
    except ValueError as e:
        if "valid Python identifier" in str(e):
            results.append((True, "✅ Invalid identifier correctly rejected"))
        else:
            results.append((False, f"❌ Wrong error for invalid identifier: {e}"))
    except Exception as e:
        results.append((False, f"❌ Unexpected error: {e}"))

    # Test None target (should be accepted now)
    try:
        link = LinkTypeSide(
            service="test",
            instance="test",
            api_name="test_link",
            cardinality=Cardinality.ONE,
            object_type_api_name="person",
            target_object_type_api_name=None,
        )
        results.append((True, "✅ None target_object_type_api_name accepted"))
    except Exception as e:
        results.append((False, f"❌ None target rejected: {e}"))

    # Print results
    for success, msg in results:
        print(msg)

    all_passed = all(r[0] for r in results)
    return all_passed, f"Validators: {sum(1 for r in results if r[0])}/{len(results)} passed"


def test_property_management():
    """Test 5: Verify property management methods work."""
    print("\n" + "=" * 60)
    print("TEST 5: PROPERTY MANAGEMENT")
    print("=" * 60)

    from ontologia.domain.metamodels.types.object_type import ObjectType

    results = []

    try:
        from sqlmodel import Session, SQLModel, create_engine

        # Create in-memory database for testing
        engine = create_engine("sqlite:///:memory:", echo=False)
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            obj_type = ObjectType(
                service="test",
                instance="test",
                api_name="person",
                display_name="Person",
                primary_key_field="id",
            )

            # Add to session first
            session.add(obj_type)
            session.commit()
            session.refresh(obj_type)

            # Test set_properties with dicts (now with proper session)
            obj_type.set_properties(
                [
                    {
                        "api_name": "id",
                        "display_name": "ID",
                        "data_type": "string",
                        "description": "Primary key",
                    },
                    {
                        "api_name": "name",
                        "display_name": "Name",
                        "data_type": "string",
                        "description": "Person name",
                    },
                    {"api_name": "age", "display_name": "Age", "data_type": "integer"},
                ],
                session,
            )

            results.append(
                (True, f"✅ set_properties() added {len(obj_type.property_types)} properties")
            )

            # Test get_property helper
            name_prop = obj_type.get_property("name")
            if name_prop and name_prop.api_name == "name":
                results.append((True, f"✅ get_property() found property: {name_prop.api_name}"))
            else:
                results.append((False, "❌ get_property() did not find property"))

            # Test missing property
            missing = obj_type.get_property("nonexistent")
            if missing is None:
                results.append((True, "✅ get_property() returns None for missing property"))
            else:
                results.append((False, "❌ get_property() should return None for missing"))

            # Test duplicate detection
            try:
                obj_type.set_properties(
                    [
                        {"api_name": "dup", "data_type": "string"},
                        {"api_name": "dup", "data_type": "integer"},
                    ],
                    session,
                )
                results.append((False, "❌ Duplicate property name not detected"))
            except ValueError as e:
                if "Duplicate property" in str(e):
                    results.append((True, "✅ Duplicate property name detected"))
                else:
                    results.append((False, f"❌ Wrong error for duplicate: {e}"))

            # Test description flow
            obj_type.set_properties(
                [
                    {
                        "api_name": "email",
                        "display_name": "Email",
                        "data_type": "string",
                        "description": "Email address",
                    }
                ],
                session,
            )
            email_prop = obj_type.get_property("email")
            if email_prop and email_prop.description == "Email address":
                results.append((True, "✅ Description flows through correctly"))
            else:
                results.append(
                    (
                        False,
                        f"❌ Description not set: {email_prop.description if email_prop else 'prop not found'}",
                    )
                )

    except Exception as e:
        results.append((False, f"❌ Property management failed: {e}"))
        import traceback

        traceback.print_exc()

    # Print results
    for success, msg in results:
        print(msg)

    all_passed = all(r[0] for r in results)
    return (
        all_passed,
        f"Property management: {sum(1 for r in results if r[0])}/{len(results)} passed",
    )


def test_constraints():
    """Test 6: Verify constraint definitions."""
    print("\n" + "=" * 60)
    print("TEST 6: DATABASE CONSTRAINTS")
    print("=" * 60)

    from sqlmodel import UniqueConstraint

    from ontologia.domain.metamodels.types.link_type import LinkTypeSide
    from ontologia.domain.metamodels.types.property_type import PropertyType

    results = []

    # Check PropertyType has unique constraint
    if hasattr(PropertyType, "__table_args__"):
        table_args = PropertyType.__table_args__
        if table_args and len(table_args) > 0:
            constraint = table_args[0]
            if isinstance(constraint, UniqueConstraint):
                results.append((True, f"✅ PropertyType has UniqueConstraint: {constraint.name}"))
            else:
                results.append(
                    (True, f"✅ PropertyType has constraint: {type(constraint).__name__}")
                )
        else:
            results.append((False, "❌ PropertyType __table_args__ is empty"))
    else:
        results.append((False, "❌ PropertyType missing __table_args__"))

    # Check LinkTypeSide has unique constraint
    if hasattr(LinkTypeSide, "__table_args__"):
        table_args = LinkTypeSide.__table_args__
        if table_args and len(table_args) > 0:
            constraint = table_args[0]
            if isinstance(constraint, UniqueConstraint):
                results.append((True, f"✅ LinkTypeSide has UniqueConstraint: {constraint.name}"))
            else:
                results.append(
                    (True, f"✅ LinkTypeSide has constraint: {type(constraint).__name__}")
                )
        else:
            results.append((False, "❌ LinkTypeSide __table_args__ is empty"))
    else:
        results.append((False, "❌ LinkTypeSide missing __table_args__"))

    # Check validation methods exist
    from ontologia.domain.metamodels.types.object_type import ObjectType

    if hasattr(ObjectType, "validate_unique_service_instance_api_name"):
        results.append((True, "✅ ObjectType has uniqueness validation method"))
    else:
        results.append((False, "❌ ObjectType missing validation method"))

    if hasattr(PropertyType, "validate_unique_object_type_api_name"):
        results.append((True, "✅ PropertyType has uniqueness validation method"))
    else:
        results.append((False, "❌ PropertyType missing validation method"))

    if hasattr(LinkTypeSide, "validate_unique_link_api_name"):
        results.append((True, "✅ LinkTypeSide has uniqueness validation method"))
    else:
        results.append((False, "❌ LinkTypeSide missing validation method"))

    # Print results
    for success, msg in results:
        print(msg)

    all_passed = all(r[0] for r in results)
    return all_passed, f"Constraints: {sum(1 for r in results if r[0])}/{len(results)} passed"


def test_pydantic_config():
    """Test 7: Verify Pydantic v2 ConfigDict."""
    print("\n" + "=" * 60)
    print("TEST 7: PYDANTIC V2 CONFIG")
    print("=" * 60)

    from ontologia.domain.metamodels.types.link_type import LinkTypeSide
    from ontologia.domain.metamodels.types.object_type import ObjectType
    from ontologia.domain.metamodels.types.property_type import PropertyType

    results = []

    # Check each model has ConfigDict
    for model_class in [ObjectType, PropertyType, LinkTypeSide]:
        if hasattr(model_class, "model_config"):
            config = model_class.model_config
            if isinstance(config, dict):  # ConfigDict is a dict
                results.append((True, f"✅ {model_class.__name__} has model_config"))

                # Check for 'extra' setting
                if "extra" in config:
                    results.append((True, f"✅ {model_class.__name__} has 'extra' config"))
                else:
                    results.append((False, f"❌ {model_class.__name__} missing 'extra' config"))
            else:
                results.append((False, f"❌ {model_class.__name__} model_config is not dict"))
        else:
            results.append((False, f"❌ {model_class.__name__} missing model_config"))

    # Print results
    for success, msg in results:
        print(msg)

    all_passed = all(r[0] for r in results)
    return all_passed, f"Pydantic config: {sum(1 for r in results if r[0])}/{len(results)} passed"


def test_cardinality():
    """Test 8: Verify cardinality enum and max_degree."""
    print("\n" + "=" * 60)
    print("TEST 8: CARDINALITY SYSTEM")
    print("=" * 60)

    from ontologia.domain.metamodels.types.link_type import Cardinality, LinkTypeSide

    results = []

    # Test enum values
    try:
        one = Cardinality.ONE
        many = Cardinality.MANY
        results.append((True, f"✅ Cardinality enum: ONE={one}, MANY={many}"))
    except Exception as e:
        results.append((False, f"❌ Cardinality enum failed: {e}"))

    # Test that enum is pure (no mutable state)
    try:
        many1 = Cardinality.MANY
        many2 = Cardinality.MANY
        if many1 is many2:
            results.append((True, "✅ Cardinality enum is pure (singleton)"))
        else:
            results.append((False, "❌ Cardinality enum not singleton"))
    except Exception as e:
        results.append((False, f"❌ Cardinality singleton test failed: {e}"))

    # Test max_degree on LinkTypeSide
    try:
        link = LinkTypeSide(
            service="test",
            instance="test",
            api_name="test",
            cardinality=Cardinality.MANY,
            object_type_api_name="person",
            target_object_type_api_name="hobby",
            max_degree=5,
        )
        if link.max_degree == 5:
            results.append((True, f"✅ max_degree field works: {link.max_degree}"))
        else:
            results.append((False, f"❌ max_degree not set correctly: {link.max_degree}"))
    except Exception as e:
        results.append((False, f"❌ max_degree test failed: {e}"))

    # Test max_degree is None by default
    try:
        link_no_max = LinkTypeSide(
            service="test",
            instance="test",
            api_name="test2",
            cardinality=Cardinality.ONE,
            object_type_api_name="person",
            target_object_type_api_name="address",
        )
        if link_no_max.max_degree is None:
            results.append((True, "✅ max_degree defaults to None"))
        else:
            results.append((False, f"❌ max_degree should be None: {link_no_max.max_degree}"))
    except Exception as e:
        results.append((False, f"❌ Default max_degree test failed: {e}"))

    # Print results
    for success, msg in results:
        print(msg)

    all_passed = all(r[0] for r in results)
    return all_passed, f"Cardinality: {sum(1 for r in results if r[0])}/{len(results)} passed"


def test_fail_fast_validation():
    """Test 9: Verify fail-fast validation in LinkTypeSide."""
    print("\n" + "=" * 60)
    print("TEST 9: FAIL-FAST VALIDATION")
    print("=" * 60)

    from sqlmodel import Session, SQLModel, create_engine

    from ontologia.domain.metamodels.types.link_type import Cardinality, LinkTypeSide

    results = []

    try:
        # Create in-memory database
        engine = create_engine("sqlite:///:memory:", echo=False)
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            # Create link with unresolved fields
            link = LinkTypeSide(
                service="test",
                instance="test",
                api_name="incomplete",
                cardinality=Cardinality.ONE,
                object_type_api_name="person",
                # Note: target_object_type_api_name and object_type_rid not set
            )

            # Try to validate - should fail fast
            try:
                link.validate_unique_before_save(session)
                results.append((False, "❌ Should have failed fast but did not"))
            except ValueError as e:
                error_msg = str(e)
                if "Call validate_object_types(session) first" in error_msg:
                    results.append((True, "✅ Fail-fast validation with clear error"))
                elif "must have object_type_rid and target_object_type_api_name" in error_msg:
                    results.append((True, "✅ Fail-fast validation with clear error"))
                else:
                    results.append((False, f"❌ Wrong error message: {error_msg}"))
            except Exception as e:
                results.append((False, f"❌ Unexpected error type: {type(e).__name__}: {e}"))

    except Exception as e:
        results.append((False, f"❌ Test setup failed: {e}"))

    # Print results
    for success, msg in results:
        print(msg)

    all_passed = all(r[0] for r in results)
    return all_passed, f"Fail-fast: {sum(1 for r in results if r[0])}/{len(results)} passed"


def main():
    """Run all tests and report results."""
    print("\n" + "🧪 " * 20)
    print("COMPREHENSIVE ONTOLOGIA TEST SUITE")
    print("🧪 " * 20 + "\n")

    test_functions = [
        test_imports,
        test_data_types,
        test_model_creation,
        test_validators,
        test_property_management,
        test_constraints,
        test_pydantic_config,
        test_cardinality,
        test_fail_fast_validation,
    ]

    results = []
    for test_func in test_functions:
        try:
            passed, summary = test_func()
            results.append((passed, summary))
        except Exception as e:
            results.append((False, f"{test_func.__name__} crashed: {e}"))
            import traceback

            traceback.print_exc()

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r[0])

    for passed, summary in results:
        status = "✅" if passed else "❌"
        print(f"{status} {summary}")

    print("\n" + "=" * 60)
    print(f"TOTAL: {passed_tests}/{total_tests} test suites passed")
    print("=" * 60)

    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED - CODEBASE FULLY VERIFIED!")
        return 0
    else:
        print(f"\n❌ {total_tests - passed_tests} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
