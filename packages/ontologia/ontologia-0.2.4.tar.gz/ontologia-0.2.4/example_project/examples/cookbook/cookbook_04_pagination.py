from __future__ import annotations

from ontologia_sdk.ontology.objects import Employee
from ontologia_sdk.testing import MockOntologyClient


def main() -> None:
    client = MockOntologyClient()
    for idx in range(1, 7):
        client.upsert_object(
            "employee",
            f"e{idx}",
            {"name": f"Employee {idx}", "dept": "ENG" if idx % 2 else "OPS"},
        )

    qb = Employee.search_builder(client)
    for page_number, page in enumerate(
        qb.order_by(Employee.name.asc()).iter_pages_typed(page_size=2), start=1
    ):
        names = [record.name for record in page.data]
        print(f"Page {page_number}: {names}")


if __name__ == "__main__":
    main()
