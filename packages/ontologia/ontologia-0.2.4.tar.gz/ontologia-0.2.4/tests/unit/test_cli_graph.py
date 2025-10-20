from pathlib import Path

from typer.testing import CliRunner

from ontologia.config import load_config
from ontologia_cli.main import app


def test_graph_reset_removes_graph_storage(tmp_path):
    manifest = tmp_path / "ontologia.toml"
    manifest.write_text(
        """
[data]
kuzu_path = "graph"
"""
    )

    runner = CliRunner()
    with runner.isolated_filesystem() as fs_dir:
        # Prepare manifest and graph directory inside isolated FS
        fs_path = Path(fs_dir)
        (fs_path / "ontologia.toml").write_text(
            manifest.read_text(encoding="utf-8"), encoding="utf-8"
        )
        graph_dir = fs_path / "graph"
        graph_dir.mkdir()

        load_config.cache_clear()
        result = runner.invoke(app, ["graph", "reset", "--yes"])

        assert result.exit_code == 0
        assert not graph_dir.exists()
