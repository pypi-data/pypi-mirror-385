import pytest

from ontologia.domain.metamodel.aggregates import LinkAggregate, ObjectTypeAggregate
from ontologia.domain.metamodel.value_objects import PrimaryKeyDefinition, PropertyDefinition
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType


def _make_object_type() -> ObjectType:
    return ObjectType(
        service="ontology",
        instance="default",
        api_name="customer",
        display_name="Customer",
        description="",
        primary_key_field="id",
        version=1,
        is_latest=True,
        rid="ot#customer",
    )


def test_object_type_aggregate_requires_primary_key_present() -> None:
    ot = _make_object_type()
    props = [PropertyDefinition(api_name="name", data_type="string")]
    with pytest.raises(ValueError, match="Primary key 'id' must exist"):
        ObjectTypeAggregate.new(
            object_type=ot,
            properties=props,
            primary_key=PrimaryKeyDefinition("id"),
        )


def test_object_type_aggregate_normalizes_values() -> None:
    ot = _make_object_type()
    props = [
        PropertyDefinition(api_name="id", data_type="string", is_primary_key=True, required=True),
        PropertyDefinition(api_name="score", data_type="integer"),
    ]
    aggregate = ObjectTypeAggregate.new(
        object_type=ot,
        properties=props,
        primary_key=PrimaryKeyDefinition("id"),
    )
    normalized = aggregate.normalize_instance_properties("42", {"score": "10"})
    assert normalized["id"] == "42"
    assert normalized["score"] == 10


def test_object_type_aggregate_unknown_property_raises() -> None:
    ot = _make_object_type()
    props = [
        PropertyDefinition(api_name="id", data_type="string", is_primary_key=True, required=True),
    ]
    aggregate = ObjectTypeAggregate.new(
        object_type=ot,
        properties=props,
        primary_key=PrimaryKeyDefinition("id"),
    )
    with pytest.raises(ValueError, match="Unknown properties"):
        aggregate.normalize_instance_properties("1", {"unknown": "value"})


def _make_link_type() -> LinkType:
    lt = LinkType(
        service="ontology",
        instance="default",
        api_name="works_for",
        display_name="Works For",
        description="",
        cardinality=Cardinality.ONE_TO_ONE,
        from_object_type_api_name="employee",
        to_object_type_api_name="company",
        inverse_api_name="has_employees",
        inverse_display_name="Has employees",
        version=1,
        is_latest=True,
        rid="lt#works_for",
    )
    return lt


def _make_instance(object_type_api: str, pk: str, rid: str) -> ObjectInstance:
    return ObjectInstance(
        service="ontology",
        instance="default",
        api_name=f"{object_type_api}_{pk}",
        display_name=f"{object_type_api}:{pk}",
        object_type_api_name=object_type_api,
        object_type_rid=f"ot#{object_type_api}",
        pk_value=str(pk),
        data={},
        rid=rid,
    )


def test_link_aggregate_cardinality_enforced() -> None:
    lt = _make_link_type()
    aggregate = LinkAggregate(
        link_type=lt,
        from_instance=_make_instance("employee", "1", "inst#1"),
        to_instance=_make_instance("company", "acme", "inst#2"),
        properties={},
    )
    with pytest.raises(ValueError, match="Cardinality violation"):
        aggregate.validate_cardinality(forward_degree=1, inverse_degree=0)


def test_link_aggregate_build_model_populates_metadata() -> None:
    lt = _make_link_type()
    from_inst = _make_instance("employee", "1", "inst#1")
    to_inst = _make_instance("company", "acme", "inst#2")
    aggregate = LinkAggregate(
        link_type=lt,
        from_instance=from_inst,
        to_instance=to_inst,
        properties={"note": "contractor"},
    )
    model = aggregate.build_model(service="ontology", instance="default")
    assert model.link_type_api_name == lt.api_name
    assert model.from_object_rid == from_inst.rid
    assert model.to_object_rid == to_inst.rid
    assert model.data["note"] == "contractor"
