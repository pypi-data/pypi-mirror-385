"""SQL implementation of the metamodel repository."""

from __future__ import annotations

from registro.core.resource import Resource
from sqlalchemy import true
from sqlmodel import Session, select

from ontologia.domain.metamodels.types.action_type import ActionType
from ontologia.domain.metamodels.types.interface_type import InterfaceType
from ontologia.domain.metamodels.types.link_type import LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.types.query_type import QueryType


class SQLMetamodelRepository:
    def __init__(self, session: Session):
        self.session = session

    # ObjectType
    def get_object_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> ObjectType | None:
        statement = (
            select(ObjectType)
            .join(Resource, Resource.rid == ObjectType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                ObjectType.api_name == api_name,
            )
        )
        if version is not None:
            statement = statement.where(ObjectType.version == version)
        elif not include_inactive:
            statement = statement.where(ObjectType.is_latest == true())
        return self.session.exec(statement).first()

    def list_object_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[ObjectType]:
        statement = (
            select(ObjectType)
            .join(Resource, Resource.rid == ObjectType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
            )
        )
        if not include_inactive:
            statement = statement.where(ObjectType.is_latest == true())
        return list(self.session.exec(statement).all())

    def save_object_type(self, object_type: ObjectType) -> ObjectType:
        persistent = self.session.merge(object_type)
        self.session.commit()
        return persistent

    def delete_object_type(self, service: str, instance: str, api_name: str) -> bool:
        object_type = self.get_object_type_by_api_name(service, instance, api_name)
        if not object_type:
            return False
        self.session.delete(object_type)
        self.session.commit()
        return True

    # LinkType
    def get_link_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> LinkType | None:
        statement = (
            select(LinkType)
            .join(Resource, Resource.rid == LinkType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                LinkType.api_name == api_name,
            )
        )
        if version is not None:
            statement = statement.where(LinkType.version == version)
        elif not include_inactive:
            statement = statement.where(LinkType.is_latest == true())
        return self.session.exec(statement).first()

    def list_link_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[LinkType]:
        statement = (
            select(LinkType)
            .join(Resource, Resource.rid == LinkType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
            )
        )
        if not include_inactive:
            statement = statement.where(LinkType.is_latest == true())
        return list(self.session.exec(statement).all())

    def save_link_type(self, link_type: LinkType) -> LinkType:
        persistent = self.session.merge(link_type)
        self.session.commit()
        return persistent

    def delete_link_type(self, service: str, instance: str, api_name: str) -> bool:
        link_type = self.get_link_type_by_api_name(service, instance, api_name)
        if not link_type:
            return False
        self.session.delete(link_type)
        self.session.commit()
        return True

    # InterfaceType
    def get_interface_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> InterfaceType | None:
        statement = (
            select(InterfaceType)
            .join(Resource, Resource.rid == InterfaceType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                InterfaceType.api_name == api_name,
            )
        )
        if version is not None:
            statement = statement.where(InterfaceType.version == version)
        elif not include_inactive:
            statement = statement.where(InterfaceType.is_latest == true())
        return self.session.exec(statement).first()

    def list_interface_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[InterfaceType]:
        statement = (
            select(InterfaceType)
            .join(Resource, Resource.rid == InterfaceType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
            )
        )
        if not include_inactive:
            statement = statement.where(InterfaceType.is_latest == true())
        return list(self.session.exec(statement).all())

    def save_interface_type(self, interface_type: InterfaceType) -> InterfaceType:
        persistent = self.session.merge(interface_type)
        self.session.commit()
        self.session.refresh(persistent)
        return persistent

    def delete_interface_type(
        self,
        service: str,
        instance: str,
        api_name: str,
    ) -> bool:
        interface_type = self.get_interface_type_by_api_name(service, instance, api_name)
        if not interface_type:
            return False
        self.session.delete(interface_type)
        self.session.commit()
        return True

    # ActionType
    def get_action_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> ActionType | None:
        statement = (
            select(ActionType)
            .join(Resource, Resource.rid == ActionType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                ActionType.api_name == api_name,
            )
        )
        if version is not None:
            statement = statement.where(ActionType.version == version)
        elif not include_inactive:
            statement = statement.where(ActionType.is_latest == true())
        return self.session.exec(statement).first()

    def list_action_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[ActionType]:
        statement = (
            select(ActionType)
            .join(Resource, Resource.rid == ActionType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
            )
        )
        if not include_inactive:
            statement = statement.where(ActionType.is_latest == true())
        return list(self.session.exec(statement).all())

    def list_action_types_for_object_type(
        self,
        service: str,
        instance: str,
        target_object_type_api_name: str,
    ) -> list[ActionType]:
        statement = (
            select(ActionType)
            .join(Resource, Resource.rid == ActionType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                ActionType.target_object_type_api_name == target_object_type_api_name,
            )
        )
        return list(self.session.exec(statement).all())

    def save_action_type(self, action: ActionType) -> ActionType:
        persistent = self.session.merge(action)
        self.session.commit()
        self.session.refresh(persistent)
        return persistent

    def delete_action_type(
        self,
        service: str,
        instance: str,
        api_name: str,
    ) -> bool:
        action = self.get_action_type_by_api_name(service, instance, api_name)
        if not action:
            return False
        self.session.delete(action)
        self.session.commit()
        return True

    # QueryType
    def get_query_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> QueryType | None:
        statement = (
            select(QueryType)
            .join(Resource, Resource.rid == QueryType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
                QueryType.api_name == api_name,
            )
        )
        if version is not None:
            statement = statement.where(QueryType.version == version)
        elif not include_inactive:
            statement = statement.where(QueryType.is_latest == true())
        return self.session.exec(statement).first()

    def list_query_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[QueryType]:
        statement = (
            select(QueryType)
            .join(Resource, Resource.rid == QueryType.rid)
            .where(
                Resource.service == service,
                Resource.instance == instance,
            )
        )
        if not include_inactive:
            statement = statement.where(QueryType.is_latest == true())
        return list(self.session.exec(statement).all())

    def save_query_type(self, query_type: QueryType) -> QueryType:
        persistent = self.session.merge(query_type)
        self.session.commit()
        self.session.refresh(persistent)
        return persistent

    def delete_query_type(
        self,
        service: str,
        instance: str,
        api_name: str,
    ) -> bool:
        query_type = self.get_query_type_by_api_name(service, instance, api_name)
        if not query_type:
            return False
        self.session.delete(query_type)
        self.session.commit()
        return True


__all__ = ["SQLMetamodelRepository"]
