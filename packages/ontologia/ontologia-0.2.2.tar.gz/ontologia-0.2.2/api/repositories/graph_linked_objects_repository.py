"""
repositories/graph_linked_objects_repository.py
-----------------------------------------------
Graph-backed repository for reading linked objects (edges) from KùzuDB.

This repository provides read methods that query the materialized graph.
Writes remain in SQLModel-backed repositories until the migration is complete.
"""

from __future__ import annotations

from api.repositories.kuzudb_repository import KuzuDBRepository


class GraphLinkedObjectsRepository:
    """Read-only repository for edges stored in KùzuDB."""

    def __init__(self, kuzu_repo: KuzuDBRepository | None = None):
        self.kuzu = kuzu_repo or KuzuDBRepository()

    def is_available(self) -> bool:
        return self.kuzu is not None and self.kuzu.is_available()

    def list_edges(
        self,
        link_type_api_name: str,
        from_label: str,
        to_label: str,
        from_pk_field: str,
        to_pk_field: str,
        *,
        limit: int = 100,
        offset: int = 0,
        property_names: list[str] | None = None,
    ) -> list[dict[str, str]]:
        """
        Returns a list of dicts with keys: fromPk, toPk.
        """
        if not self.is_available():
            return []
        fetch_limit = int(limit) + int(offset) if int(offset) > 0 else int(limit)
        # Build RETURN clause with optional edge properties
        props_return = ""
        if property_names:
            prop_parts = [f"r.`{p}` AS `{p}`" for p in property_names]
            props_return = ", " + ", ".join(prop_parts)
        query = (
            f"MATCH (a:`{from_label}`)-[r:`{link_type_api_name}`]->(b:`{to_label}`) "
            f"RETURN a.`{from_pk_field}` AS fromPk, b.`{to_pk_field}` AS toPk{props_return} "
            f"LIMIT {fetch_limit}"
        )
        try:
            res = self.kuzu.execute(query)
            try:
                df = res.get_as_df()  # type: ignore[attr-defined]
                if df is None or len(df) == 0:
                    return []
                items: list[dict[str, str]] = []
                start = int(offset) if int(offset) > 0 else 0
                end = start + int(limit) if int(limit) > 0 else len(df)
                rng = range(start, min(end, len(df)))
                for idx in rng:
                    row = df.iloc[idx]
                    item = {
                        "fromPk": str(row["fromPk"]),
                        "toPk": str(row["toPk"]),
                    }
                    if property_names:
                        for p in property_names:
                            if p in df.columns:
                                try:
                                    item[p] = row[p]
                                except Exception:
                                    item[p] = None
                    items.append(item)
                return items
            except Exception:
                return []
        except Exception:
            return []
