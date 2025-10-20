"""SQL implementation of the object instance repository."""

from __future__ import annotations

from registro.core.resource import Resource
from sqlmodel import Session, select

from ontologia.domain.metamodels.instances.models_sql import ObjectInstance


class SQLObjectInstanceRepository:
    """Persist object instances using SQLModel persistence."""

    def __init__(self, session: Session):
        self.session = session

    def get_object_instance(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
    ) -> ObjectInstance | None:
        stmt = (
            select(ObjectInstance)
            .join(Resource, Resource.rid == ObjectInstance.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                ObjectInstance.object_type_api_name == object_type_api_name,
                ObjectInstance.pk_value == pk_value,
            )
        )
        res = self.session.exec(stmt).first()
        if res is not None:
            return res
        fallback = select(ObjectInstance).where(
            ObjectInstance.object_type_api_name == object_type_api_name,
            ObjectInstance.pk_value == pk_value,
        )
        return self.session.exec(fallback).first()

    def list_object_instances(
        self,
        service: str,
        instance: str,
        object_type_api_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ObjectInstance]:
        try:
            stmt = (
                select(ObjectInstance)
                .join(Resource, Resource.rid == ObjectInstance.rid)
                .where(Resource.service == service, Resource.instance == instance)
            )
            if object_type_api_name:
                stmt = stmt.where(ObjectInstance.object_type_api_name == object_type_api_name)
            stmt = stmt.limit(limit).offset(offset)
            results = list(self.session.exec(stmt).all())
            if results:
                return results
        except Exception:
            pass

        fallback = select(ObjectInstance)
        if object_type_api_name:
            fallback = fallback.where(ObjectInstance.object_type_api_name == object_type_api_name)
        fallback = fallback.limit(limit).offset(offset)
        return list(self.session.exec(fallback).all())

    def save_object_instance(self, obj: ObjectInstance) -> ObjectInstance:
        persistent = self.session.merge(obj)
        self.session.commit()
        return persistent

    def delete_object_instance(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
    ) -> bool:
        obj = self.get_object_instance(service, instance, object_type_api_name, pk_value)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True


__all__ = ["SQLObjectInstanceRepository"]
