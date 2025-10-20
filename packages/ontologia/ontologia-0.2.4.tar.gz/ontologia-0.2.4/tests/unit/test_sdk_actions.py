import pytest

from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.testing import MockOntologyClient


def test_client_actions_namespace_executes_with_validation():
    client = MockOntologyClient()
    client.upsert_object("employee", "e1", {"name": "Alice"})
    client.register_action(
        "employee",
        "promote",
        parameters=[{"apiName": "level", "required": True}],
        handler=lambda pk, params: {"pk": pk, "level": params["level"]},
    )

    result = client.actions.promote(object_type="employee", pk="e1", level="L3")
    assert result == {"pk": "e1", "level": "L3"}

    with pytest.raises(ValueError):
        client.actions.promote(object_type="employee", pk="e1")


def test_object_actions_namespace_uses_client_namespace():
    client = MockOntologyClient()
    client.upsert_object("employee", "e1", {"name": "Alice"})
    client.register_action(
        "employee",
        "promote",
        parameters=[{"apiName": "level", "required": True}],
    )

    employee = Employee.get(client, "e1")
    result = employee.actions.promote(level="L3")
    assert result["action"] == "promote"
    assert result["parameters"]["level"] == "L3"

    available = employee.actions.available()
    assert any(a.get("apiName") == "promote" for a in available)
