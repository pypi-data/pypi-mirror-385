from __future__ import annotations

from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.testing import MockOntologyClient


def main() -> None:
    client = MockOntologyClient()
    client.upsert_object("employee", "e1", {"name": "Alice", "dept": "ENG"})
    client.upsert_object("employee", "e2", {"name": "Bob", "dept": "OPS"})
    client.upsert_object("employee", "e3", {"name": "Carol", "dept": "ENG"})

    qb = Employee.search_builder(client)
    page = qb.where(Employee.dept == "ENG").order_by(Employee.name.asc()).all_typed()

    for employee in page.data:
        print(f"Engineer: {employee.name}")


if __name__ == "__main__":
    main()
