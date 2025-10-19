from fastapi.testclient import TestClient


class _StubGraphRepo:
    def __init__(self, *args, **kwargs):
        self._available = True

    def is_available(self) -> bool:
        return True

    def list_by_interface(self, interface_api_name: str, *, limit: int = 100, offset: int = 0):
        # Return deterministic rows as unified graph would
        return [
            {
                "objectTypeApiName": "employee",
                "pkValue": "e1",
                "properties": {"id": "e1", "name": "Alice"},
            },
            {
                "objectTypeApiName": "device",
                "pkValue": "d1",
                "properties": {"id": "d1", "name": "MacBook"},
            },
        ][offset : offset + limit]


def _put_interface(client: TestClient, api: str):
    return client.put(
        f"/v2/ontologies/default/interfaces/{api}",
        json={
            "displayName": api,
            "properties": {},
        },
    )


def _put_ot(client: TestClient, api: str, implements: list[str]):
    return client.put(
        f"/v2/ontologies/default/objectTypes/{api}",
        json={
            "displayName": api.title(),
            "primaryKey": "id",
            "properties": {
                "id": {"dataType": "string", "displayName": "ID", "required": True},
                "name": {"dataType": "string", "displayName": "Name", "required": False},
            },
            "implements": implements,
        },
    )


def _put_obj(client: TestClient, ot: str, pk: str, props: dict):
    return client.put(
        f"/v2/ontologies/default/objects/{ot}/{pk}", json={"properties": dict(props or {})}
    )


def test_interface_listing_uses_unified_graph_path(monkeypatch, client: TestClient):
    # Enable unified graph
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")

    # Patch InstancesService to use stub graph repo
    import api.services.instances_service as instances_service

    monkeypatch.setattr(instances_service, "GraphInstancesRepository", _StubGraphRepo)

    # Define interface and implementers
    _put_interface(client, "Identifiable")
    _put_ot(client, "employee", ["Identifiable"])
    _put_ot(client, "device", ["Identifiable"])

    # Seed some SQL instances (not read by stub, but keeps API consistent)
    _put_obj(client, "employee", "e1", {"name": "Alice"})
    _put_obj(client, "device", "d1", {"name": "MacBook"})

    # Call list by interface (InstancesService.list_objects will choose unified path)
    r = client.get("/v2/ontologies/default/objects/Identifiable")
    assert r.status_code == 200, r.text
    data = r.json()["data"]

    # Validate mapping comes from stub unified path
    assert {(it["objectTypeApiName"], it["pkValue"]) for it in data} == {
        ("employee", "e1"),
        ("device", "d1"),
    }
    props0 = data[0]["properties"]
    assert "id" in props0 and "name" in props0
