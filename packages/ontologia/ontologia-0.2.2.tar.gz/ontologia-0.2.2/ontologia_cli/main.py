from __future__ import annotations

# ruff: noqa: FBT002
import asyncio
import json
import os
import secrets
import shutil
import socket
import subprocess
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Literal

import httpx
import questionary
import typer
from git import Actor, Repo
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from sqlalchemy import true
from typer.testing import CliRunner

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

from api.v2.schemas.metamodel import LinkTypePutRequest, ObjectTypePutRequest
from ontologia_agent import AgentPlan, ArchitectAgent, ProjectState
from ontologia_cli.config import load_config

console = Console()

CONFIG_DIR = Path.home() / ".ontologia"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOCAL_STATE_DIR = ".ontologia"
LOCAL_STATE_FILE = "state.json"

_CONFIG = load_config()
DEFAULT_HOST = _CONFIG.api.base_url
DEFAULT_ONTOLOGY = _CONFIG.api.ontology
DEFAULT_DEFINITIONS_DIR = _CONFIG.project.definitions_dir
DEFAULT_SDK_DIR = _CONFIG.sdk.output_dir


@dataclass
class PlanItem:
    kind: str  # objectType | linkType
    api_name: str
    action: str  # create | update | delete
    dangerous: bool = False
    reasons: list[str] = field(default_factory=list)


def _load_yaml_file(path: str) -> dict:
    if yaml is None:
        raise RuntimeError("pyyaml is required. Install with: uvx pip install pyyaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _collect_definitions(root_dir: str) -> tuple[dict[str, dict], dict[str, dict]]:
    obj_dir = os.path.join(root_dir, "object_types")
    link_dir = os.path.join(root_dir, "link_types")
    objs: dict[str, dict] = {}
    links: dict[str, dict] = {}

    if os.path.isdir(obj_dir):
        for fn in os.listdir(obj_dir):
            if fn.endswith((".yml", ".yaml")):
                raw = _load_yaml_file(os.path.join(obj_dir, fn))
                api_name = str(raw.get("apiName") or os.path.splitext(fn)[0])
                objs[api_name] = raw

    if os.path.isdir(link_dir):
        for fn in os.listdir(link_dir):
            if fn.endswith((".yml", ".yaml")):
                raw = _load_yaml_file(os.path.join(link_dir, fn))
                api_name = str(raw.get("apiName") or os.path.splitext(fn)[0])
                links[api_name] = raw

    return objs, links


def _validate_local(objs: dict[str, dict], links: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    for api_name, raw in objs.items():
        body = {k: v for k, v in raw.items() if k != "apiName"}
        try:
            ObjectTypePutRequest(**body)
        except ValidationError as ve:
            errors.append(f"ObjectType '{api_name}' invalid: {ve}")
    for api_name, raw in links.items():
        body = {k: v for k, v in raw.items() if k != "apiName"}
        try:
            LinkTypePutRequest(**body)
        except ValidationError as ve:
            errors.append(f"LinkType '{api_name}' invalid: {ve}")
    return errors


def _fetch_server_state(host: str, ontology: str) -> tuple[dict[str, dict], dict[str, dict]]:
    base = host.rstrip("/") + f"/v2/ontologies/{ontology}"
    with httpx.Client(timeout=30) as client:
        obj_resp = client.get(base + "/objectTypes")
        obj_resp.raise_for_status()
        obj_data = obj_resp.json().get("data", [])
        objs = {it["apiName"]: it for it in obj_data}

        link_resp = client.get(base + "/linkTypes")
        link_resp.raise_for_status()
        link_data = link_resp.json().get("data", [])
        links = {it["apiName"]: it for it in link_data}
    return objs, links


def _plan(
    objs_local: dict[str, dict],
    links_local: dict[str, dict],
    objs_remote: dict[str, dict],
    links_remote: dict[str, dict],
) -> list[PlanItem]:
    plan: list[PlanItem] = []
    for api_name in objs_local.keys():
        if api_name not in objs_remote:
            plan.append(PlanItem("objectType", api_name, "create"))
        else:
            local = objs_local[api_name]
            remote = objs_remote[api_name]
            if (
                (local.get("displayName") != remote.get("displayName"))
                or (local.get("properties") != remote.get("properties"))
                or (local.get("primaryKey") != remote.get("primaryKey"))
            ):
                reasons: list[str] = []
                if local.get("primaryKey") != remote.get("primaryKey"):
                    reasons.append("primaryKey change")
                remote_props = dict(remote.get("properties") or {})
                local_props = dict(local.get("properties") or {})
                for prop_name in remote_props.keys() - local_props.keys():
                    reasons.append(f"property removed: {prop_name}")
                for prop_name, local_prop in local_props.items():
                    if prop_name not in remote_props:
                        continue
                    remote_prop = remote_props.get(prop_name) or {}
                    if (local_prop or {}).get("dataType") != remote_prop.get("dataType"):
                        reasons.append(
                            f"property type change: {prop_name} ({remote_prop.get('dataType')}→{(local_prop or {}).get('dataType')})"
                        )
                plan.append(
                    PlanItem(
                        "objectType",
                        api_name,
                        "update",
                        dangerous=bool(reasons),
                        reasons=reasons,
                    )
                )
    for api_name in set(objs_remote.keys()) - set(objs_local.keys()):
        plan.append(PlanItem("objectType", api_name, "delete", dangerous=True, reasons=["delete"]))
    for api_name in links_local.keys():
        if api_name not in links_remote:
            plan.append(PlanItem("linkType", api_name, "create"))
        else:
            local = links_local[api_name]
            remote = links_remote[api_name]
            fields = [
                "displayName",
                "cardinality",
                "fromObjectType",
                "toObjectType",
                "inverse",
                "description",
                "properties",
                "backingDatasetApiName",
                "fromPropertyMapping",
                "toPropertyMapping",
                "propertyMappings",
                "incrementalField",
            ]
            if any(local.get(f) != remote.get(f) for f in fields):
                reasons: list[str] = []
                if local.get("fromObjectType") != remote.get("fromObjectType") or local.get(
                    "toObjectType"
                ) != remote.get("toObjectType"):
                    reasons.append("endpoint change")
                plan.append(
                    PlanItem(
                        "linkType",
                        api_name,
                        "update",
                        dangerous=bool(reasons),
                        reasons=reasons,
                    )
                )
    for api_name in set(links_remote.keys()) - set(links_local.keys()):
        plan.append(PlanItem("linkType", api_name, "delete", dangerous=True, reasons=["delete"]))
    return plan


def _apply(
    host: str,
    ontology: str,
    plan: list[PlanItem],
    objs_local: dict[str, dict],
    links_local: dict[str, dict],
    *,
    allow_destructive: bool = False,
) -> None:
    base = host.rstrip("/") + f"/v2/ontologies/{ontology}"
    with httpx.Client(timeout=30) as client:
        for item in plan:
            try:
                if item.dangerous and not allow_destructive:
                    raise RuntimeError(
                        f"Refusing dangerous {item.kind} {item.api_name} without --allow-destructive"
                    )
                if item.action == "delete":
                    if not allow_destructive:
                        raise RuntimeError(
                            f"Refusing to delete {item.kind} {item.api_name} without --allow-destructive"
                        )
                    if item.kind == "objectType":
                        client.delete(base + f"/objectTypes/{item.api_name}").raise_for_status()
                    else:
                        client.delete(base + f"/linkTypes/{item.api_name}").raise_for_status()
                elif item.kind == "objectType":
                    body = {k: v for k, v in objs_local[item.api_name].items() if k != "apiName"}
                    client.put(base + f"/objectTypes/{item.api_name}", json=body).raise_for_status()
                else:
                    body = {k: v for k, v in links_local[item.api_name].items() if k != "apiName"}
                    client.put(base + f"/linkTypes/{item.api_name}", json=body).raise_for_status()
                print(f"[OK] {item.action.upper()} {item.kind} {item.api_name}")
            except httpx.HTTPError as e:
                print(f"[ERR] {item.kind} {item.api_name}: {e}")
                raise


def _to_camel(name: str) -> str:
    parts = [p for p in str(name).replace("-", "_").split("_") if p]
    return "".join(s[:1].upper() + s[1:] for s in parts) or "X"


def _py_type_of(data_type: str, *, required: bool) -> str:
    mapping = {
        "string": "str",
        "integer": "int",
        "double": "float",
        "boolean": "bool",
        "date": "datetime.date",
        "timestamp": "datetime.datetime",
    }
    base = mapping.get(str(data_type), "typing.Any")
    return base if required else f"{base} | None"


def _python_literal(value: object) -> str:
    if isinstance(value, dict):
        inner = ", ".join(f'"{k}": {_python_literal(v)}' for k, v in value.items())
        return "{" + inner + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_python_literal(v) for v in value) + "]"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value is True:
        return "True"
    if value is False:
        return "False"
    if value is None:
        return "None"
    return repr(value)


def _generate_objects_module(
    out_dir: str, objs_remote: dict[str, dict], links_remote: dict[str, dict]
) -> None:
    os.makedirs(out_dir, exist_ok=True)
    link_classes = sorted([_to_camel(lt_api) + "LinkProperties" for lt_api in links_remote.keys()])
    object_classes = sorted([_to_camel(api_name) for api_name in objs_remote.keys()])

    init_path = os.path.join(out_dir, "__init__.py")
    with open(init_path, "w", encoding="utf-8") as f:
        f.write("# Generated by ontologia-cli generate-sdk\n")
        if link_classes:
            f.write("from .links import " + ", ".join(link_classes) + "\n")
        if object_classes:
            f.write("from .objects import " + ", ".join(object_classes) + "\n")
        names = link_classes + object_classes
        if names:
            f.write("\n__all__ = [" + ", ".join(f'"{n}"' for n in names) + "]\n")

    uses_datetime = False
    for ot in objs_remote.values():
        for prop_def in (ot.get("properties") or {}).values():
            if str(prop_def.get("dataType")) in {"date", "timestamp"}:
                uses_datetime = True
                break
        if uses_datetime:
            break

    import_lines: list[str] = ["from __future__ import annotations", ""]
    if uses_datetime:
        import_lines.append("import datetime")
    import_lines.append("import typing")
    import_lines.append("")
    import_lines.extend(
        [
            "from ontologia_sdk.actions import ObjectActionsNamespace",
            "from ontologia_sdk.client import OntologyClient",
            "from ontologia_sdk.dsl import FieldDescriptor",
            "from ontologia_sdk.link_proxy import LinkDescriptor",
            "from ontologia_sdk.query import QueryBuilder",
            "from ontologia_sdk.types import Page",
        ]
    )
    if link_classes:
        import_lines.append("")
        import_lines.append("from .links import " + ", ".join(link_classes))
    import_lines.append("")
    import_lines += [
        "",
        "class ObjectTypeMeta(type):",
        "    def __getattr__(cls, item: str) -> FieldDescriptor:",
        '        fields = getattr(cls, "__fields__", {})',
        "        if item in fields:",
        "            return FieldDescriptor(cls.object_type_api_name, item, fields[item])",
        "        raise AttributeError(item)",
        "",
        "class BaseObject(metaclass=ObjectTypeMeta):",
        '    object_type_api_name: str = ""',
        '    primary_key: str = ""',
        "    __fields__: dict[str, dict[str, typing.Any]] = {}",
        "",
        "    def __init__(self, client: OntologyClient, rid: str, pkValue: str, properties: dict[str, typing.Any]):",
        "        self._client = client",
        "        self.rid = rid",
        "        self.pk = pkValue",
        "        for k, v in dict(properties or {}).items():",
        "            setattr(self, k, v)",
        '        shared_actions = getattr(client, "actions", None)',
        "        self.actions = ObjectActionsNamespace(",
        "            client=client,",
        "            object_type=self.object_type_api_name,",
        "            pk_getter=lambda: self.pk,",
        "            shared_namespace=shared_actions,",
        "        )",
        "",
        "    @classmethod",
        "    def get(cls, client: OntologyClient, pk: str):",
        "        data = client.get_object(cls.object_type_api_name, pk)",
        "        return cls.from_response(client, data)",
        "",
        "    @classmethod",
        "    def from_response(cls, client: OntologyClient, data: dict[str, typing.Any]):",
        '        props = dict(data.get("properties") or {})',
        '        return cls(client, data.get("rid", ""), str(data.get("pkValue", "")), props)',
        "",
        "    @classmethod",
        "    def search(",
        "        cls,",
        "        client: OntologyClient,",
        "        where: list[dict] | None = None,",
        "        order_by: list[dict] | None = None,",
        "        limit: int = 100,",
        "        offset: int = 0,",
        "    ):",
        "        qb = cls.search_builder(client)",
        "        if where:",
        "            qb.where(where)",
        "        if order_by:",
        "            qb.order_by(order_by)",
        "        qb.limit(limit)",
        "        qb.offset(offset)",
        "        return qb.all()",
        "",
        "    @classmethod",
        "    def search_typed(",
        "        cls,",
        "        client: OntologyClient,",
        "        where: list[dict] | None = None,",
        "        order_by: list[dict] | None = None,",
        "        limit: int = 100,",
        "        offset: int = 0,",
        "    ) -> Page[typing.Any]:",
        "        qb = cls.search_builder(client)",
        "        if where:",
        "            qb.where(where)",
        "        if order_by:",
        "            qb.order_by(order_by)",
        "        qb.limit(limit)",
        "        qb.offset(offset)",
        "        return qb.all_typed()",
        "",
        "    @classmethod",
        "    def iter_search(",
        "        cls,",
        "        client: OntologyClient,",
        "        where: list[dict] | None = None,",
        "        order_by: list[dict] | None = None,",
        "        page_size: int = 100,",
        "        offset: int = 0,",
        "    ):",
        "        qb = cls.search_builder(client)",
        "        if where:",
        "            qb.where(where)",
        "        if order_by:",
        "            qb.order_by(order_by)",
        "        qb.limit(page_size)",
        "        qb.offset(offset)",
        "        return qb.iter_pages(page_size=page_size)",
        "",
        "    @classmethod",
        "    def iter_search_typed(",
        "        cls,",
        "        client: OntologyClient,",
        "        where: list[dict] | None = None,",
        "        order_by: list[dict] | None = None,",
        "        page_size: int = 100,",
        "        offset: int = 0,",
        "    ):",
        "        qb = cls.search_builder(client)",
        "        if where:",
        "            qb.where(where)",
        "        if order_by:",
        "            qb.order_by(order_by)",
        "        qb.limit(page_size)",
        "        qb.offset(offset)",
        "        return qb.iter_pages_typed(page_size=page_size)",
        "",
        "    @classmethod",
        "    def search_builder(cls, client: OntologyClient) -> QueryBuilder:",
        "        return QueryBuilder(client=client, object_type=cls.object_type_api_name, object_cls=cls)",
        "",
        "    @classmethod",
        "    def field(cls, name: str) -> FieldDescriptor:",
        '        fields = getattr(cls, "__fields__", {})',
        "        if name not in fields:",
        "            raise AttributeError(name)",
        "        return FieldDescriptor(cls.object_type_api_name, name, fields[name])",
        "",
        "    def list_actions(self):",
        "        return self._client.list_actions(self.object_type_api_name, self.pk)",
        "",
        "    def execute_action(self, action_api_name: str, parameters: dict[str, typing.Any] | None = None):",
        "        return self._client.execute_action(self.object_type_api_name, self.pk, action_api_name, parameters)",
        "",
    ]

    body_lines: list[str] = []
    ot_to_out_links: dict[str, list[str]] = {}
    for lt_api, lt in links_remote.items():
        src = str(lt.get("fromObjectType") or "")
        if src:
            ot_to_out_links.setdefault(src, []).append(lt_api)
    for api_name in sorted(objs_remote.keys()):
        ot = objs_remote[api_name] or {}
        cls_name = _to_camel(api_name)
        pk = str(ot.get("primaryKey") or "id")
        props: dict = dict(ot.get("properties") or {})
        body_lines.append("")
        body_lines.append(f"class {cls_name}(BaseObject):")
        body_lines.append(f'    object_type_api_name = "{api_name}"')
        body_lines.append(f'    primary_key = "{pk}"')
        if props:
            body_lines.append("    __fields__ = {")
            for prop_name, prop_def in props.items():
                serialized = _python_literal(prop_def)
                body_lines.append(f'        "{prop_name}": {serialized},')
            body_lines.append("    }")
        else:
            body_lines.append("    __fields__: dict[str, dict[str, typing.Any]] = {}")
        type_lines: list[str] = []
        for prop_name, prop_def in props.items():
            dt = _py_type_of(
                str(prop_def.get("dataType")), required=bool(prop_def.get("required", False))
            )
            type_lines.append(f"        {prop_name}: {dt}  # noqa: N815")
        if type_lines:
            body_lines.append("    if typing.TYPE_CHECKING:")
            body_lines.extend(type_lines)
        for lt_api in sorted(ot_to_out_links.get(api_name, [])):
            lt = links_remote.get(lt_api) or {}
            to_object = str(lt.get("toObjectType") or "")
            props_cls_name = _to_camel(lt_api) + "LinkProperties"
            body_lines.append("")
            body_lines.append(
                f'    {lt_api} = LinkDescriptor("{lt_api}", to_object_type="{to_object}", properties_cls={props_cls_name})'
            )
            body_lines.append("")
            body_lines.append(f"    # Links: {lt_api}")
            body_lines.append(
                f"    def traverse_{lt_api}(self, limit: int = 100, offset: int = 0):"
            )
            body_lines.append(
                f'        return self._client.traverse(self.object_type_api_name, self.pk, "{lt_api}", limit=limit, offset=offset)'
            )
            body_lines.append(f"    def get_{lt_api}_link(self, to_pk: str):")
            body_lines.append(f'        return self._client.get_link("{lt_api}", self.pk, to_pk)')
            cls_name = _to_camel(lt_api) + "LinkProperties"
            body_lines.append(f"    def get_{lt_api}_link_typed(self, to_pk: str):")
            body_lines.append(f'        raw = self._client.get_link("{lt_api}", self.pk, to_pk)')
            body_lines.append('        props = dict(raw.get("linkProperties") or {})')
            body_lines.append(f"        return {cls_name}.from_dict(props)")
            body_lines.append(
                f"    def create_{lt_api}(self, to_pk: str, properties: dict[str, typing.Any] | None = None):"
            )
            body_lines.append(
                f'        return self._client.create_link("{lt_api}", self.pk, to_pk, properties)'
            )
            body_lines.append(f"    def delete_{lt_api}(self, to_pk: str) -> None:")
            body_lines.append(
                f'        return self._client.delete_link("{lt_api}", self.pk, to_pk)'
            )
            body_lines.append(f"    def list_{lt_api}(self, to_pk: str | None = None):")
            body_lines.append(
                f'        return self._client.list_links("{lt_api}", from_pk=self.pk, to_pk=to_pk)'
            )
    path = os.path.join(out_dir, "objects.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(import_lines + body_lines) + "\n")


def _generate_links_module(out_dir: str, links_remote: dict[str, dict]) -> None:
    os.makedirs(out_dir, exist_ok=True)
    uses_datetime = any(
        str(prop_def.get("dataType")) in {"date", "timestamp"}
        for lt in links_remote.values()
        for prop_def in (lt.get("properties") or {}).values()
    )

    import_lines: list[str] = ["from __future__ import annotations", ""]
    if uses_datetime:
        import_lines.append("import datetime")
    import_lines.append("import typing")
    import_lines.append("")
    import_lines += [
        "",
        "class BaseLinkProperties:",
        '    link_type_api_name: str = ""',
        "",
        "    def __init__(self, **kwargs: typing.Any):",
        "        for k, v in kwargs.items():",
        "            setattr(self, k, v)",
        "",
        "    @classmethod",
        "    def from_dict(cls, data: dict[str, typing.Any]):",
        "        return cls(**dict(data or {}))",
        "",
    ]
    body_lines: list[str] = []
    for lt_api in sorted(links_remote.keys()):
        lt = links_remote[lt_api] or {}
        props: dict = dict(lt.get("properties") or {})
        cls_name = _to_camel(lt_api) + "LinkProperties"
        body_lines.append("")
        body_lines.append(f"class {cls_name}(BaseLinkProperties):")
        body_lines.append(f'    link_type_api_name = "{lt_api}"')
        for prop_name, prop_def in props.items():
            dt = _py_type_of(
                str(prop_def.get("dataType")), required=bool(prop_def.get("required", False))
            )
            body_lines.append(f"    {prop_name}: {dt} = None  # noqa: N815")
    path = os.path.join(out_dir, "links.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(import_lines + body_lines) + "\n")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _register_project(
    name: str,
    project_dir: Path,
    api_url: str,
    mcp_url: str,
    token: str,
    model_name: str,
    profile: str,
) -> None:
    data = _load_json(CONFIG_FILE)
    projects = data.setdefault("projects", {})
    projects[name] = {
        "path": str(project_dir),
        "api_url": api_url,
        "mcp_url": mcp_url,
        "agent_token": token,
        "model_name": model_name,
        "profile": profile,
    }
    data["current_project"] = name
    _save_json(CONFIG_FILE, data)


def _list_registered_projects() -> dict[str, dict[str, Any]]:
    data = _load_json(CONFIG_FILE)
    return data.get("projects", {})


def _find_local_state(start: Path) -> tuple[Path, dict[str, Any]] | None:
    for base in [start] + list(start.parents):
        candidate = base / LOCAL_STATE_DIR / LOCAL_STATE_FILE
        if candidate.exists():
            return base, _load_json(candidate)
    return None


def _write_local_state(project_dir: Path, data: dict[str, Any]) -> None:
    state_dir = project_dir / LOCAL_STATE_DIR
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / LOCAL_STATE_FILE
    _save_json(state_path, data)


def _load_project_state(model_override: str | None = None) -> ProjectState:
    local = _find_local_state(Path.cwd())
    if local:
        root_path, state_data = local
    else:
        config = _load_json(CONFIG_FILE)
        current = config.get("current_project")
        if not current:
            console.print(
                "[red]No Ontologia project context found. Run `ontologia genesis` first.[/red]"
            )
            raise typer.Exit(1)
        project_info = config.get("projects", {}).get(current)
        if not project_info:
            console.print(f"[red]Project '{current}' not found in registry.[/red]")
            raise typer.Exit(1)
        root_path = Path(project_info.get("path", "."))
        state_data = {
            "name": current,
            "api_url": project_info.get("api_url", DEFAULT_HOST),
            "mcp_url": project_info.get("mcp_url"),
            "agent_token": project_info.get("agent_token"),
            "model_name": project_info.get("model_name"),
        }
    if not root_path.exists():
        console.print(f"[red]Project directory '{root_path}' not found.[/red]")
        raise typer.Exit(1)
    name = state_data.get("name") or root_path.name
    api_url = state_data.get("api_url") or DEFAULT_HOST
    mcp_url = state_data.get("mcp_url") or api_url.rstrip("/") + "/mcp"
    token = state_data.get("agent_token") or state_data.get("token")
    if not token:
        console.print(
            "[red]Project state missing agent token. Re-run genesis or update state file.[/red]"
        )
        raise typer.Exit(1)
    model_name = model_override or state_data.get("model_name") or "openai:gpt-4o-mini"
    return ProjectState(
        name=name,
        root_path=root_path,
        api_url=api_url,
        mcp_url=mcp_url,
        agent_token=token,
        model_name=model_name,
    )


def _find_free_port(start: int) -> int:
    port = start
    while port < start + 1000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                port += 1
                continue
            return port
    raise RuntimeError("Unable to find a free port")


def _render_docker_compose(api_port: int, db_port: int, kuzu_port: int, profile: str) -> str:
    return (
        textwrap.dedent(
            f"""
        version: "3.9"
        services:
          api:
            image: ghcr.io/ontologiahq/ontologia-api:latest
            ports:
              - "{api_port}:8000"
            env_file:
              - .env
            depends_on:
              - postgres
              - kuzu
          postgres:
            image: postgres:15
            environment:
              POSTGRES_DB: ontologia
              POSTGRES_USER: ontologia
              POSTGRES_PASSWORD: ontologia
            ports:
              - "{db_port}:5432"
          kuzu:
            image: ghcr.io/kuzudb/kuzu:latest
            ports:
              - "{kuzu_port}:9075"
            volumes:
              - ./data/kuzu:/var/lib/kuzu
        """
        ).strip()
        + "\n"
    )


def _render_env_file(project_name: str, api_port: int, agent_token: str, profile: str) -> str:
    api_url = f"http://localhost:{api_port}"
    return (
        textwrap.dedent(
            f"""
        # Generated by ontologia genesis
        ONTOLOGIA_PROJECT={project_name}
        ONTOLOGIA_GENESIS_PROFILE={profile}
        ONTOLOGIA_API_URL={api_url}
        ONTOLOGIA_MCP_URL={api_url}/mcp
        ONTOLOGIA_AGENT_TOKEN={agent_token}
        POSTGRES_DB=ontologia
        POSTGRES_USER=ontologia
        POSTGRES_PASSWORD=ontologia
        JWT_SECRET_KEY={secrets.token_hex(32)}
        """
        ).strip()
        + "\n"
    )


def _render_gitignore() -> str:
    return (
        textwrap.dedent(
            """
        .env
        .ontologia/
        __pycache__/
        *.pyc
        data/
        dist/
        .DS_Store
        """
        ).strip()
        + "\n"
    )


def _render_readme(project_name: str) -> str:
    return (
        textwrap.dedent(
            f"""
        # {project_name}

        This project was scaffolded by `ontologia genesis`. It contains the local definitions for
        your Ontologia ecosystem. Common commands:

        ```bash
        ontologia validate --dir ontologia
        ontologia diff --dir ontologia --host http://localhost:8000 --ontology default
        ontologia agent
        ```
        """
        ).strip()
        + "\n"
    )


def _write_scaffold(
    project_dir: Path,
    *,
    project_name: str,
    api_port: int,
    db_port: int,
    kuzu_port: int,
    agent_token: str,
    model_name: str,
    profile: str,
) -> dict[str, Any]:
    (project_dir / "ontologia" / "object_types").mkdir(parents=True, exist_ok=True)
    (project_dir / "ontologia" / "link_types").mkdir(parents=True, exist_ok=True)
    (project_dir / "data" / "kuzu").mkdir(parents=True, exist_ok=True)

    compose_path = project_dir / "docker-compose.yml"
    compose_path.write_text(
        _render_docker_compose(api_port, db_port, kuzu_port, profile), encoding="utf-8"
    )
    env_path = project_dir / ".env"
    env_path.write_text(
        _render_env_file(project_name, api_port, agent_token, profile), encoding="utf-8"
    )
    gitignore_path = project_dir / ".gitignore"
    gitignore_path.write_text(_render_gitignore(), encoding="utf-8")
    readme_path = project_dir / "README.md"
    readme_path.write_text(_render_readme(project_name), encoding="utf-8")

    api_url = f"http://localhost:{api_port}"
    state = {
        "name": project_name,
        "api_url": api_url,
        "mcp_url": f"{api_url}/mcp",
        "agent_token": agent_token,
        "model_name": model_name,
        "profile": profile,
        "created_at": time.time(),
    }
    _write_local_state(project_dir, state)
    return state


def _initialize_git_repo(project_dir: Path) -> None:
    repo = Repo.init(project_dir)
    repo.git.add(A=True)
    actor = Actor("Ontologia Genesis", "genesis@ontologia.local")
    try:
        repo.index.commit("chore: initial genesis scaffold", author=actor, committer=actor)
    except Exception as exc:  # pragma: no cover - depends on user git config
        console.print(f"[yellow]Warning: initial commit failed ({exc}).[/yellow]")


def _run_docker_compose_up(project_dir: Path) -> None:
    try:
        docker_bin = shutil.which("docker")
        if docker_bin is None:
            console.print("[yellow]Docker executable not found; skipping service startup.[/yellow]")
            return
        subprocess.run(  # noqa: S603
            [docker_bin, "compose", "up", "-d"], cwd=project_dir, check=True
        )
        console.print("[green]Docker services started.[/green]")
    except FileNotFoundError:
        console.print("[yellow]Docker compose not found; skipping service startup.[/yellow]")
    except subprocess.CalledProcessError as exc:
        console.print(f"[red]Docker compose failed: {exc}[/red]")


def _wait_for_health(api_url: str, timeout: int = 120) -> bool:
    deadline = time.time() + timeout
    health_url = api_url.rstrip("/") + "/health"
    while time.time() < deadline:
        try:
            resp = httpx.get(health_url, timeout=5.0)
            if resp.status_code == 200:
                return True
        except httpx.HTTPError:
            pass
        time.sleep(2)
    return False


def _bootstrap_environment(api_url: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    bootstrap_url = api_url.rstrip("/") + "/v2/genesis/bootstrap"
    try:
        resp = httpx.post(bootstrap_url, json={}, headers=headers, timeout=15)
        if resp.status_code == 404:
            console.print("[yellow]Bootstrap endpoint not found; skipping.[/yellow]")
            return
        resp.raise_for_status()
        console.print("[green]Bootstrap completed successfully.[/green]")
    except Exception as exc:
        console.print(f"[yellow]Bootstrap step failed or was skipped: {exc}[/yellow]")


def _display_plan(plan: AgentPlan) -> None:
    console.print(f"[bold]Summary:[/bold] {plan.summary}")
    console.print(f"[bold]Branch:[/bold] {plan.branch_name}")
    console.print(f"[bold]Commit:[/bold] {plan.commit_message}")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File")
    table.add_column("Description")
    for file_change in plan.files:
        description = file_change.description or ""
        table.add_row(file_change.path, description)
    if plan.files:
        console.print(table)
    else:
        console.print("(No files to change)")


_MAX_LOG_CHARS = 4000


def _truncate_log(text: str, limit: int = _MAX_LOG_CHARS) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    truncated = text[:limit]
    return f"{truncated}\n… ({len(text) - limit} additional characters truncated)"


def _display_pipeline_result(result: dict[str, Any]) -> None:
    status = str(result.get("status"))
    return_code = result.get("returncode")
    stdout = _truncate_log(result.get("stdout", ""))
    stderr = _truncate_log(result.get("stderr", ""))

    if status == "ok":
        console.print("[green]✅ Pipeline executed successfully.[/green]")
    else:
        console.print(
            f"[red]❌ Pipeline failed (return code {return_code}). Review the logs below.[/red]"
        )

    if stdout:
        console.print(Panel(stdout, title="stdout", border_style="cyan"))
    if stderr:
        style = "red" if status != "ok" else "yellow"
        console.print(Panel(stderr, title="stderr", border_style=style))


def _build_failure_prompt(original_prompt: str, result: dict[str, Any]) -> str:
    stdout = _truncate_log(result.get("stdout", "")) or "<empty>"
    stderr = _truncate_log(result.get("stderr", "")) or "<empty>"
    returncode = result.get("returncode")
    return (
        f"{original_prompt}\n\n"
        "Previous plan was applied, but the pipeline execution failed. Use the details below to "
        "diagnose and correct the problem. Update only the necessary files.\n"
        f"Return code: {returncode}\n"
        f"STDOUT:\n{stdout}\n\n"
        f"STDERR:\n{stderr}"
    )


def validate_command(definitions_dir: str) -> int:
    objs, links = _collect_definitions(definitions_dir)
    errors = _validate_local(objs, links)
    if errors:
        console.print("[red]Validation errors:[/red]")
        for e in errors:
            console.print(f" - {e}")
        return 1
    console.print("[green]Validation OK[/green]")
    return 0


def diff_command(
    definitions_dir: str,
    host: str,
    ontology: str,
    *,
    fail_on_dangerous: bool = False,
    impact: bool = False,
    deps: bool = False,
) -> int:
    objs_local, links_local = _collect_definitions(definitions_dir)
    errors = _validate_local(objs_local, links_local)
    if errors:
        console.print("[red]Validation errors:[/red]")
        for e in errors:
            console.print(f" - {e}")
        return 1
    objs_remote, links_remote = _fetch_server_state(host, ontology)
    plan = _plan(objs_local, links_local, objs_remote, links_remote)
    if not plan:
        console.print("No changes.")
        return 0
    console.print("Migration plan:")
    for p in plan:
        tag = " [DANGEROUS]" if p.dangerous else ""
        extra = f" ({', '.join(p.reasons)})" if p.reasons else ""
        console.print(f" - [{p.action}]{tag} {p.kind}: {p.api_name}{extra}")
    if impact:
        impacted: set[str] = set()
        for p in plan:
            if p.kind == "objectType":
                impacted.add(p.api_name)
            elif p.kind == "linkType":
                src = links_local.get(p.api_name) or links_remote.get(p.api_name) or {}
                f = src.get("fromObjectType")
                t = src.get("toObjectType")
                if f:
                    impacted.add(str(f))
                if t:
                    impacted.add(str(t))
        if impacted:
            console.print("Impact (object instance counts):")
            base = host.rstrip("/") + f"/v2/ontologies/{ontology}/analytics/aggregate"
            with httpx.Client(timeout=30) as client:
                for ot in sorted(impacted):
                    try:
                        resp = client.post(
                            base,
                            json={
                                "objectTypeApiName": ot,
                                "metrics": [{"func": "count"}],
                                "groupBy": [],
                                "where": [],
                            },
                        )
                        resp.raise_for_status()
                        data = resp.json() or {}
                        rows = data.get("rows") or []
                        count_val = 0
                        if rows:
                            metrics = rows[0].get("metrics") or {}
                            count_val = metrics.get("count") or metrics.get("m_count") or 0
                        console.print(f" - {ot}: {count_val}")
                    except Exception as exc:
                        console.print(f" - {ot}: error fetching count ({exc})")
    if deps:
        changed_ots = {p.api_name for p in plan if p.kind == "objectType"}
        changed_lts = {p.api_name for p in plan if p.kind == "linkType"}
        ot_to_lts: dict[str, list[str]] = {}
        for lt_api, lt in links_remote.items():
            f = lt.get("fromObjectType")
            t = lt.get("toObjectType")
            if f:
                ot_to_lts.setdefault(str(f), []).append(lt_api)
            if t:
                ot_to_lts.setdefault(str(t), []).append(lt_api)
        printed = False
        for ot in sorted(changed_ots):
            deps_list = sorted(set(ot_to_lts.get(ot, [])))
            if not printed:
                console.print("Dependencies:")
                printed = True
            console.print(f" - objectType {ot}: linkTypes → {deps_list}")
        for lt_api in sorted(changed_lts):
            src = links_local.get(lt_api) or links_remote.get(lt_api) or {}
            f = src.get("fromObjectType")
            t = src.get("toObjectType")
            if not printed:
                console.print("Dependencies:")
                printed = True
            console.print(f" - linkType {lt_api}: endpoints → from={f}, to={t}")
    if fail_on_dangerous and any(p.dangerous for p in plan):
        console.print("Found dangerous operations. Failing as requested (--fail-on-dangerous).")
        return 2
    return 0


def apply_command(
    definitions_dir: str,
    host: str,
    ontology: str,
    *,
    allow_destructive: bool = False,
    assume_yes: bool = False,
) -> int:
    objs_local, links_local = _collect_definitions(definitions_dir)
    errors = _validate_local(objs_local, links_local)
    if errors:
        console.print("[red]Validation errors:[/red]")
        for e in errors:
            console.print(f" - {e}")
        return 1
    objs_remote, links_remote = _fetch_server_state(host, ontology)
    plan = _plan(objs_local, links_local, objs_remote, links_remote)
    if not plan:
        console.print("No changes to apply.")
        return 0
    console.print("Migration plan:")
    for p in plan:
        tag = " [DANGEROUS]" if p.dangerous else ""
        extra = f" ({', '.join(p.reasons)})" if p.reasons else ""
        console.print(f" - [{p.action}]{tag} {p.kind}: {p.api_name}{extra}")
    if (
        any(p.action == "delete" for p in plan) or any(p.dangerous for p in plan)
    ) and not allow_destructive:
        console.print(
            "Refusing to apply deletes or dangerous changes without --allow-destructive. Aborting."
        )
        return 1
    if not assume_yes:
        confirm = questionary.confirm("Apply these changes?", default=False).ask()
        if not confirm:
            console.print("Aborted.")
            return 1
    _apply(
        host,
        ontology,
        plan,
        objs_local,
        links_local,
        allow_destructive=bool(allow_destructive),
    )
    config = load_config()
    if config.sdk.auto_generate_on_apply:
        console.print("[cyan]Regenerating SDK from server definitions...[/cyan]")
        out_dir = Path(config.sdk.output_dir)
        code = generate_sdk_command(
            str(definitions_dir),
            host,
            ontology,
            str(out_dir),
            source="remote",
        )
        if code != 0:
            console.print("[red]SDK generation failed.[/red]")
            return code
    return 0


def generate_sdk_command(
    definitions_dir: str,
    host: str,
    ontology: str,
    out_dir: str,
    *,
    source: Literal["remote", "local"] = "remote",
) -> int:
    if source == "local":
        objs_local, links_local = _collect_definitions(definitions_dir)
        errors = _validate_local(objs_local, links_local)
        if errors:
            console.print("[red]Validation errors:[/red]")
            for e in errors:
                console.print(f" - {e}")
            return 1
        objs_remote, links_remote = objs_local, links_local
    else:
        objs_remote, links_remote = _fetch_server_state(host, ontology)
    _generate_objects_module(out_dir, objs_remote, links_remote)
    _generate_links_module(out_dir, links_remote)
    console.print(f"SDK generated to: {out_dir}")
    return 0


app = typer.Typer(add_completion=False, help="Ontology as Code CLI")
projects_app = typer.Typer(help="Manage local Ontologia projects.")
pipeline_app = typer.Typer(help="Orchestrate Ontologia data pipelines.")
graph_app = typer.Typer(help="Manage Kùzu graph storage.")
migrations_app = typer.Typer(help="Execute schema migration tasks.")
app.add_typer(projects_app, name="projects")
app.add_typer(pipeline_app, name="pipeline")
app.add_typer(graph_app, name="graph")
app.add_typer(migrations_app, name="migrations")


@app.command("genesis")
def genesis_command(
    name: str = typer.Argument(..., help="Name of the new Ontologia ecosystem"),
    directory: Path = typer.Option(Path.cwd(), "--directory", "-d", help="Target directory"),
    profile: str = typer.Option("light", "--profile", help="Installation profile label"),
    start_services: Annotated[
        bool,
        typer.Option(
            "--start-services",
            help="Start Docker services after scaffolding",
            is_flag=True,
        ),
    ] = False,  # noqa: FBT002
    bootstrap: Annotated[
        bool,
        typer.Option(
            "--bootstrap",
            help="Attempt to bootstrap the ontology once the API is healthy",
            is_flag=True,
        ),
    ] = False,  # noqa: FBT002
    model: str = typer.Option(
        "openai:gpt-4o-mini", "--model", help="Default LLM model for the agent"
    ),
) -> None:
    project_dir = (directory / name).resolve()
    if project_dir.exists():
        console.print(f"[red]Directory '{project_dir}' already exists.[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]✨ Creating Ontologia ecosystem '{name}'[/bold]")
    project_dir.mkdir(parents=True, exist_ok=True)

    api_port = _find_free_port(8000)
    db_port = _find_free_port(5432)
    kuzu_port = _find_free_port(9075)
    agent_token = secrets.token_hex(32)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Scaffolding project structure...", total=None)
        state = _write_scaffold(
            project_dir,
            project_name=name,
            api_port=api_port,
            db_port=db_port,
            kuzu_port=kuzu_port,
            agent_token=agent_token,
            model_name=model,
            profile=profile,
        )
        progress.update(task, description="Initializing git repository...")
        _initialize_git_repo(project_dir)
        progress.update(task, description="Registering project context...")
        _register_project(
            name, project_dir, state["api_url"], state["mcp_url"], agent_token, model, profile
        )
        progress.update(task, description="Finalizing...")
        progress.stop_task(task)

    console.print(f"[green]✅ Ecosystem '{name}' created at {project_dir}[/green]")
    console.print(f"   API URL: [cyan]{state['api_url']}[/cyan]")

    if start_services:
        _run_docker_compose_up(project_dir)
        if bootstrap:
            console.print("[cyan]Waiting for API health...[/cyan]")
            if _wait_for_health(state["api_url"]):
                _bootstrap_environment(state["api_url"], agent_token)
            else:
                console.print(
                    "[yellow]API did not become healthy within the timeout window.[/yellow]"
                )
    else:
        console.print(
            "[yellow]Services not started. Run `docker compose up -d` inside the project directory when ready.[/yellow]"
        )

    console.print("\nNext steps:")
    console.print(f"  1. cd {project_dir}")
    console.print("  2. ontologia agent\n")


@app.command("agent")
def agent_command(
    model: str | None = typer.Option(
        None, "--model", help="Override the LLM model for this session"
    ),
    auto_apply: Annotated[
        bool,
        typer.Option(
            "--auto-apply",
            help="Apply plans automatically without confirmation",
            is_flag=True,
        ),
    ] = False,  # noqa: FBT002
    author_name: str | None = typer.Option(None, "--author-name", help="Git author name override"),
    author_email: str | None = typer.Option(
        None, "--author-email", help="Git author email override"
    ),
) -> None:
    try:
        state = _load_project_state(model_override=model)
    except typer.Exit as exc:
        raise exc
    except Exception as exc:  # pragma: no cover - defensive
        console.print(f"[red]Failed to load project state:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"[green]Connected to project '{state.name}'[/green]")
    console.print(f"API: [cyan]{state.api_url}[/cyan]")

    try:
        agent = ArchitectAgent(state)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    except Exception as exc:  # pragma: no cover - defensive
        console.print(f"[red]Failed to initialize agent:[/red] {exc}")
        raise typer.Exit(1) from exc

    while True:
        try:
            user_prompt = questionary.text("👤 > ").ask()
        except KeyboardInterrupt:
            console.print("\n[yellow]Session cancelled by user.[/yellow]")
            raise typer.Exit() from None
        if user_prompt is None:
            console.print()
            break
        prompt = user_prompt.strip()
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            break

        base_prompt = prompt
        current_prompt = base_prompt

        while True:
            console.print("[cyan]🤖 Agent thinking…[/cyan]")
            try:
                plan = asyncio.run(agent.create_plan(current_prompt))
            except Exception as exc:
                console.print(f"[red]Agent failed to produce a plan:[/red] {exc}")
                break

            _display_plan(plan)
            if plan.is_empty():
                console.print("[green]The agent determined no changes are required.[/green]")
                break

            if auto_apply:
                apply_change = True
            else:
                answer = questionary.confirm("Apply this plan?", default=True).ask()
                apply_change = bool(answer)
            if not apply_change:
                console.print("[yellow]Plan discarded.[/yellow]")
                break

            try:
                written = agent.apply_plan(
                    plan,
                    author_name=author_name,
                    author_email=author_email,
                )
            except Exception as exc:
                console.print(f"[red]Failed to apply plan:[/red] {exc}")
                break

            if written:
                console.print(
                    f"[green]✅ Applied {len(written)} file(s) on branch '{plan.branch_name}'.[/green]"
                )
                for path in written:
                    rel = path.relative_to(state.root_path)
                    console.print(f"  • {rel}")
            else:
                console.print("[yellow]No files were written; nothing to commit.[/yellow]")

            try:
                pipeline_result = asyncio.run(agent.run_pipeline())
            except Exception as exc:
                pipeline_result = {
                    "status": "error",
                    "returncode": None,
                    "stdout": "",
                    "stderr": str(exc),
                }

            _display_pipeline_result(pipeline_result)
            if str(pipeline_result.get("status")) == "ok":
                break

            retry = questionary.confirm(
                "Pipeline failed. Ask the agent to generate a corrective plan?", default=True
            ).ask()
            if not retry:
                console.print("[yellow]Stopping after pipeline failure.[/yellow]")
                break

            current_prompt = _build_failure_prompt(base_prompt, pipeline_result)
            console.print("[cyan]🔁 Retrying with failure context…[/cyan]")
        # inner loop end -> prompt user again
    console.print("[cyan]Session ended.[/cyan]")


@app.command("dev")
def dev_cli(
    no_docker: Annotated[
        bool,
        typer.Option("--no-docker", help="Skip starting Docker services", is_flag=True),
    ] = False,  # noqa: FBT002
    no_reload: Annotated[
        bool,
        typer.Option("--no-reload", help="Disable Uvicorn auto-reload", is_flag=True),
    ] = False,  # noqa: FBT002
) -> None:
    """Start a local Ontologia development workspace."""

    config = load_config()
    console.print("[bold green]🚀 Starting Ontologia workspace[/bold green]")

    if not no_docker:
        console.print("[cyan]Bringing up Docker services...[/cyan]")
        docker_binary = shutil.which("docker")
        if docker_binary is None:
            console.print("[red]Docker executable not found in PATH.[/red]")
            raise typer.Exit(1)
        subprocess.run([docker_binary, "compose", "up", "-d"], check=True)  # noqa: S603

    console.print(f"[cyan]Starting API server at http://{config.api.host}:{config.api.port}[/cyan]")
    uvicorn_args = [
        "uvicorn",
        "api.main:app",
        "--host",
        config.api.host,
        "--port",
        str(config.api.port),
    ]
    if not no_reload:
        uvicorn_args.append("--reload")

    env = os.environ.copy()
    env.setdefault("ONTOLOGIA_CONFIG_ROOT", str(Path.cwd()))

    uvicorn_binary = shutil.which("uvicorn")
    if uvicorn_binary is None:
        console.print("[red]uvicorn executable not found in PATH.[/red]")
        raise typer.Exit(1)
    subprocess.run([uvicorn_binary, *uvicorn_args[1:]], env=env, check=True)  # noqa: S603


@pipeline_app.command("run")
def pipeline_run(
    skip_dbt: Annotated[
        bool,
        typer.Option("--skip-dbt", help="Skip dbt dependency install and build", is_flag=True),
    ] = False,  # noqa: FBT002
    skip_sync: Annotated[
        bool,
        typer.Option("--skip-sync", help="Skip ontology sync stage", is_flag=True),
    ] = False,  # noqa: FBT002
) -> None:
    """Execute the full Ontologia data pipeline (DuckDB prep, dbt, sync)."""

    config = load_config()
    uv_binary = shutil.which("uv")
    if uv_binary is None:
        console.print("[red]uv executable not found in PATH.[/red]")
        raise typer.Exit(1)

    env = os.environ.copy()
    env.setdefault("ONTOLOGIA_CONFIG_ROOT", str(Path.cwd()))
    duckdb_path = os.path.abspath(env.get("DUCKDB_PATH", config.data.duckdb_path))
    env["DUCKDB_PATH"] = duckdb_path

    console.print(f"[cyan]Preparing DuckDB raw tables at {duckdb_path}[/cyan]")
    subprocess.run(  # noqa: S603
        [uv_binary, "run", "python", "scripts/prepare_duckdb_raw.py"],
        env=env,
        check=True,
    )

    if not skip_dbt:
        dbt_dir = Path("example_project/dbt_project")
        if not dbt_dir.exists():
            console.print(f"[red]dbt project not found at {dbt_dir}.[/red]")
            raise typer.Exit(1)
        dbt_env = env.copy()
        dbt_env["DBT_PROFILES_DIR"] = str(dbt_dir.resolve())
        console.print("[cyan]Running dbt deps...[/cyan]")
        subprocess.run(  # noqa: S603
            [uv_binary, "run", "dbt", "deps"],
            env=dbt_env,
            cwd=dbt_dir,
            check=True,
        )
        console.print("[cyan]Running dbt build...[/cyan]")
        subprocess.run(  # noqa: S603
            [uv_binary, "run", "dbt", "build"],
            env=dbt_env,
            cwd=dbt_dir,
            check=True,
        )
    else:
        console.print("[yellow]Skipping dbt stage (--skip-dbt).[/yellow]")

    if not skip_sync:
        console.print("[cyan]Syncing ontology to Kùzu...[/cyan]")
        subprocess.run(  # noqa: S603
            [uv_binary, "run", "python", "scripts/main_sync.py"],
            env=env,
            check=True,
        )
    else:
        console.print("[yellow]Skipping sync stage (--skip-sync).[/yellow]")

    console.print("[bold green]✅ Pipeline completed successfully.[/bold green]")


@migrations_app.command("run")
def migrations_run(
    task_rid: Annotated[str, typer.Argument(help="RID of the migration task")],
    *,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Validate only", is_flag=True),
    ] = False,
    batch_size: Annotated[
        int | None,
        typer.Option("--batch-size", help="Instances processed per batch", min=1),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="API base URL", show_default=False),
    ] = DEFAULT_HOST,
    ontology: Annotated[
        str,
        typer.Option("--ontology", help="Ontology instance name", show_default=False),
    ] = DEFAULT_ONTOLOGY,
) -> None:
    """Execute a specific migration task via the API."""

    url = host.rstrip("/") + f"/v2/ontologies/{ontology}/migrations/tasks/{task_rid}/run"
    payload: dict[str, Any] = {"dryRun": dry_run}
    if batch_size is not None:
        payload["batchSize"] = batch_size
    try:
        resp = httpx.post(url, json=payload, timeout=60)
        resp.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - network failure handled at runtime
        console.print(f"[red]Request failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    data = resp.json()
    failed = int(data.get("failedCount", 0))
    updated = int(data.get("updatedCount", 0))
    status = str(data.get("taskStatus", ""))

    if failed:
        console.print(
            f"[red]Migration task {task_rid} finished with {failed} failures (status={status}).[/red]"
        )
        errors = data.get("errors") or []
        if errors:
            console.print(f"[red]- {errors[0]}[/red]")
        raise typer.Exit(1)

    verb = "validated" if dry_run else "applied"
    console.print(
        f"[green]Migration task {task_rid} {verb} successfully (updated {updated} instance(s)).[/green]"
    )


@migrations_app.command("run-pending")
def migrations_run_pending(
    *,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Validate without applying", is_flag=True),
    ] = False,
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Maximum number of tasks to process", min=1),
    ] = None,
    batch_size: Annotated[
        int | None,
        typer.Option("--batch-size", help="Instances processed per batch", min=1),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="API base URL", show_default=False),
    ] = DEFAULT_HOST,
    ontology: Annotated[
        str,
        typer.Option("--ontology", help="Ontology instance name", show_default=False),
    ] = DEFAULT_ONTOLOGY,
) -> None:
    """Execute all pending migration tasks for an ontology."""

    url = host.rstrip("/") + f"/v2/ontologies/{ontology}/migrations/tasks/run-pending"
    payload: dict[str, Any] = {"dryRun": dry_run}
    if limit is not None:
        payload["limit"] = limit
    if batch_size is not None:
        payload["batchSize"] = batch_size

    try:
        resp = httpx.post(url, json=payload, timeout=120)
        resp.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - network failure handled at runtime
        console.print(f"[red]Request failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    data = resp.json() or {}
    results = data.get("results") or []
    if not results:
        console.print("[yellow]No pending migration tasks found.[/yellow]")
        return

    failures = [r for r in results if int(r.get("failedCount", 0))]
    console.print(f"[cyan]Processed {len(results)} migration task(s).[/cyan]")
    if failures:
        first = failures[0]
        console.print(
            f"[red]{len(failures)} task(s) reported failures; first: {first.get('taskRid')}[/red]"
        )
        raise typer.Exit(1)

    verb = "validated" if dry_run else "applied"
    console.print(f"[green]All tasks {verb} successfully.[/green]")


@graph_app.command("reset")
def graph_reset(
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Confirm graph storage cleanup", is_flag=True)
    ] = False,  # noqa: FBT002
) -> None:
    """Delete the current Kùzu graph storage so it can be rebuilt fresh."""

    config = load_config(Path.cwd())
    kuzu_path = Path(config.data.kuzu_path).expanduser()
    if not kuzu_path.is_absolute():
        kuzu_path = (Path.cwd() / kuzu_path).resolve()
    else:
        kuzu_path = kuzu_path.resolve()

    if not kuzu_path.exists():
        console.print(f"[yellow]Graph storage not found at {kuzu_path}; nothing to reset.[/yellow]")
        return

    if kuzu_path == Path("/"):
        console.print(
            "[red]Refusing to remove '/'. Update ontologia.toml to point to a directory first.[/red]"
        )
        raise typer.Exit(1)

    if not yes:
        proceed = typer.confirm(
            f"This will delete all data under '{kuzu_path}'. Continue?",
            default=False,
        )
        if not proceed:
            raise typer.Abort()

    if kuzu_path.is_dir():
        shutil.rmtree(kuzu_path)
    else:
        kuzu_path.unlink()

    console.print(
        "[green]Kùzu graph storage removed. Run 'ontologia pipeline run' to rebuild the unified graph.[/green]"
    )


def test_contract_command(definitions_dir: str, duckdb_path: str | None = None) -> int:
    """Validate that physical DuckDB tables match ontology object definitions."""

    try:
        import duckdb
    except ImportError:  # pragma: no cover - optional dependency
        console.print("[red]DuckDB is not installed. Install with `uv add duckdb`.[/red]")
        return 1

    from sqlmodel import Session, select

    from api.core.database import engine
    from ontologia.domain.metamodels.types.object_type import ObjectType

    config = load_config()
    objs_local, _ = _collect_definitions(definitions_dir)
    if not objs_local:
        console.print("[yellow]No object type definitions found; nothing to validate.[/yellow]")
        return 0

    resolved_duckdb = os.path.abspath(
        duckdb_path or os.getenv("DUCKDB_PATH") or config.data.duckdb_path
    )
    if not Path(resolved_duckdb).exists():
        console.print(f"[red]DuckDB database not found at {resolved_duckdb}.[/red]")
        return 1

    def _quote_identifier(identifier: str) -> str:
        parts = [part for part in identifier.split(".") if part]
        return ".".join('"' + part.replace('"', '""') + '"' for part in parts)

    def _duckdb_columns(conn: duckdb.DuckDBPyConnection, table: str) -> dict[str, str]:
        qualified = _quote_identifier(table)
        rows = conn.execute(f"DESCRIBE SELECT * FROM {qualified}").fetchall()  # noqa: S608
        return {row[0]: row[1] for row in rows}

    def _normalize_duckdb_type(raw: str) -> str:
        upper = raw.upper().strip()
        if "(" in upper:
            upper = upper.split("(", 1)[0]
        return upper

    type_compatibility: dict[str, set[str]] = {
        "string": {"VARCHAR", "TEXT", "STRING"},
        "integer": {"INTEGER", "INT", "BIGINT", "SMALLINT", "TINYINT"},
        "double": {"DOUBLE", "FLOAT", "REAL", "DECIMAL", "NUMERIC"},
        "number": {"DOUBLE", "FLOAT", "REAL", "DECIMAL", "NUMERIC"},
        "boolean": {"BOOLEAN", "BOOL"},
        "date": {"DATE"},
        "timestamp": {"TIMESTAMP", "DATETIME"},
    }

    def _is_type_compatible(expected: str | None, actual: str) -> bool:
        if expected is None:
            return True
        normalized_expected = expected.lower()
        if normalized_expected in {"struct", "array"}:
            return True
        normalized_actual = _normalize_duckdb_type(actual)
        compatible = type_compatibility.get(normalized_expected)
        if compatible is None:
            return True
        return normalized_actual in compatible

    results: list[tuple[str, str, str | None, str]] = []
    error_count = 0

    with Session(engine) as session:
        object_types = session.exec(
            select(ObjectType).where(
                ObjectType.service == "ontology",
                ObjectType.instance == config.api.ontology,
                ObjectType.is_latest == true(),
            )
        ).all()

        if not object_types:
            console.print(
                "[yellow]No object types registered in the metamodel; nothing to validate.[/yellow]"
            )
            return 0

        conn = duckdb.connect(database=resolved_duckdb, read_only=True)
        try:
            for ot in object_types:
                schema = objs_local.get(ot.api_name)
                if schema is None:
                    results.append(
                        ("error", ot.api_name, None, "Object type not found in local definitions")
                    )
                    error_count += 1
                    continue

                properties = schema.get("properties") or {}
                data_sources = list(getattr(ot, "data_sources", []) or [])
                if not data_sources:
                    results.append(("warning", ot.api_name, None, "No data sources configured"))
                    continue

                for data_source in data_sources:
                    dataset = getattr(data_source, "dataset", None)
                    if dataset is None and getattr(data_source, "dataset_branch", None) is not None:
                        dataset = data_source.dataset_branch.dataset

                    if dataset is None:
                        results.append(("error", ot.api_name, None, "Data source missing dataset"))
                        error_count += 1
                        continue

                    if dataset.source_type != "duckdb_table":
                        results.append(
                            (
                                "warning",
                                ot.api_name,
                                dataset.source_identifier,
                                f"Unsupported source type '{dataset.source_type}'; skipping",
                            )
                        )
                        continue

                    try:
                        columns = _duckdb_columns(conn, dataset.source_identifier)
                    except duckdb.Error as exc:  # pragma: no cover - depends on DuckDB state
                        results.append(
                            (
                                "error",
                                ot.api_name,
                                dataset.source_identifier,
                                f"Failed to inspect table: {exc}",
                            )
                        )
                        error_count += 1
                        continue

                    inverse_mapping = {
                        str(prop_name): str(column_name)
                        for column_name, prop_name in (data_source.property_mappings or {}).items()
                    }

                    dataset_failed = False
                    for prop_name, prop_def in properties.items():
                        dataset_column = inverse_mapping.get(prop_name, prop_name)
                        if dataset_column not in columns:
                            results.append(
                                (
                                    "error",
                                    ot.api_name,
                                    dataset.source_identifier,
                                    f"Missing column '{dataset_column}' for property '{prop_name}'",
                                )
                            )
                            error_count += 1
                            dataset_failed = True
                            continue

                        expected_type = (
                            prop_def.get("dataType") if isinstance(prop_def, dict) else None
                        )
                        if isinstance(expected_type, str) and not _is_type_compatible(
                            expected_type, columns[dataset_column]
                        ):
                            results.append(
                                (
                                    "error",
                                    ot.api_name,
                                    dataset.source_identifier,
                                    (
                                        f"Type mismatch for '{prop_name}': expected {expected_type}, "
                                        f"found {columns[dataset_column]}"
                                    ),
                                )
                            )
                            error_count += 1
                            dataset_failed = True

                    if not dataset_failed:
                        results.append(
                            (
                                "ok",
                                ot.api_name,
                                dataset.source_identifier,
                                "Schema matches object definition",
                            )
                        )
        finally:
            conn.close()

    if not results:
        console.print("[yellow]No datasets available for validation.[/yellow]")
        return 0

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status")
    table.add_column("ObjectType")
    table.add_column("Dataset/Table")
    table.add_column("Details", overflow="fold")

    style_map = {"ok": "green", "warning": "yellow", "error": "red"}
    for status, ot_name, dataset_id, message in results:
        style = style_map.get(status, "white")
        dataset_label = dataset_id or "-"
        table.add_row(f"[{style}]{status.upper()}[/]", ot_name, dataset_label, message)

    console.print(table)

    if error_count > 0:
        console.print(f"[red]Contract tests failed with {error_count} error(s).[/red]")
        return 1

    console.print("[bold green]✅ Contract tests passed.[/bold green]")
    return 0


@app.command("test-contract")
def test_contract_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
    duckdb_path: Path | None = typer.Option(
        None, "--duckdb-path", help="Override DuckDB database path"
    ),
) -> None:
    code = test_contract_command(
        str(definitions_dir), duckdb_path=str(duckdb_path) if duckdb_path else None
    )
    if code != 0:
        raise typer.Exit(code)


@app.command("validate")
def validate_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
) -> None:
    code = validate_command(str(definitions_dir))
    if code != 0:
        raise typer.Exit(code)


@app.command("diff")
def diff_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
    host: str = typer.Option(DEFAULT_HOST, "--host", help="API host"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", help="Ontology API name"),
    fail_on_dangerous: Annotated[
        bool,
        typer.Option(
            "--fail-on-dangerous",
            help="Exit non-zero if dangerous operations are present",
            is_flag=True,
        ),
    ] = False,  # noqa: FBT002
    impact: Annotated[
        bool,
        typer.Option(
            "--impact", help="Show instance counts for affected object types", is_flag=True
        ),
    ] = False,  # noqa: FBT002
    deps: Annotated[
        bool,
        typer.Option("--deps", help="Show dependency summary for changed types", is_flag=True),
    ] = False,  # noqa: FBT002
) -> None:
    code = diff_command(
        str(definitions_dir),
        host,
        ontology,
        fail_on_dangerous=fail_on_dangerous,
        impact=impact,
        deps=deps,
    )
    if code != 0:
        raise typer.Exit(code)


@app.command("apply")
def apply_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
    host: str = typer.Option(DEFAULT_HOST, "--host", help="API host"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", help="Ontology API name"),
    allow_destructive: Annotated[
        bool,
        typer.Option(
            "--allow-destructive", help="Allow destructive operations (deletes)", is_flag=True
        ),
    ] = False,  # noqa: FBT002
    yes: Annotated[
        bool, typer.Option("--yes", help="Apply without confirmation", is_flag=True)
    ] = False,  # noqa: FBT002
) -> None:
    code = apply_command(
        str(definitions_dir),
        host,
        ontology,
        allow_destructive=allow_destructive,
        assume_yes=yes,
    )
    if code != 0:
        raise typer.Exit(code)


@app.command("generate-sdk")
def generate_sdk_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
    host: str = typer.Option(DEFAULT_HOST, "--host", help="API host"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", help="Ontology API name"),
    source: Literal["remote", "local"] = typer.Option(
        "remote", "--source", help="Use 'remote' (API) or 'local' definitions"
    ),
    out: Path = typer.Option(
        Path(DEFAULT_SDK_DIR), "--out", help="Output directory for generated modules"
    ),
) -> None:
    code = generate_sdk_command(str(definitions_dir), host, ontology, str(out), source=source)
    if code != 0:
        raise typer.Exit(code)


@projects_app.command("list")
def projects_list() -> None:
    projects = _list_registered_projects()
    if not projects:
        console.print("[yellow]No registered projects found.[/yellow]")
        return
    data = _load_json(CONFIG_FILE)
    current = data.get("current_project")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Project")
    table.add_column("Path")
    table.add_column("API URL")
    for name, info in projects.items():
        label = f"{name} (current)" if name == current else name
        table.add_row(label, info.get("path", "?"), info.get("api_url", "?"))
    console.print(table)


@projects_app.command("switch")
def projects_switch(name: str) -> None:
    data = _load_json(CONFIG_FILE)
    projects = data.get("projects", {})
    if name not in projects:
        console.print(f"[red]Project '{name}' not found in registry.[/red]")
        raise typer.Exit(1)
    data["current_project"] = name
    _save_json(CONFIG_FILE, data)
    console.print(f"[green]Current project set to '{name}'.[/green]")


def main(argv: list[str] | None = None) -> int:
    """Entry point used both by tests and console scripts."""

    if argv is None:
        app()
        return 0
    runner = CliRunner()
    result = runner.invoke(app, argv)
    if result.exception:
        raise result.exception
    return result.exit_code


def run() -> None:
    app()


if __name__ == "__main__":
    run()
