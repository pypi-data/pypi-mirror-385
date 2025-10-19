"""
test_unified_linktype.py
------------------------
Testes simplificados para o novo LinkType unificado.
"""

from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType


def test_basic_linktype_creation():
    """Test: Criar LinkType básico."""
    print("\n" + "=" * 60)
    print("TEST: LinkType Creation")
    print("=" * 60)

    results = []

    # Test 1: Criar LinkType simples
    try:
        link = LinkType(
            service="test",
            instance="test",
            api_name="works_for",
            display_name="Works For",
            from_object_type_api_name="employee",
            to_object_type_api_name="company",
            inverse_api_name="has_employees",
            inverse_display_name="Has Employees",
            cardinality=Cardinality.MANY_TO_ONE,
        )
        results.append((True, f"✅ LinkType created: {link.api_name}"))
        results.append((True, f"✅ Cardinality: {link.cardinality}"))
        results.append((True, f"✅ Inverse: {link.inverse_api_name}"))
    except Exception as e:
        results.append((False, f"❌ LinkType creation failed: {e}"))

    # Test 2: Testar max_degree
    try:
        link_max = LinkType(
            service="test",
            instance="test",
            api_name="manages",
            display_name="Manages",
            from_object_type_api_name="manager",
            to_object_type_api_name="team",
            inverse_api_name="managed_by",
            inverse_display_name="Managed By",
            cardinality=Cardinality.ONE_TO_MANY,
            max_degree_forward=5,  # Manager pode gerenciar até 5 teams
            max_degree_inverse=1,  # Team tem 1 manager
        )
        results.append(
            (
                True,
                f"✅ LinkType with max_degree: forward={link_max.max_degree_forward}, inverse={link_max.max_degree_inverse}",
            )
        )
    except Exception as e:
        results.append((False, f"❌ max_degree test failed: {e}"))

    # Test 3: Validação de identificadores
    try:
        bad_link = LinkType(
            service="test",
            instance="test",
            api_name="bad-name",  # Invalid identifier
            display_name="Bad",
            from_object_type_api_name="a",
            to_object_type_api_name="b",
            inverse_api_name="inverse",
            inverse_display_name="Inverse",
            cardinality=Cardinality.ONE_TO_ONE,
        )
        results.append((False, "❌ Invalid identifier was accepted"))
    except ValueError as e:
        if "valid Python identifier" in str(e):
            results.append((True, "✅ Invalid identifier rejected correctly"))
        else:
            results.append((False, f"❌ Wrong error: {e}"))

    # Test 4: Validação api_name != inverse_api_name
    try:
        same_link = LinkType(
            service="test",
            instance="test",
            api_name="same",
            display_name="Same",
            from_object_type_api_name="a",
            to_object_type_api_name="b",
            inverse_api_name="same",  # Same as api_name!
            inverse_display_name="Same Inverse",
            cardinality=Cardinality.ONE_TO_ONE,
        )
        results.append((False, "❌ Same api_name and inverse_api_name was accepted"))
    except ValueError as e:
        if "must be different" in str(e):
            results.append((True, "✅ Same names rejected correctly"))
        else:
            results.append((False, f"❌ Wrong error: {e}"))

    # Print results
    for success, msg in results:
        print(msg)

    passed = sum(1 for s, _ in results if s)
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    return passed == total


def test_cardinality_enum():
    """Test: Enum de Cardinalidade."""
    print("\n" + "=" * 60)
    print("TEST: Cardinality Enum")
    print("=" * 60)

    results = []

    # Test enum values
    try:
        assert Cardinality.ONE_TO_ONE == "ONE_TO_ONE"
        assert Cardinality.ONE_TO_MANY == "ONE_TO_MANY"
        assert Cardinality.MANY_TO_ONE == "MANY_TO_ONE"
        assert Cardinality.MANY_TO_MANY == "MANY_TO_MANY"
        results.append((True, "✅ All cardinality values correct"))
    except AssertionError as e:
        results.append((False, f"❌ Cardinality enum failed: {e}"))

    # Test singleton behavior
    try:
        c1 = Cardinality.MANY_TO_ONE
        c2 = Cardinality.MANY_TO_ONE
        assert c1 is c2
        results.append((True, "✅ Cardinality is singleton"))
    except AssertionError:
        results.append((False, "❌ Cardinality is not singleton"))

    # Print results
    for success, msg in results:
        print(msg)

    passed = sum(1 for s, _ in results if s)
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    return passed == total


def test_linktype_methods():
    """Test: Métodos do LinkType."""
    print("\n" + "=" * 60)
    print("TEST: LinkType Methods")
    print("=" * 60)

    results = []

    link = LinkType(
        service="test",
        instance="test",
        api_name="works_for",
        display_name="Works For",
        from_object_type_api_name="employee",
        to_object_type_api_name="company",
        inverse_api_name="has_employees",
        inverse_display_name="Has Employees",
        cardinality=Cardinality.MANY_TO_ONE,
    )

    # Test get_forward_definition
    try:
        forward = link.get_forward_definition()
        assert forward["api_name"] == "works_for"
        assert forward["from"] == "employee"
        assert forward["to"] == "company"
        assert forward["cardinality"] == "MANY"  # MANY_TO_ONE from employee perspective
        results.append((True, f"✅ get_forward_definition() works: {forward}"))
    except Exception as e:
        results.append((False, f"❌ get_forward_definition() failed: {e}"))

    # Test get_inverse_definition
    try:
        inverse = link.get_inverse_definition()
        assert inverse["api_name"] == "has_employees"
        assert inverse["from"] == "company"  # Reversed
        assert inverse["to"] == "employee"  # Reversed
        assert inverse["cardinality"] == "ONE"  # MANY_TO_ONE from company perspective
        results.append((True, f"✅ get_inverse_definition() works: {inverse}"))
    except Exception as e:
        results.append((False, f"❌ get_inverse_definition() failed: {e}"))

    # Test __repr__
    try:
        repr_str = repr(link)
        assert "works_for" in repr_str
        assert "has_employees" in repr_str
        assert "MANY_TO_ONE" in repr_str
        results.append((True, f"✅ __repr__() works: {repr_str}"))
    except Exception as e:
        results.append((False, f"❌ __repr__() failed: {e}"))

    # Print results
    for success, msg in results:
        print(msg)

    passed = sum(1 for s, _ in results if s)
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    return passed == total


def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("UNIFIED LINKTYPE TESTS")
    print("=" * 60)

    all_passed = True

    all_passed &= test_basic_linktype_creation()
    all_passed &= test_cardinality_enum()
    all_passed &= test_linktype_methods()

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
