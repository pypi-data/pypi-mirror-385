def test_interface_crud(client):
    base = "/v2/ontologies/default"

    # Create Interface
    resp = client.put(
        f"{base}/interfaces/Localizavel",
        json={
            "displayName": "Localizável",
            "description": "Qualquer coisa com endereço.",
            "properties": {"address": {"dataType": "string", "displayName": "Address"}},
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["apiName"] == "Localizavel"
    assert body["displayName"] == "Localizável"
    assert "rid" in body
    assert body["version"] == 1
    assert body["isLatest"] is True

    # Get Interface
    resp = client.get(f"{base}/interfaces/Localizavel")
    assert resp.status_code == 200
    body = resp.json()
    assert body["apiName"] == "Localizavel"

    # List Interfaces
    resp = client.get(f"{base}/interfaces")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(item["apiName"] == "Localizavel" and item["version"] == 1 for item in data)

    # Update Interface
    resp = client.put(
        f"{base}/interfaces/Localizavel",
        json={
            "displayName": "Localizável 2",
            "description": "Atualizada",
            "properties": {"address": {"dataType": "string", "displayName": "Endereço"}},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["displayName"] == "Localizável 2"
    assert body["version"] == 2
    assert body["isLatest"] is True

    # Delete Interface
    resp = client.delete(f"{base}/interfaces/Localizavel")
    assert resp.status_code == 204

    # Ensure gone
    resp = client.get(f"{base}/interfaces/Localizavel")
    assert resp.status_code == 404
