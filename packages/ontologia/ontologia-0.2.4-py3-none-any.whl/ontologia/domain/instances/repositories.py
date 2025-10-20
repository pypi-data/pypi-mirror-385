"""Repository interfaces for the instances bounded context."""

from __future__ import annotations

from typing import Protocol

from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance


class ObjectInstanceRepository(Protocol):
    def get_object_instance(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
    ) -> ObjectInstance | None: ...

    def list_object_instances(
        self,
        service: str,
        instance: str,
        object_type_api_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ObjectInstance]: ...

    def save_object_instance(self, obj: ObjectInstance) -> ObjectInstance: ...

    def delete_object_instance(
        self,
        service: str,
        instance: str,
        object_type_api_name: str,
        pk_value: str,
    ) -> bool: ...


class LinkRepository(Protocol):
    def count_from_degree(self, link_type_rid: str, from_object_rid: str) -> int: ...

    def count_to_degree(self, link_type_rid: str, to_object_rid: str) -> int: ...

    def find(
        self, link_type_rid: str, from_object_rid: str, to_object_rid: str
    ) -> LinkedObject | None: ...

    def save(self, link: LinkedObject) -> LinkedObject: ...

    def delete(self, link: LinkedObject) -> None: ...

    def list_by_link_type(
        self,
        service: str,
        instance: str,
        link_type_api_name: str,
    ) -> list[LinkedObject]: ...
