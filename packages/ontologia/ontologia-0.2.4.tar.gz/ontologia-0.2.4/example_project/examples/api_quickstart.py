from __future__ import annotations

import os

from ontologia_sdk.client import OntologyClient
from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.testing import MockOntologyClient


def _make_client():
    base_url = os.getenv("ONTOLOGIA_API")
    if base_url:
        return OntologyClient(host=base_url)
    return MockOntologyClient()


def _bootstrap_data(client) -> None:
    client.upsert_object("company", "c1", {"name": "Initech"})
    client.upsert_object("employee", "e1", {"name": "Alice", "dept": "ENG"})
    client.create_link("works_for", "e1", "c1", {"role": "Engineer"})
    if isinstance(client, MockOntologyClient):
        client.register_action(
            "employee",
            "promote",
            parameters=[{"apiName": "level", "required": True}],
            handler=lambda pk, params: {"status": "success", "level": params["level"]},
        )


def main() -> None:
    client = _make_client()
    _bootstrap_data(client)

    employee = Employee.get(client, "e1")
    print("Employee:", employee.name, employee.dept)

    company_edges = employee.works_for.iter_pages_typed(page_size=1)
    first_page = next(company_edges)
    for edge in first_page.data:
        role = getattr(edge.link_properties, "role", None)
        print("Works for company", edge.to_pk, "role", role)

    query = Employee.search_builder(client)
    engineers = query.where(Employee.dept == "ENG").all_typed()
    print("Engineer count:", len(engineers.data))

    try:
        result = employee.actions.promote(level="L3")
        print("Action result:", result)
    except Exception as exc:  # pragma: no cover - execution depends on server-side actions
        print("Action not available:", exc)


if __name__ == "__main__":
    main()
