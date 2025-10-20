from ontologia_cli import main as cli_main


def test_generate_sdk_links_and_helpers(tmp_path, monkeypatch):
    # Arrange: stub server state with one object and one link with properties
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
            },
            "company": {
                "apiName": "company",
                "displayName": "Company",
                "primaryKey": "id",
                "properties": {
                    "id": {"dataType": "string", "displayName": "ID", "required": True},
                    "name": {"dataType": "string", "displayName": "Name", "required": False},
                },
            },
        }
        links_remote = {
            "works_for": {
                "apiName": "works_for",
                "displayName": "Works For",
                "fromObjectType": "employee",
                "toObjectType": "company",
                "properties": {
                    "role": {"dataType": "string", "displayName": "Role", "required": True},
                    "sinceDate": {"dataType": "date", "displayName": "Since", "required": False},
                },
            }
        }
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

    # Links module
    links_py = out_dir / "links.py"
    assert links_py.exists(), "links.py was not generated"
    text_links = links_py.read_text(encoding="utf-8")
    assert "class WorksForLinkProperties(BaseLinkProperties):" in text_links
    assert 'link_type_api_name = "works_for"' in text_links
    assert "role: str" in text_links
    assert "sinceDate: datetime.date | None" in text_links

    # Objects module contains helpers for works_for
    objects_py = out_dir / "objects.py"
    assert objects_py.exists(), "objects.py was not generated"
    text_objects = objects_py.read_text(encoding="utf-8")
    # traversal and get_link
    assert "def traverse_works_for(self, limit: int = 100, offset: int = 0):" in text_objects
    assert "def get_works_for_link(self, to_pk: str):" in text_objects
    # create/delete/list helpers
    assert (
        "def create_works_for(self, to_pk: str, properties: dict[str, typing.Any] | None = None):"
        in text_objects
    )
    assert "def delete_works_for(self, to_pk: str) -> None:" in text_objects
    assert "def list_works_for(self, to_pk: str | None = None):" in text_objects
    assert 'works_for = LinkDescriptor("works_for"' in text_objects
