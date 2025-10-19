from __future__ import annotations

from fastapi.testclient import TestClient


def _seed_many_employees(client: TestClient, count: int = 200) -> None:
    client.put(
        "/v2/ontologies/default/objectTypes/employee",
        json={
            "displayName": "Employee",
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name"},
            },
        },
    )
    for idx in range(count):
        client.put(
            f"/v2/ontologies/default/objects/employee/e{idx}",
            json={"properties": {"id": f"e{idx}", "name": f"Employee {idx}"}},
        )


def test_employee_listing_benchmark(client: TestClient, benchmark):
    _seed_many_employees(client)

    def query():
        resp = client.get(
            "/v2/ontologies/default/objects",
            params={"objectType": "employee", "limit": 50},
        )
        assert resp.status_code == 200
        return resp.json()

    benchmark(query)
