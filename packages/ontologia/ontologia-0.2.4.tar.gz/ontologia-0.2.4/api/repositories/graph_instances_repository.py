"""
repositories/graph_instances_repository.py
-------------------------------------------
Graph-backed repository for reading object instances from KùzuDB.

This repository provides read methods that query the materialized graph.
Writes remain in SQLModel-backed repositories until the migration is complete.
"""

from __future__ import annotations

import json
from typing import Any

from registro.core.resource import Resource
from sqlmodel import Session, select

from api.repositories.instances_repository import InstancesRepository
from api.repositories.kuzudb_repository import KuzuDBRepository
from api.repositories.linked_objects_repository import LinkedObjectsRepository
from api.repositories.metamodel_repository import MetamodelRepository
from ontologia.domain.metamodels.instances.models_sql import ObjectInstance
from ontologia.domain.metamodels.types.link_type import LinkType


class GraphInstancesRepository:
    """
    Read-only repository for object instances stored in KùzuDB.
    """

    def __init__(self, kuzu_repo: KuzuDBRepository | None = None, session: Session | None = None):
        self.kuzu = kuzu_repo or KuzuDBRepository()
        # Optional SQL fallback context (used during tests or when Kùzu is not available)
        self.session = session
        self._inst_repo = InstancesRepository(session) if session is not None else None
        self._link_repo = LinkedObjectsRepository(session) if session is not None else None
        self._meta_repo = MetamodelRepository(session) if session is not None else None

    def is_available(self) -> bool:
        return self.kuzu is not None and self.kuzu.is_available()

    def get_by_pk(
        self,
        object_type_api_name: str,
        pk_field: str,
        pk_value: str,
    ) -> dict[str, Any] | None:
        """
        Returns a dictionary with keys: objectTypeApiName, pkValue, properties.
        """
        if not self.is_available():
            # SQLModel fallback
            if self._inst_repo is None:
                return None
            inst: ObjectInstance | None = self._inst_repo.get_object_instance(
                "ontology", "default", object_type_api_name, pk_value
            )
            if not inst:
                return None
            return {
                "objectTypeApiName": object_type_api_name,
                "pkValue": str(pk_value),
                "properties": dict(inst.data or {}),
            }
        query = (
            "MATCH (o:Object) "
            f"WHERE o.objectTypeApiName = '{object_type_api_name}' AND o.pkValue = '{pk_value}' "
            "RETURN o.pkValue AS pkValue, o.properties AS properties"
        )
        try:
            res = self.kuzu.execute(query)
            df = res.get_as_df()  # type: ignore[attr-defined]
        except Exception:
            return None

        if df is None or len(df) == 0:
            return None

        row = df.iloc[0]
        props_raw = row.get("properties") if hasattr(row, "get") else row["properties"]
        props: dict[str, Any]
        if isinstance(props_raw, str):
            try:
                props = json.loads(props_raw)
            except Exception:
                props = {}
        else:
            props = dict(props_raw or {}) if isinstance(props_raw, dict) else {}
        return {
            "objectTypeApiName": object_type_api_name,
            "pkValue": str(pk_value),
            "properties": props,
        }

    def list_by_type(
        self,
        object_type_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Returns a list of dictionaries with keys: objectTypeApiName, pkValue, properties.
        """
        if not self.is_available():
            # SQLModel fallback
            if self._inst_repo is None:
                return []
            items: list[dict[str, Any]] = []
            objs = self._inst_repo.list_object_instances(
                "ontology",
                "default",
                object_type_api_name=object_type_api_name,
                limit=limit,
                offset=offset,
            )
            for it in objs:
                items.append(
                    {
                        "objectTypeApiName": object_type_api_name,
                        "pkValue": it.pk_value,
                        "properties": dict(it.data or {}),
                    }
                )
            return items
        query = (
            "MATCH (o:Object) "
            f"WHERE o.objectTypeApiName = '{object_type_api_name}' "
            f"RETURN o.pkValue AS pkValue, o.properties AS properties LIMIT {int(limit)}"
        )
        items: list[dict[str, Any]] = []
        try:
            res = self.kuzu.execute(query)
            df = res.get_as_df()  # type: ignore[attr-defined]
        except Exception:
            return []

        if df is None or len(df) == 0:
            return []

        start = int(offset) if int(offset) > 0 else 0
        end = start + int(limit) if int(limit) > 0 else len(df)
        rng = range(start, min(end, len(df)))
        for idx in rng:
            row = df.iloc[idx]
            props_raw = row.get("properties") if hasattr(row, "get") else row["properties"]
            try:
                props = (
                    json.loads(props_raw) if isinstance(props_raw, str) else dict(props_raw or {})
                )
            except Exception:
                props = {}
            items.append(
                {
                    "objectTypeApiName": object_type_api_name,
                    "pkValue": str(row.get("pkValue") if hasattr(row, "get") else row["pkValue"]),
                    "properties": props,
                }
            )
        return items

    def list_by_interface(
        self,
        interface_api_name: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Returns a list of dicts with keys: objectTypeApiName, pkValue, properties for all implementers
        of an Interface, using the unified Object node model when enabled.
        Fallback to per-implementer union via SQL/graph per-type when unified is disabled.
        """
        if not self.is_available():
            # SQL fallback via implementers
            items: list[dict[str, Any]] = []
            if not self._meta_repo:
                return items
            itf = self._meta_repo.get_interface_type_by_api_name(
                "ontology", "default", interface_api_name
            )
            if not itf or not getattr(itf, "object_types", None):
                return []
            fetch = int(limit) + int(offset) if int(offset) > 0 else int(limit)
            for impl in itf.object_types:
                rows = self.list_by_type(impl.api_name, limit=fetch, offset=0)
                items.extend(rows)
            start = int(offset) if int(offset) > 0 else 0
            end = start + int(limit) if int(limit) > 0 else len(items)
            return items[start:end]

        query = (
            "MATCH (o:Object) "
            f"WHERE '{interface_api_name}' IN o.labels "
            f"RETURN o.objectTypeApiName AS objectTypeApiName, o.pkValue AS pkValue, o.properties AS properties LIMIT {int(limit)}"
        )
        items: list[dict[str, Any]] = []
        try:
            res = self.kuzu.execute(query)
            df = res.get_as_df()  # type: ignore[attr-defined]
        except Exception:
            return []

        if df is None or len(df) == 0:
            return []

        start = int(offset) if int(offset) > 0 else 0
        end = start + int(limit) if int(limit) > 0 else len(df)
        rng = range(start, min(end, len(df)))
        for idx in rng:
            row = df.iloc[idx]
            props_raw = row.get("properties") if hasattr(row, "get") else row["properties"]
            try:
                props = (
                    json.loads(props_raw) if isinstance(props_raw, str) else dict(props_raw or {})
                )
            except Exception:
                props = {}
            items.append(
                {
                    "objectTypeApiName": str(
                        row.get("objectTypeApiName")
                        if hasattr(row, "get")
                        else row["objectTypeApiName"]
                    ),
                    "pkValue": str(row.get("pkValue") if hasattr(row, "get") else row["pkValue"]),
                    "properties": props,
                }
            )
        return items

    def get_linked_objects(
        self,
        *,
        from_label: str,
        from_pk_field: str,
        from_pk_value: str,
        link_label: str,
        to_label: str,
        direction: str = "forward",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Traverse the graph starting at a node (from_label, from_pk_field=from_pk_value)
        following edges of type link_label to nodes of label to_label.

        Returns a list of dicts with keys: objectTypeApiName, properties.
        """
        if not self.is_available():
            # SQLModel fallback traversal
            if not (self.session and self._inst_repo and self._link_repo):
                return []
            # Resolve LinkType by forward api_name; if not found, try inverse_api_name
            lt = (
                self._meta_repo.get_link_type_by_api_name("ontology", "default", link_label)
                if self._meta_repo
                else None
            )
            if not lt:
                try:
                    stmt = (
                        select(LinkType)
                        .join(Resource, Resource.rid == LinkType.rid)
                        .where(
                            Resource.service == "ontology",
                            Resource.instance == "default",
                            LinkType.inverse_api_name == link_label,
                        )
                    )
                    lt = self.session.exec(stmt).first()
                except Exception:
                    lt = None
            if not lt:
                return []
            # Source instance
            src = self._inst_repo.get_object_instance(
                "ontology", "default", from_label, from_pk_value
            )
            if not src:
                return []
            # List all links by forward api_name (stored with links)
            links = self._link_repo.list_by_link_type("ontology", "default", lt.api_name)
            # Filter by direction
            if direction == "forward":
                dest_rids = [
                    it.to_object_rid
                    for it in links
                    if getattr(it, "from_object_rid", None) == src.rid
                ]
            else:
                dest_rids = [
                    it.from_object_rid
                    for it in links
                    if getattr(it, "to_object_rid", None) == src.rid
                ]
            # Page and hydrate
            start = max(0, int(offset))
            end = start + max(0, int(limit)) if int(limit) > 0 else len(dest_rids)
            out: list[dict[str, Any]] = []
            for rid in dest_rids[start:end]:
                inst = self.session.get(ObjectInstance, rid)
                if not inst:
                    continue
                out.append(
                    {
                        "objectTypeApiName": to_label,
                        "properties": dict(inst.data or {}),
                    }
                )
            return out
        fetch_limit = int(limit) + int(offset) if int(offset) > 0 else int(limit)
        if direction == "forward":
            query = (
                "MATCH (a:Object)-[:`" + link_label + "`]->(b:Object) "
                f"WHERE a.objectTypeApiName = '{from_label}' AND a.pkValue = '{from_pk_value}' AND b.objectTypeApiName = '{to_label}' "
                f"RETURN b.pkValue AS pkValue, b.properties AS properties LIMIT {fetch_limit}"
            )
        else:
            query = (
                "MATCH (a:Object)<-[:`" + link_label + "`]-(b:Object) "
                f"WHERE a.objectTypeApiName = '{from_label}' AND a.pkValue = '{from_pk_value}' AND b.objectTypeApiName = '{to_label}' "
                f"RETURN b.pkValue AS pkValue, b.properties AS properties LIMIT {fetch_limit}"
            )
        try:
            res = self.kuzu.execute(query)
            try:
                df = res.get_as_df()  # type: ignore[attr-defined]
                if df is None or len(df) == 0:
                    return []
                items: list[dict[str, Any]] = []
                start = int(offset) if int(offset) > 0 else 0
                end = start + int(limit) if int(limit) > 0 else len(df)
                rng = range(start, min(end, len(df)))
                for idx in rng:
                    row = df.iloc[idx]
                    props_raw = row.get("properties") if hasattr(row, "get") else row["properties"]
                    try:
                        props = (
                            json.loads(props_raw)
                            if isinstance(props_raw, str)
                            else dict(props_raw or {})
                        )
                    except Exception:
                        props = {}
                    items.append(
                        {
                            "objectTypeApiName": to_label,
                            "properties": props,
                        }
                    )
                return items
            except Exception:
                return []
        except Exception:
            return []
