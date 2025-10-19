"""SQL implementation of the link repository."""

from __future__ import annotations

from registro.core.resource import Resource
from sqlmodel import Session, select

from ontologia.domain.metamodels.instances.models_sql import LinkedObject


class SQLLinkRepository:
    def __init__(self, session: Session):
        self.session = session

    def find(
        self,
        link_type_rid: str,
        from_object_rid: str,
        to_object_rid: str,
    ) -> LinkedObject | None:
        stmt = select(LinkedObject).where(
            LinkedObject.link_type_rid == link_type_rid,
            LinkedObject.from_object_rid == from_object_rid,
            LinkedObject.to_object_rid == to_object_rid,
        )
        return self.session.exec(stmt).first()

    def count_from_degree(self, link_type_rid: str, from_object_rid: str) -> int:
        stmt = select(LinkedObject).where(
            LinkedObject.link_type_rid == link_type_rid,
            LinkedObject.from_object_rid == from_object_rid,
        )
        return len(self.session.exec(stmt).all())

    def count_to_degree(self, link_type_rid: str, to_object_rid: str) -> int:
        stmt = select(LinkedObject).where(
            LinkedObject.link_type_rid == link_type_rid,
            LinkedObject.to_object_rid == to_object_rid,
        )
        return len(self.session.exec(stmt).all())

    def list_by_link_type(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
    ) -> list[LinkedObject]:
        stmt = (
            select(LinkedObject)
            .join(Resource, Resource.rid == LinkedObject.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                LinkedObject.link_type_api_name == link_type_api_name,
            )
        )
        return list(self.session.exec(stmt).all())

    def save(self, link: LinkedObject) -> LinkedObject:
        persistent = self.session.merge(link)
        self.session.commit()
        return persistent

    def delete(self, link: LinkedObject) -> None:
        self.session.delete(link)
        self.session.commit()


__all__ = ["SQLLinkRepository"]
