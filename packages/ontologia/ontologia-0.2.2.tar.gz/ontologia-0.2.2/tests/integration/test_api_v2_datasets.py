from fastapi.testclient import TestClient


def test_datasets_crud_branches_transactions(client: TestClient):
    # Create dataset
    r = client.put(
        "/v2/ontologies/default/datasets/sales_gold",
        json={
            "displayName": "Sales (Gold)",
            "sourceType": "duckdb_table",
            "sourceIdentifier": "gold.sales",
            "schemaDefinition": {"columns": [{"name": "id", "type": "string"}]},
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["apiName"] == "sales_gold"

    # Get dataset
    g = client.get("/v2/ontologies/default/datasets/sales_gold")
    assert g.status_code == 200

    # List datasets
    lst = client.get("/v2/ontologies/default/datasets")
    assert lst.status_code == 200
    names = [d["apiName"] for d in lst.json()["data"]]
    assert "sales_gold" in names

    # Create transaction
    tx = client.post(
        "/v2/ontologies/default/datasets/sales_gold/transactions",
        json={"transactionType": "SNAPSHOT", "commitMessage": "initial"},
    )
    assert tx.status_code == 200, tx.text
    tx_rid = tx.json()["rid"]

    # Create branch pointing to the transaction
    br = client.put(
        "/v2/ontologies/default/datasets/sales_gold/branches/main",
        json={"headTransactionRid": tx_rid},
    )
    assert br.status_code == 200, br.text

    # List branches
    bl = client.get("/v2/ontologies/default/datasets/sales_gold/branches")
    assert bl.status_code == 200
    assert any(b["branchName"] == "main" for b in bl.json()["data"])
