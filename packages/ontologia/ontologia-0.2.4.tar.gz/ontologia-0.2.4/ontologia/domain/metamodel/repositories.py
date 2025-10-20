"""Repository interfaces for the metamodel bounded context."""

from __future__ import annotations

from typing import Protocol

from ontologia.domain.metamodels.types.action_type import ActionType
from ontologia.domain.metamodels.types.interface_type import InterfaceType
from ontologia.domain.metamodels.types.link_type import LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.types.query_type import QueryType


class MetamodelRepository(Protocol):
    """Abstracts persistence operations needed by the metamodel domain."""

    # ObjectType
    def get_object_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> ObjectType | None: ...

    def list_object_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[ObjectType]: ...

    def save_object_type(self, object_type: ObjectType) -> ObjectType: ...

    def delete_object_type(self, service: str, instance: str, api_name: str) -> bool: ...

    # LinkType
    def get_link_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> LinkType | None: ...

    def list_link_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[LinkType]: ...

    def save_link_type(self, link_type: LinkType) -> LinkType: ...

    def delete_link_type(self, service: str, instance: str, api_name: str) -> bool: ...

    # InterfaceType
    def get_interface_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> InterfaceType | None: ...

    def list_interface_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[InterfaceType]: ...

    def save_interface_type(self, itf: InterfaceType) -> InterfaceType: ...

    def delete_interface_type(self, service: str, instance: str, api_name: str) -> bool: ...

    # ActionType
    def get_action_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> ActionType | None: ...

    def list_action_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[ActionType]: ...

    def list_action_types_for_object_type(
        self,
        service: str,
        instance: str,
        target_object_type_api_name: str,
    ) -> list[ActionType]: ...

    def save_action_type(self, action: ActionType) -> ActionType: ...

    def delete_action_type(self, service: str, instance: str, api_name: str) -> bool: ...

    # QueryType
    def get_query_type_by_api_name(
        self,
        service: str,
        instance: str,
        api_name: str,
        *,
        version: int | None = None,
        include_inactive: bool = False,
    ) -> QueryType | None: ...

    def list_query_types(
        self,
        service: str,
        instance: str,
        *,
        include_inactive: bool = False,
    ) -> list[QueryType]: ...

    def save_query_type(self, query_type: QueryType) -> QueryType: ...

    def delete_query_type(self, service: str, instance: str, api_name: str) -> bool: ...
