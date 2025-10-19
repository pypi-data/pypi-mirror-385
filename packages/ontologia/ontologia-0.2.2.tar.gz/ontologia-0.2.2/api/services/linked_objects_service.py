"""
services/linked_objects_service.py
----------------------------------
Service layer for LinkedObjects (edges), enforcing LinkType cardinalities.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import date, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session

from api.core.auth import UserPrincipal
from api.repositories.graph_linked_objects_repository import GraphLinkedObjectsRepository
from api.v2.schemas.bulk import LinkBulkLoadRequest
from api.v2.schemas.linked_objects import (
    LinkCreateRequest,
    LinkedObjectListResponse,
    LinkedObjectReadResponse,
)
from ontologia.config import use_graph_reads_enabled
from ontologia.domain.events import DomainEventBus, NullEventBus
from ontologia.domain.instances.events import LinkCreated, LinkDeleted
from ontologia.domain.instances.repositories import LinkRepository, ObjectInstanceRepository
from ontologia.domain.metamodel.aggregates import LinkAggregate
from ontologia.domain.metamodel.repositories import (
    MetamodelRepository as MetamodelRepositoryProtocol,
)
from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance
from ontologia.domain.metamodels.types.link_type import LinkType
from ontologia.infrastructure.persistence.sql.instances_repository import (
    SQLObjectInstanceRepository,
)
from ontologia.infrastructure.persistence.sql.linked_objects_repository import SQLLinkRepository
from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository,
)

logger = logging.getLogger(__name__)


class _LinkedObjectsServiceBase:
    def __init__(
        self,
        *,
        session: Session,
        service: str,
        instance: str,
        repo: LinkRepository,
        inst_repo: ObjectInstanceRepository,
        metamodel_repo: MetamodelRepositoryProtocol,
        graph_repo: GraphLinkedObjectsRepository | None,
        principal: UserPrincipal | None,
        event_bus: DomainEventBus,
    ) -> None:
        self.session = session
        self.service = service
        self.instance = instance
        self.repo = repo
        self.inst_repo = inst_repo
        self.metamodel_repo = metamodel_repo
        self.graph_repo = graph_repo
        self.principal = principal
        self._event_bus = event_bus
        self._use_graph_reads_flag = use_graph_reads_enabled()

    def _graph_reads_enabled(self) -> bool:
        try:
            return bool(
                self._use_graph_reads_flag and self.graph_repo and self.graph_repo.is_available()
            )
        except Exception:
            return False

    def _link_type(self, api_name: str) -> LinkType:
        lt: LinkType | None = self.metamodel_repo.get_link_type_by_api_name(
            self.service, self.instance, api_name
        )
        if not lt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"LinkType '{api_name}' not found",
            )
        return lt

    def _fetch_instance(self, object_type_api: str, pk: str) -> ObjectInstance | None:
        return self.inst_repo.get_object_instance(
            self.service, self.instance, object_type_api, str(pk)
        )

    def _aggregate(
        self,
        link_type: LinkType,
        from_instance: ObjectInstance,
        to_instance: ObjectInstance,
        properties: dict[str, Any] | None,
    ) -> LinkAggregate:
        aggregate = LinkAggregate(
            link_type=link_type,
            from_instance=from_instance,
            to_instance=to_instance,
            properties=dict(properties or {}),
        )
        aggregate.validate_properties()
        return aggregate

    def _counts(
        self, link_type: LinkType, from_inst: ObjectInstance, to_inst: ObjectInstance
    ) -> tuple[int, int]:
        forward = self.repo.count_from_degree(link_type.rid, from_inst.rid)
        inverse = self.repo.count_to_degree(link_type.rid, to_inst.rid)
        return forward, inverse

    def _to_response(self, link: LinkedObject, link_type: LinkType) -> LinkedObjectReadResponse:
        return LinkedObjectReadResponse(
            rid=link.rid,
            linkTypeApiName=link_type.api_name,
            fromObjectType=link_type.from_object_type_api_name,
            toObjectType=link_type.to_object_type_api_name,
            fromPk=self._pk_from_instance_rid(link.from_object_rid),
            toPk=self._pk_from_instance_rid(link.to_object_rid),
            linkProperties=dict(getattr(link, "data", {}) or {}),
        )

    def _pk_from_instance_rid(self, rid: str) -> str:
        inst = self.session.get(ObjectInstance, rid)
        return inst.pk_value if inst else rid

    def _parse_validity_timestamp(self, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        try:
            text = str(value).strip()
            if not text:
                return None
            return datetime.fromisoformat(text)
        except Exception:
            return None

    def _is_valid_at(self, properties: dict[str, Any], as_of: datetime | None) -> bool:
        if as_of is None:
            return True
        start_raw = (
            properties.get("valid_from")
            or properties.get("validFrom")
            or properties.get("__valid_from")
        )
        end_raw = (
            properties.get("valid_to") or properties.get("validTo") or properties.get("__valid_to")
        )
        start = self._parse_validity_timestamp(start_raw)
        end = self._parse_validity_timestamp(end_raw)
        if start and as_of < start:
            return False
        if end and as_of >= end:
            return False
        return True

    def _apply_link_validity_filter(
        self, links: Iterable[LinkedObjectReadResponse], as_of: datetime | None
    ) -> list[LinkedObjectReadResponse]:
        if as_of is None:
            return list(links)
        filtered: list[LinkedObjectReadResponse] = []
        for link in links:
            props = dict(link.linkProperties or {})
            if self._is_valid_at(props, as_of):
                filtered.append(link)
        return filtered

    def _publish_event(self, event) -> None:
        try:
            self._event_bus.publish(event)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("domain event publish failed: %s", event)

    def _graph_property_names(self, link_type: LinkType) -> list[str]:
        return [prop.api_name for prop in (getattr(link_type, "link_property_types", []) or [])]


class LinkedObjectsCommandService(_LinkedObjectsServiceBase):
    def create_link(
        self, link_type_api_name: str, body: LinkCreateRequest
    ) -> LinkedObjectReadResponse:
        logger.info(
            "linked_objects.create.start service=%s instance=%s linkType=%s fromPk=%s toPk=%s",
            self.service,
            self.instance,
            link_type_api_name,
            body.fromPk,
            body.toPk,
        )
        link_type = self._link_type(link_type_api_name)
        from_inst = self._fetch_instance(link_type.from_object_type_api_name, body.fromPk)
        if not from_inst:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"From object '{link_type.from_object_type_api_name}:{body.fromPk}' not found",
            )
        to_inst = self._fetch_instance(link_type.to_object_type_api_name, body.toPk)
        if not to_inst:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"To object '{link_type.to_object_type_api_name}:{body.toPk}' not found",
            )

        aggregate = self._aggregate(link_type, from_inst, to_inst, getattr(body, "properties", {}))
        forward, inverse = self._counts(link_type, from_inst, to_inst)
        try:
            aggregate.validate_cardinality(forward, inverse)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        existing = self.repo.find(link_type.rid, from_inst.rid, to_inst.rid)
        if existing:
            logger.info(
                "linked_objects.create.duplicate service=%s instance=%s linkType=%s fromPk=%s toPk=%s",
                self.service,
                self.instance,
                link_type_api_name,
                body.fromPk,
                body.toPk,
            )
            return self._to_response(existing, link_type)

        model = aggregate.build_model(service=self.service, instance=self.instance)
        self.session.add(model)
        saved = self.repo.save(model)
        from_pk_field = getattr(link_type.from_object_type, "primary_key_field", None)
        to_pk_field = getattr(link_type.to_object_type, "primary_key_field", None)
        if not from_pk_field:
            from_ot = self.metamodel_repo.get_object_type_by_api_name(
                self.service, self.instance, link_type.from_object_type_api_name
            )
            from_pk_field = getattr(from_ot, "primary_key_field", "")
        if not to_pk_field:
            to_ot = self.metamodel_repo.get_object_type_by_api_name(
                self.service, self.instance, link_type.to_object_type_api_name
            )
            to_pk_field = getattr(to_ot, "primary_key_field", "")
        logger.info(
            "linked_objects.create.success service=%s instance=%s linkType=%s fromPk=%s toPk=%s rid=%s",
            self.service,
            self.instance,
            link_type_api_name,
            body.fromPk,
            body.toPk,
            getattr(saved, "rid", None),
        )
        self._publish_event(
            LinkCreated(
                service=self.service,
                instance=self.instance,
                link_type_api_name=link_type.api_name,
                from_object_type=link_type.from_object_type_api_name,
                to_object_type=link_type.to_object_type_api_name,
                from_primary_key_field=str(from_pk_field or ""),
                to_primary_key_field=str(to_pk_field or ""),
                from_pk=str(body.fromPk),
                to_pk=str(body.toPk),
                properties=dict(aggregate.properties or {}),
                property_names=tuple(self._graph_property_names(link_type)),
            )
        )
        return self._to_response(saved, link_type)

    def delete_link(self, link_type_api_name: str, from_pk: str, to_pk: str) -> bool:
        logger.info(
            "linked_objects.delete.start service=%s instance=%s linkType=%s fromPk=%s toPk=%s",
            self.service,
            self.instance,
            link_type_api_name,
            from_pk,
            to_pk,
        )
        try:
            link_type = self._link_type(link_type_api_name)
        except HTTPException:
            return False
        from_inst = self._fetch_instance(link_type.from_object_type_api_name, from_pk)
        to_inst = self._fetch_instance(link_type.to_object_type_api_name, to_pk)
        if not from_inst or not to_inst:
            return False
        existing = self.repo.find(link_type.rid, from_inst.rid, to_inst.rid)
        if not existing:
            return False
        self.repo.delete(existing)
        from_pk_field = getattr(link_type.from_object_type, "primary_key_field", None)
        to_pk_field = getattr(link_type.to_object_type, "primary_key_field", None)
        if not from_pk_field:
            from_ot = self.metamodel_repo.get_object_type_by_api_name(
                self.service, self.instance, link_type.from_object_type_api_name
            )
            from_pk_field = getattr(from_ot, "primary_key_field", "")
        if not to_pk_field:
            to_ot = self.metamodel_repo.get_object_type_by_api_name(
                self.service, self.instance, link_type.to_object_type_api_name
            )
            to_pk_field = getattr(to_ot, "primary_key_field", "")
        self._publish_event(
            LinkDeleted(
                service=self.service,
                instance=self.instance,
                link_type_api_name=link_type.api_name,
                from_object_type=link_type.from_object_type_api_name,
                to_object_type=link_type.to_object_type_api_name,
                from_primary_key_field=str(from_pk_field or ""),
                to_primary_key_field=str(to_pk_field or ""),
                from_pk=str(from_pk),
                to_pk=str(to_pk),
            )
        )
        logger.info(
            "linked_objects.delete.success service=%s instance=%s linkType=%s fromPk=%s toPk=%s",
            self.service,
            self.instance,
            link_type_api_name,
            from_pk,
            to_pk,
        )
        return True

    def bulk_load_links(
        self, link_type_api_name: str, body: LinkBulkLoadRequest
    ) -> LinkedObjectListResponse:
        link_type = self._link_type(link_type_api_name)
        mode = (body.mode or "create").lower()
        responses: list[LinkedObjectReadResponse] = []
        for item in body.items or []:
            if mode == "delete":
                if self.delete_link(link_type_api_name, item.fromPk, item.toPk):
                    responses.append(
                        LinkedObjectReadResponse(
                            rid=f"{link_type.api_name}:{item.fromPk}->{item.toPk}",
                            linkTypeApiName=link_type.api_name,
                            fromObjectType=link_type.from_object_type_api_name,
                            toObjectType=link_type.to_object_type_api_name,
                            fromPk=item.fromPk,
                            toPk=item.toPk,
                        )
                    )
            else:
                created = self.create_link(
                    link_type_api_name,
                    LinkCreateRequest(
                        fromPk=item.fromPk,
                        toPk=item.toPk,
                        properties=getattr(item, "properties", {}),
                    ),
                )
                responses.append(created)
        return LinkedObjectListResponse(data=responses)


class LinkedObjectsQueryService(_LinkedObjectsServiceBase):
    def get_link(
        self,
        link_type_api_name: str,
        from_pk: str,
        to_pk: str,
        *,
        valid_at: datetime | None = None,
    ) -> LinkedObjectReadResponse | None:
        try:
            link_type = self._link_type(link_type_api_name)
        except HTTPException:
            return None
        if self._graph_reads_enabled() and self.graph_repo:
            response = self._graph_get_link(link_type, from_pk, to_pk)
            if response and self._is_valid_at(dict(response.linkProperties or {}), valid_at):
                return response
            if response:
                return None
        from_inst = self._fetch_instance(link_type.from_object_type_api_name, from_pk)
        to_inst = self._fetch_instance(link_type.to_object_type_api_name, to_pk)
        if not from_inst or not to_inst:
            return None
        lo = self.repo.find(link_type.rid, from_inst.rid, to_inst.rid)
        if not lo:
            return None
        response = self._to_response(lo, link_type)
        if self._is_valid_at(dict(response.linkProperties or {}), valid_at):
            return response
        return None

    def list_links(
        self,
        link_type_api_name: str,
        from_pk: str | None = None,
        to_pk: str | None = None,
        *,
        valid_at: datetime | None = None,
    ) -> LinkedObjectListResponse:
        link_type = self._link_type(link_type_api_name)
        if self._graph_reads_enabled() and self.graph_repo:
            responses = self._graph_list_links(link_type, from_pk, to_pk)
            if responses is not None:
                return LinkedObjectListResponse(
                    data=self._apply_link_validity_filter(responses, valid_at)
                )

        items = self.repo.list_by_link_type(self.service, self.instance, link_type_api_name)
        if from_pk is not None:
            from_inst = self._fetch_instance(link_type.from_object_type_api_name, from_pk)
            from_rid = getattr(from_inst, "rid", None) if from_inst else None
            items = [it for it in items if it.from_object_rid == from_rid]
        if to_pk is not None:
            to_inst = self._fetch_instance(link_type.to_object_type_api_name, to_pk)
            to_rid = getattr(to_inst, "rid", None) if to_inst else None
            items = [it for it in items if it.to_object_rid == to_rid]
        responses = [self._to_response(item, link_type) for item in items]
        return LinkedObjectListResponse(data=self._apply_link_validity_filter(responses, valid_at))

    def _graph_get_link(
        self, link_type: LinkType, from_pk: str, to_pk: str
    ) -> LinkedObjectReadResponse | None:
        edges = self._graph_edges(link_type)
        for edge in edges:
            if str(edge.get("fromPk")) == str(from_pk) and str(edge.get("toPk")) == str(to_pk):
                link_props = {
                    name: edge.get(name)
                    for name in self._graph_property_names(link_type)
                    if name in edge
                }
                return LinkedObjectReadResponse(
                    rid=f"{link_type.api_name}:{from_pk}->{to_pk}",
                    linkTypeApiName=link_type.api_name,
                    fromObjectType=link_type.from_object_type_api_name,
                    toObjectType=link_type.to_object_type_api_name,
                    fromPk=str(from_pk),
                    toPk=str(to_pk),
                    linkProperties=link_props,
                )
        return None

    def _graph_list_links(
        self,
        link_type: LinkType,
        from_pk: str | None,
        to_pk: str | None,
    ) -> list[LinkedObjectReadResponse] | None:
        edges = self._graph_edges(link_type)
        if edges is None:
            return None
        results: list[LinkedObjectReadResponse] = []
        for edge in edges:
            if from_pk is not None and str(edge.get("fromPk")) != str(from_pk):
                continue
            if to_pk is not None and str(edge.get("toPk")) != str(to_pk):
                continue
            link_props = {
                name: edge.get(name)
                for name in self._graph_property_names(link_type)
                if name in edge
            }
            results.append(
                LinkedObjectReadResponse(
                    rid=f"{link_type.api_name}:{edge.get('fromPk')}->{edge.get('toPk')}",
                    linkTypeApiName=link_type.api_name,
                    fromObjectType=link_type.from_object_type_api_name,
                    toObjectType=link_type.to_object_type_api_name,
                    fromPk=str(edge.get("fromPk", "")),
                    toPk=str(edge.get("toPk", "")),
                    linkProperties=link_props,
                )
            )
        return results

    def _graph_edges(self, link_type: LinkType) -> list[dict[str, Any]] | None:
        if not self.graph_repo:
            return None
        from_ot = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, link_type.from_object_type_api_name
        )
        to_ot = self.metamodel_repo.get_object_type_by_api_name(
            self.service, self.instance, link_type.to_object_type_api_name
        )
        if not from_ot or not to_ot or not from_ot.primary_key_field or not to_ot.primary_key_field:
            return None
        return self.graph_repo.list_edges(
            link_type_api_name=link_type.api_name,
            from_label=link_type.from_object_type_api_name,
            to_label=link_type.to_object_type_api_name,
            from_pk_field=from_ot.primary_key_field,
            to_pk_field=to_ot.primary_key_field,
            property_names=self._graph_property_names(link_type),
        )


class LinkedObjectsService:
    def __init__(
        self,
        session: Session,
        service: str = "api",
        instance: str = "default",
        graph_repo: GraphLinkedObjectsRepository | None = None,
        principal: UserPrincipal | None = None,
        event_bus: DomainEventBus | None = None,
        repo: LinkRepository | None = None,
        inst_repo: ObjectInstanceRepository | None = None,
        metamodel_repo: MetamodelRepositoryProtocol | None = None,
    ) -> None:
        self.session = session
        self.service = service
        self.instance = instance
        self.principal = principal
        self.repo = repo or SQLLinkRepository(session)
        self.inst_repo = inst_repo or SQLObjectInstanceRepository(session)
        self.metamodel_repo = metamodel_repo or SQLMetamodelRepository(session)
        self._event_bus = event_bus or NullEventBus()
        if graph_repo is not None:
            self.graph_repo = graph_repo
        elif use_graph_reads_enabled():
            self.graph_repo = GraphLinkedObjectsRepository()
        else:
            self.graph_repo = None

        self._commands = LinkedObjectsCommandService(
            session=self.session,
            service=self.service,
            instance=self.instance,
            repo=self.repo,
            inst_repo=self.inst_repo,
            metamodel_repo=self.metamodel_repo,
            graph_repo=self.graph_repo,
            principal=self.principal,
            event_bus=self._event_bus,
        )
        self._queries = LinkedObjectsQueryService(
            session=self.session,
            service=self.service,
            instance=self.instance,
            repo=self.repo,
            inst_repo=self.inst_repo,
            metamodel_repo=self.metamodel_repo,
            graph_repo=self.graph_repo,
            principal=self.principal,
            event_bus=self._event_bus,
        )

    @property
    def command_service(self) -> LinkedObjectsCommandService:
        return self._commands

    @property
    def query_service(self) -> LinkedObjectsQueryService:
        return self._queries

    def create_link(
        self, link_type_api_name: str, body: LinkCreateRequest
    ) -> LinkedObjectReadResponse:
        return self._commands.create_link(link_type_api_name, body)

    def delete_link(self, link_type_api_name: str, from_pk: str, to_pk: str) -> bool:
        return self._commands.delete_link(link_type_api_name, from_pk, to_pk)

    def bulk_load_links(
        self, link_type_api_name: str, body: LinkBulkLoadRequest
    ) -> LinkedObjectListResponse:
        return self._commands.bulk_load_links(link_type_api_name, body)

    def get_link(
        self,
        link_type_api_name: str,
        from_pk: str,
        to_pk: str,
        *,
        valid_at: datetime | None = None,
    ) -> LinkedObjectReadResponse | None:
        return self._queries.get_link(link_type_api_name, from_pk, to_pk, valid_at=valid_at)

    def list_links(
        self,
        link_type_api_name: str,
        from_pk: str | None = None,
        to_pk: str | None = None,
        *,
        valid_at: datetime | None = None,
    ) -> LinkedObjectListResponse:
        return self._queries.list_links(
            link_type_api_name,
            from_pk=from_pk,
            to_pk=to_pk,
            valid_at=valid_at,
        )
