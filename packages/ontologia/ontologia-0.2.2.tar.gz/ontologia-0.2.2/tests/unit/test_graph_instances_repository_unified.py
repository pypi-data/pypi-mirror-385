from unittest.mock import MagicMock

from api.repositories.graph_instances_repository import GraphInstancesRepository


class _Row:
    def __init__(self, d):
        self._d = d

    def __getitem__(self, k):
        return self._d[k]

    def get(self, k, default=None):
        return self._d.get(k, default)


class _DF:
    def __init__(self, rows):
        self._rows = [_Row(r) for r in rows]
        self.columns = list(rows[0].keys()) if rows else []
        # mimic pandas' .iloc indexer
        self.iloc = self

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, idx):
        return self._rows[idx]


class _Result:
    def __init__(self, df):
        self._df = df

    def get_as_df(self):  # noqa: D401
        return self._df


def test_list_by_interface_unified_uses_object_and_labels(monkeypatch):
    # enable unified graph
    monkeypatch.setenv("USE_UNIFIED_GRAPH", "1")

    # mock kuzu repo
    mock_kuzu = MagicMock()
    mock_kuzu.is_available.return_value = True
    rows = [
        {
            "objectTypeApiName": "employee",
            "pkValue": "e1",
            "properties": '{"id":"e1","name":"Alice"}',
        },
        {
            "objectTypeApiName": "employee",
            "pkValue": "e2",
            "properties": '{"id":"e2","name":"Bob"}',
        },
    ]
    df = _DF(rows)
    mock_kuzu.execute.return_value = _Result(df)

    repo = GraphInstancesRepository(kuzu_repo=mock_kuzu, session=None)

    out = repo.list_by_interface("person", limit=10, offset=0)

    # verify mapping
    assert len(out) == 2
    assert out[0]["objectTypeApiName"] == "employee"
    assert out[0]["pkValue"] == "e1"
    assert out[0]["properties"]["name"] == "Alice"

    # verify query shape
    executed = "\n".join(str(call.args[0]) for call in mock_kuzu.execute.call_args_list)
    assert "MATCH (o:Object)" in executed
    assert "IN o.labels" in executed
    assert (
        "RETURN o.objectTypeApiName AS objectTypeApiName, o.pkValue AS pkValue, o.properties AS properties"
        in executed
    )
