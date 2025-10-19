from __future__ import annotations

import typing

from ontologia_sdk.actions import ObjectActionsNamespace
from ontologia_sdk.client import OntologyClient
from ontologia_sdk.dsl import FieldDescriptor
from ontologia_sdk.link_proxy import LinkDescriptor
from ontologia_sdk.query import QueryBuilder
from ontologia_sdk.types import Page

from .links import WorksForLinkProperties


class ObjectTypeMeta(type):
    def __getattr__(cls, item: str) -> FieldDescriptor:
        fields = getattr(cls, "__fields__", {})
        if item in fields:
            return FieldDescriptor(cls.object_type_api_name, item, fields[item])
        raise AttributeError(item)


class BaseObject(metaclass=ObjectTypeMeta):
    object_type_api_name: str = ""
    primary_key: str = ""
    __fields__: dict[str, dict[str, typing.Any]] = {}

    def __init__(
        self, client: OntologyClient, rid: str, pkValue: str, properties: dict[str, typing.Any]
    ):
        self._client = client
        self.rid = rid
        self.pk = pkValue
        for k, v in dict(properties or {}).items():
            setattr(self, k, v)
        shared_actions = getattr(client, "actions", None)
        self.actions = ObjectActionsNamespace(
            client=client,
            object_type=self.object_type_api_name,
            pk_getter=lambda: self.pk,
            shared_namespace=shared_actions,
        )

    @classmethod
    def get(cls, client: OntologyClient, pk: str):
        data = client.get_object(cls.object_type_api_name, pk)
        return cls.from_response(client, data)

    @classmethod
    def from_response(cls, client: OntologyClient, data: dict[str, typing.Any]):
        props = dict(data.get("properties") or {})
        return cls(client, data.get("rid", ""), str(data.get("pkValue", "")), props)

    @classmethod
    def search(
        cls,
        client: OntologyClient,
        where: list[dict] | None = None,
        order_by: list[dict] | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        qb = cls.search_builder(client)
        if where:
            qb.where(where)
        if order_by:
            qb.order_by(order_by)
        qb.limit(limit)
        qb.offset(offset)
        return qb.all()

    @classmethod
    def search_typed(
        cls,
        client: OntologyClient,
        where: list[dict] | None = None,
        order_by: list[dict] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Page[typing.Any]:
        qb = cls.search_builder(client)
        if where:
            qb.where(where)
        if order_by:
            qb.order_by(order_by)
        qb.limit(limit)
        qb.offset(offset)
        return qb.all_typed()

    @classmethod
    def iter_search(
        cls,
        client: OntologyClient,
        where: list[dict] | None = None,
        order_by: list[dict] | None = None,
        page_size: int = 100,
        offset: int = 0,
    ):
        qb = cls.search_builder(client)
        if where:
            qb.where(where)
        if order_by:
            qb.order_by(order_by)
        qb.limit(page_size)
        qb.offset(offset)
        return qb.iter_pages(page_size=page_size)

    @classmethod
    def iter_search_typed(
        cls,
        client: OntologyClient,
        where: list[dict] | None = None,
        order_by: list[dict] | None = None,
        page_size: int = 100,
        offset: int = 0,
    ):
        qb = cls.search_builder(client)
        if where:
            qb.where(where)
        if order_by:
            qb.order_by(order_by)
        qb.limit(page_size)
        qb.offset(offset)
        return qb.iter_pages_typed(page_size=page_size)

    @classmethod
    def search_builder(cls, client: OntologyClient) -> QueryBuilder:
        return QueryBuilder(client=client, object_type=cls.object_type_api_name, object_cls=cls)

    @classmethod
    def field(cls, name: str) -> FieldDescriptor:
        fields = getattr(cls, "__fields__", {})
        if name not in fields:
            raise AttributeError(name)
        return FieldDescriptor(cls.object_type_api_name, name, fields[name])

    def list_actions(self):
        return self._client.list_actions(self.object_type_api_name, self.pk)

    def execute_action(self, action_api_name: str, parameters: dict[str, typing.Any] | None = None):
        return self._client.execute_action(
            self.object_type_api_name, self.pk, action_api_name, parameters
        )


class Company(BaseObject):
    object_type_api_name = "company"
    primary_key = "id"
    __fields__ = {
        "id": {"dataType": "string", "displayName": "ID", "required": True},
        "name": {"dataType": "string", "displayName": "Name"},
    }
    if typing.TYPE_CHECKING:
        id: str  # noqa: N815
        name: str | None  # noqa: N815


class Employee(BaseObject):
    object_type_api_name = "employee"
    primary_key = "id"
    __fields__ = {
        "id": {"dataType": "string", "displayName": "ID", "required": True},
        "name": {"dataType": "string", "displayName": "Name"},
        "dept": {"dataType": "string", "displayName": "Department"},
    }
    if typing.TYPE_CHECKING:
        id: str  # noqa: N815
        name: str | None  # noqa: N815
        dept: str | None  # noqa: N815

    works_for = LinkDescriptor(
        "works_for", to_object_type="company", properties_cls=WorksForLinkProperties
    )

    # Links: works_for
    def traverse_works_for(self, limit: int = 100, offset: int = 0):
        return self._client.traverse(
            self.object_type_api_name, self.pk, "works_for", limit=limit, offset=offset
        )

    def get_works_for_link(self, to_pk: str):
        return self._client.get_link("works_for", self.pk, to_pk)

    def get_works_for_link_typed(self, to_pk: str):
        raw = self._client.get_link("works_for", self.pk, to_pk)
        props = dict(raw.get("linkProperties") or {})
        return WorksForLinkProperties.from_dict(props)

    def create_works_for(self, to_pk: str, properties: dict[str, typing.Any] | None = None):
        return self._client.create_link("works_for", self.pk, to_pk, properties)

    def delete_works_for(self, to_pk: str) -> None:
        return self._client.delete_link("works_for", self.pk, to_pk)

    def list_works_for(self, to_pk: str | None = None):
        return self._client.list_links("works_for", from_pk=self.pk, to_pk=to_pk)
