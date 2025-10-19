from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def test_contract_shapes_querytypes_and_datasets():
    client = TestClient(app)
    spec = client.get("/openapi.json").json()

    assert "paths" in spec and "components" in spec and "schemas" in spec["components"]
    paths = spec["paths"]
    schemas = spec["components"]["schemas"]

    # QueryTypes endpoints exist
    assert "/v2/ontologies/{ontologyApiName}/queryTypes/{queryApiName}" in paths
    assert "/v2/ontologies/{ontologyApiName}/queries/{queryApiName}/execute" in paths

    # Verify schema fields for aliases
    qt_put = schemas["QueryTypePutRequest"]["properties"]
    assert "targetApiName" in qt_put
    assert "targetObjectType" in qt_put
    assert "query" in qt_put

    qt_read = schemas["QueryTypeReadResponse"]["properties"]
    assert "targetApiName" in qt_read
    assert "query" in qt_read

    # Datasets DELETE endpoint exists
    assert "/v2/ontologies/{ontologyApiName}/datasets/{datasetApiName}" in paths
    ds_item = paths["/v2/ontologies/{ontologyApiName}/datasets/{datasetApiName}"]
    assert "delete" in ds_item
