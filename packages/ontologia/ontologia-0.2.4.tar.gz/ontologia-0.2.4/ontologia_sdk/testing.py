from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ontologia_sdk.actions import ActionsNamespace


class MockOntologyClient:
    """
    In-memory mock of OntologyClient for unit tests.

    Stores objects and links in dicts. Intended only for local testing.
    """

    def __init__(self, *, ontology: str = "default") -> None:
        self.ontology = ontology
        # objects[object_type][pk] = {"rid": ..., "pkValue": pk, "properties": {...}}
        self.objects: dict[str, dict[str, dict[str, Any]]] = {}
        # links[link_type][(from_pk, to_pk)] = {"properties": {...}}
        self.links: dict[str, dict[tuple[str, str], dict[str, Any]]] = {}
        # actions[object_type][action_api_name] = metadata + handler
        self._actions: dict[str, dict[str, dict[str, Any]]] = {}
        self.actions = ActionsNamespace(self, enable_validation=True, cache_ttl=0.0)

    # --- Objects ---
    def upsert_object(
        self, object_type: str, pk: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        ot = self.objects.setdefault(object_type, {})
        rid = f"mock:{object_type}:{pk}"
        rec = {"rid": rid, "pkValue": pk, "properties": dict(properties or {})}
        ot[pk] = rec
        return rec

    def get_object(self, object_type: str, pk: str) -> dict[str, Any]:
        rec = self.objects.get(object_type, {}).get(pk)
        if not rec:
            raise KeyError(f"object not found: {object_type} {pk}")
        return rec

    def delete_object(self, object_type: str, pk: str) -> None:
        ot = self.objects.get(object_type)
        if ot and pk in ot:
            del ot[pk]

    def search_objects(
        self,
        object_type: str,
        *,
        where: list[dict[str, Any]] | None = None,
        order_by: list[dict[str, Any]] | None = None,
        limit: int = 100,
        offset: int = 0,
        traverse: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        items = list(self.objects.get(object_type, {}).values())
        # naive filtering: property equals
        for cond in list(where or []):
            prop = cond.get("property")
            op = cond.get("op")
            val = cond.get("value")
            if op == "eq":
                items = [x for x in items if x.get("properties", {}).get(prop) == val]
        # ignore order_by for simplicity
        start = max(0, int(offset))
        end = start + max(0, int(limit)) if int(limit) > 0 else len(items)
        return {"data": items[start:end], "nextPageToken": None}

    # --- Actions ---
    def register_action(
        self,
        object_type: str,
        action_api_name: str,
        *,
        parameters: list[dict[str, Any]] | None = None,
        handler: Callable[[str, dict[str, Any]], Any] | None = None,
    ) -> None:
        actions = self._actions.setdefault(object_type, {})
        actions[action_api_name] = {
            "apiName": action_api_name,
            "parameters": list(parameters or []),
            "handler": handler,
        }

    def list_actions(self, object_type: str, pk: str) -> dict[str, Any]:
        actions = [
            {k: v for k, v in details.items() if k != "handler"}
            for details in self._actions.get(object_type, {}).values()
        ]
        return {"data": actions}

    def execute_action(
        self,
        object_type: str,
        pk: str,
        action_api_name: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        action = self._actions.get(object_type, {}).get(action_api_name)
        if not action:
            raise KeyError(f"Unknown action: {action_api_name}")
        handler = action.get("handler")
        params = dict(parameters or {})
        if handler:
            result = handler(pk, params)
            return result if isinstance(result, dict) else {"result": result}
        return {
            "objectType": object_type,
            "pk": pk,
            "action": action_api_name,
            "parameters": params,
        }

    # --- Links ---
    def create_link(
        self, link_type: str, from_pk: str, to_pk: str, properties: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        m = self.links.setdefault(link_type, {})
        key = (from_pk, to_pk)
        m[key] = dict(properties or {})
        return {
            "rid": f"mock:{link_type}:{from_pk}->{to_pk}",
            "linkTypeApiName": link_type,
            "fromObjectType": "",
            "toObjectType": "",
            "fromPk": from_pk,
            "toPk": to_pk,
            "linkProperties": dict(properties or {}),
        }

    def traverse(
        self,
        from_object_type: str,
        from_pk: str,
        link_type: str,
        *,
        limit: int = 100,
        offset: int = 0,
        valid_at: str | None = None,
    ) -> dict[str, Any]:
        listing = self.list_links(link_type, from_pk=from_pk, valid_at=valid_at)
        items = listing.get("data", [])
        start = max(0, int(offset))
        end = start + max(0, int(limit)) if int(limit) > 0 else len(items)
        return {"data": items[start:end], "nextPageToken": None}

    def get_link(
        self,
        link_type: str,
        from_pk: str,
        to_pk: str,
        *,
        valid_at: str | None = None,
    ) -> dict[str, Any]:
        props = self.links.get(link_type, {}).get((from_pk, to_pk))
        if props is None:
            raise KeyError("link not found")
        return {
            "rid": f"mock:{link_type}:{from_pk}->{to_pk}",
            "linkTypeApiName": link_type,
            "fromObjectType": "",
            "toObjectType": "",
            "fromPk": from_pk,
            "toPk": to_pk,
            "linkProperties": dict(props or {}),
        }

    def list_links(
        self,
        link_type: str,
        *,
        from_pk: str | None = None,
        to_pk: str | None = None,
        valid_at: str | None = None,
    ) -> dict[str, Any]:
        data: list[dict[str, Any]] = []
        for (fp, tp), props in self.links.get(link_type, {}).items():
            if from_pk is not None and fp != from_pk:
                continue
            if to_pk is not None and tp != to_pk:
                continue
            data.append(
                {
                    "rid": f"mock:{link_type}:{fp}->{tp}",
                    "linkTypeApiName": link_type,
                    "fromObjectType": "",
                    "toObjectType": "",
                    "fromPk": fp,
                    "toPk": tp,
                    "linkProperties": dict(props or {}),
                }
            )
        return {"data": data, "nextPageToken": None}

    def delete_link(self, link_type: str, from_pk: str, to_pk: str) -> None:
        m = self.links.get(link_type)
        if m and (from_pk, to_pk) in m:
            del m[(from_pk, to_pk)]
