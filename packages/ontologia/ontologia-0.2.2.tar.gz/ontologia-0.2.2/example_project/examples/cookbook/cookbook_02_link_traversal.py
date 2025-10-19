from __future__ import annotations

from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.testing import MockOntologyClient


def main() -> None:
    client = MockOntologyClient()
    client.upsert_object("employee", "e1", {"name": "Alice"})
    client.upsert_object("company", "c1", {"name": "Initech"})
    client.create_link("works_for", "e1", "c1", {"role": "Engineer"})

    employee = Employee.get(client, "e1")
    traversal = employee.works_for.list_typed()
    for edge in traversal.data:
        props = edge.link_properties
        role = getattr(props, "role", None)
        print(f"{employee.name} works for company {edge.to_pk} as {role}")


if __name__ == "__main__":
    main()
