from __future__ import annotations

from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.testing import MockOntologyClient


def main() -> None:
    client = MockOntologyClient()
    client.upsert_object("employee", "e1", {"name": "Alice"})
    client.register_action(
        "employee",
        "promote",
        parameters=[{"apiName": "level", "required": True}],
        handler=lambda pk, params: {"pk": pk, "level": params["level"]},
    )

    employee = Employee.get(client, "e1")
    result = employee.actions.promote(level="L3")
    print(f"Promotion result: {result}")


if __name__ == "__main__":
    main()
