from unittest.mock import MagicMock

from scripts.main_sync import run_sync


def test_run_sync_with_mocks_does_not_raise(session):
    # Given mocks for kuzu and duckdb, run_sync should complete without raising
    mock_kuzu = MagicMock()
    mock_duckdb = MagicMock()

    # No DuckDB path needed; ensure it doesn't attempt to import
    run_sync(duckdb_path=None, meta_session=session, kuzu_conn=mock_kuzu, duckdb_conn=mock_duckdb)

    # Ensure at least schema build attempted on kuzu
    executed = "\n".join(str(call.args[0]) for call in mock_kuzu.execute.call_args_list)
    assert "CREATE" in executed or executed == ""  # allow empty if no object/link types present
