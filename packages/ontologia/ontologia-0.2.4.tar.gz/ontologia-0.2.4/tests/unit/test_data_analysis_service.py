import sqlite3
from pathlib import Path
from typing import Any

import pytest

from api.services.data_analysis_service import DataAnalysisService


def _write_sample_csv(path: Path) -> None:
    path.write_text(
        """transaction_id,product_sku,customer_id,amount
1,SKU-1,CUST-1,10.5
2,SKU-2,CUST-1,20.0
3,SKU-1,CUST-2,
""",
        encoding="utf-8",
    )


def test_profile_source_returns_schema(tmp_path: Path) -> None:
    csv_path = tmp_path / "sales.csv"
    _write_sample_csv(csv_path)

    service = DataAnalysisService()
    profile = service.profile_source(csv_path, sample_size=10)

    assert profile["source_path"] == str(csv_path)
    assert profile["rows_profiled"] == 3
    columns = {col["name"]: col for col in profile["columns"]}
    assert set(columns) == {"transaction_id", "product_sku", "customer_id", "amount"}
    assert columns["transaction_id"]["inferred_type"] == "int"
    assert columns["transaction_id"]["is_highly_unique"] is True
    assert columns["transaction_id"]["unique_count_in_sample"] == 3
    assert columns["amount"]["inferred_type"] == "float"
    assert columns["amount"]["null_count_in_sample"] == 1
    assert columns["amount"]["example_values"] == ["10.5", "20.0"]


def test_profile_source_rejects_invalid_extension(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    path.write_text("{}", encoding="utf-8")

    service = DataAnalysisService()
    with pytest.raises(ValueError):
        service.profile_source(path, sample_size=5)


def test_profile_source_requires_positive_sample(tmp_path: Path) -> None:
    csv_path = tmp_path / "sales.csv"
    _write_sample_csv(csv_path)

    service = DataAnalysisService()
    with pytest.raises(ValueError):
        service.profile_source(csv_path, sample_size=0)


def test_profile_sql_table_returns_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "example.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE sales (id INTEGER PRIMARY KEY, sku TEXT, amount REAL, active TEXT)"
        )
        conn.executemany(
            "INSERT INTO sales (sku, amount, active) VALUES (?, ?, ?)",
            [
                ("SKU-1", 10.5, "true"),
                ("SKU-2", 20.0, "false"),
                ("SKU-3", None, None),
            ],
        )
        conn.commit()
    finally:
        conn.close()

    service = DataAnalysisService()
    profile = service.profile_sql_table(f"sqlite:///{db_path}", "sales", sample_size=5)

    assert profile["rows_profiled"] == 3
    columns = {col["name"]: col for col in profile["columns"]}
    assert columns["id"]["inferred_type"] == "int"
    assert columns["amount"]["inferred_type"] == "float"
    assert columns["active"]["inferred_type"] == "bool"
    assert columns["amount"]["null_count_in_sample"] == 1


def test_profile_rest_endpoint_handles_nested_array(monkeypatch) -> None:
    sample_payload = {
        "data": {
            "items": [
                {"id": 1, "sku": "SKU-1", "amount": 5.0},
                {"id": 2, "sku": "SKU-2", "amount": 7.5},
                {"id": 3, "sku": "SKU-3", "amount": 9.0},
            ]
        }
    }

    class FakeResponse:
        def raise_for_status(self) -> None:  # noqa: D401 - simple stub
            return None

        def json(self) -> dict[str, Any]:
            return sample_payload

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:  # noqa: D401 - simple stub
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args, **kwargs) -> None:  # noqa: D401
            return None

        def request(self, method, url, headers=None):  # noqa: D401
            assert method == "GET"
            assert url == "https://example.com/data"
            return FakeResponse()

    monkeypatch.setattr(
        "api.services.data_analysis_service.httpx.Client",
        FakeClient,
    )

    service = DataAnalysisService()
    profile = service.profile_rest_endpoint(
        "https://example.com/data",
        sample_size=2,
        array_path="data.items",
    )

    assert profile["rows_profiled"] == 2
    columns = {col["name"]: col for col in profile["columns"]}
    assert columns["sku"]["unique_count_in_sample"] == 2
    assert columns["amount"]["inferred_type"] == "float"
