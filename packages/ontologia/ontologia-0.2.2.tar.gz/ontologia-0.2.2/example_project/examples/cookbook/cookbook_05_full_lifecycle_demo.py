from __future__ import annotations

from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.testing import MockOntologyClient


def main() -> None:
    client = MockOntologyClient()

    client.upsert_object("company", "c1", {"name": "Initech"})
    client.upsert_object(
        "employee",
        "e1",
        {"name": "Alice", "dept": "ENG"},
    )
    client.create_link("works_for", "e1", "c1", {"role": "Engineer"})

    engineer = Employee.get(client, "e1")
    print("Employee:", engineer.name, engineer.dept)

    assigned = engineer.works_for.all_typed()
    for edge in assigned.data:
        props = edge.link_properties
        print("Works for:", edge.to_pk, getattr(props, "role", None))

    client.register_action(
        "employee",
        "promote",
        parameters=[{"apiName": "level", "required": True}],
        handler=lambda pk, params: {"status": "success", "level": params["level"]},
    )
    result = engineer.actions.promote(level="L3")
    print("Action result:", result)

    client.delete_link("works_for", "e1", "c1")
    builder = Employee.search_builder(client)
    page = builder.where(Employee.dept == "ENG").all_typed()
    print("Engineering employees:", [emp.name for emp in page.data])


if __name__ == "__main__":
    main()
