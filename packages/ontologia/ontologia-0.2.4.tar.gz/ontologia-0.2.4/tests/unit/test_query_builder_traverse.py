from unittest.mock import MagicMock

from ontologia_sdk.query import QueryBuilder


def test_query_builder_traverse_emits_step():
    client = MagicMock()
    qb = QueryBuilder(client=client, object_type="employee")

    qb.where({"property": "name", "op": "eq", "value": "Alice"}).traverse(
        "works_in",
        where={"property": "name", "op": "eq", "value": "Engineering"},
    ).all()

    assert client.search_objects.called
    _, kwargs = client.search_objects.call_args
    assert kwargs["traverse"] == [
        {
            "link": "works_in",
            "direction": "forward",
            "where": [
                {"property": "name", "op": "eq", "value": "Engineering"},
            ],
        }
    ]
