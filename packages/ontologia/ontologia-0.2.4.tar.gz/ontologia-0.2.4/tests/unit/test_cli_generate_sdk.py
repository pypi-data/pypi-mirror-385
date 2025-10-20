from ontologia_cli import main as cli_main


def test_generate_sdk_creates_modules(tmp_path, monkeypatch):
    # Arrange: stub server state
    def fake_fetch(host: str, ontology: str):
        objs_remote = {
            "employee": {
                "apiName": "employee",
                "displayName": "Employee",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                    "name": {"dataType": "string", "displayName": "Name", "required": False},
                },
            }
        }
        links_remote = {}
        return objs_remote, links_remote

    monkeypatch.setattr(cli_main, "_fetch_server_state", fake_fetch)

    out_dir = tmp_path / "sdk"
    # Act: run CLI
    code = cli_main.main(
        [
            "generate-sdk",
            "--host",
            "http://localhost:8000",
            "--ontology",
            "default",
            "--out",
            str(out_dir),
        ]
    )

    # Assert
    assert code == 0
    assert (out_dir / "__init__.py").exists()
    objects_py = out_dir / "objects.py"
    assert objects_py.exists(), "objects.py was not generated"
    text = objects_py.read_text(encoding="utf-8")
    assert "class ObjectTypeMeta" in text
    assert "class Employee(BaseObject):" in text
    assert 'object_type_api_name = "employee"' in text
    assert "__fields__" in text
    assert "if typing.TYPE_CHECKING:" in text
    assert "def search_typed(" in text
    assert "def iter_search(" in text
