"""
services/metamodel_service.py
------------------------------
Camada de serviço para lógica de negócio do metamodelo.

Responsabilidades:
- Validações de regras de negócio
- Conversão entre DTOs (schemas) e Modelos de DB
- Orquestração de operações complexas
- Tratamento de erros de negócio
"""

import ast
import logging
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from api.core.auth import UserPrincipal
from api.services.instances_service import InstancesService
from api.v2.schemas.actions import ActionParameterDefinition
from api.v2.schemas.metamodel import (
    ActionTypeListResponse,
    ActionTypePutRequest,
    ActionTypeReadResponse,
    InterfaceListResponse,
    InterfacePutRequest,
    InterfaceReadResponse,
    LinkInverseDefinition,
    LinkTypePutRequest,
    LinkTypeReadResponse,
    ObjectTypePutRequest,
    ObjectTypeReadResponse,
    PropertyDefinition,
    QueryTypeListResponse,
    QueryTypePutRequest,
    QueryTypeReadResponse,
    RuleDefinition,
)
from api.v2.schemas.search import ObjectSearchRequest, OrderBySpec, WhereCondition
from datacatalog.models import Dataset, DatasetBranch, DatasetTransaction, TransactionType
from ontologia.domain.events import DomainEventBus, NullEventBus
from ontologia.domain.metamodel.aggregates import ObjectTypeAggregate
from ontologia.domain.metamodel.events import ObjectTypeCreated, ObjectTypeUpdated
from ontologia.domain.metamodel.repositories import (
    MetamodelRepository as MetamodelRepositoryProtocol,
)
from ontologia.domain.metamodel.value_objects import PrimaryKeyDefinition
from ontologia.domain.metamodel.value_objects import (
    PropertyDefinition as DomainPropertyDefinition,
)
from ontologia.domain.metamodels.instances.models_sql import LinkedObject, ObjectInstance
from ontologia.domain.metamodels.instances.object_type_data_source import ObjectTypeDataSource
from ontologia.domain.metamodels.migrations.migration_task import (
    MigrationTask,
    MigrationTaskStatus,
)
from ontologia.domain.metamodels.types.action_type import ActionType
from ontologia.domain.metamodels.types.interface_type import InterfaceType
from ontologia.domain.metamodels.types.link_property_type import LinkPropertyType
from ontologia.domain.metamodels.types.link_type import Cardinality, LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.types.query_type import QueryType
from ontologia.infrastructure.persistence.sql.metamodel_repository import (
    SQLMetamodelRepository,
)

logger = logging.getLogger(__name__)


class MetamodelService:
    """
    Serviço de negócio para operações de metamodelo.

    Padrão Service: Encapsula lógica de negócio e orquestra repositórios.
    """

    def __init__(
        self,
        session: Session,
        service: str = "api",
        instance: str = "default",
        principal: UserPrincipal | None = None,
        event_bus: DomainEventBus | None = None,
        repo: MetamodelRepositoryProtocol | None = None,
    ):
        """
        Args:
            session: Sessão SQLModel injetada
            service: Service identifier (multi-tenancy)
            instance: Instance identifier (multi-tenancy)
        """
        self.repo = repo or SQLMetamodelRepository(session)
        self.session = session
        self.service = service
        self.instance = instance
        self.principal = principal
        self._event_bus = event_bus or NullEventBus()

    # --- ObjectType Operations ---

    def upsert_object_type(
        self, api_name: str, schema: ObjectTypePutRequest
    ) -> ObjectTypeReadResponse:
        """
        Cria uma nova versão de ObjectType (imutável por versão) ou cria um novo ObjectType.

        Args:
            api_name: API name do ObjectType
            schema: Dados do ObjectType (request body)

        Returns:
            ObjectType criado (nova versão) ou atualizado

        Raises:
            HTTPException: Se validações falharem
        """
        try:
            property_definitions = [
                DomainPropertyDefinition(
                    api_name=prop_name,
                    data_type=prop_def.dataType,
                    display_name=prop_def.displayName,
                    description=prop_def.description,
                    required=bool(prop_def.required),
                    quality_checks=tuple(prop_def.qualityChecks or []),
                    derivation_script=prop_def.derivationScript,
                    is_primary_key=(prop_name == schema.primaryKey),
                )
                for prop_name, prop_def in schema.properties.items()
            ]
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        primary_key = PrimaryKeyDefinition(schema.primaryKey)

        if schema.primaryKey not in schema.properties:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"primaryKey '{schema.primaryKey}' must be defined in properties",
            )
        pk_property = schema.properties[schema.primaryKey]
        if not pk_property.required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"primaryKey '{schema.primaryKey}' must be required",
            )

        existing = self.repo.get_object_type_by_api_name(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
        )

        migration_operations: list[dict[str, Any]] = []
        existing_version = 0
        if existing:
            existing_version = existing.version
            existing_props_map = {p.api_name: p for p in existing.property_types}
            for prop_name, old_prop in existing_props_map.items():
                new_prop_def = schema.properties.get(prop_name)
                if new_prop_def is None:
                    migration_operations.append(
                        {
                            "property": prop_name,
                            "operation": "drop_property",
                        }
                    )
                    continue
                old_type = str(old_prop.data_type)
                new_type = new_prop_def.dataType
                if old_type != new_type:
                    migration_operations.append(
                        {
                            "property": prop_name,
                            "operation": "change_type",
                            "from": old_type,
                            "to": new_type,
                            "recommendedTransformation": f"CAST({prop_name} AS {new_type.upper()})",
                        }
                    )

        new_version = 1
        if existing:
            # Se mudança de PK for solicitada, bloquear se existirem instâncias
            if existing.primary_key_field != schema.primaryKey:
                inst_exists = self.session.exec(
                    select(ObjectInstance).where(
                        ObjectInstance.object_type_api_name == existing.api_name
                    )
                ).first()
                if inst_exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Cannot change primaryKey for ObjectType '{existing.api_name}' while instances exist"
                        ),
                    )
            existing.is_latest = False
            self.session.add(existing)
            new_version = existing.version + 1

        object_type = ObjectType(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            display_name=schema.displayName,
            description=schema.description,
            primary_key_field=schema.primaryKey,
            version=new_version,
            is_latest=True,
        )
        self.session.add(object_type)
        self.session.flush()  # Garantir RID para filhos

        try:
            aggregate = ObjectTypeAggregate.new(
                object_type=object_type,
                properties=property_definitions,
                primary_key=primary_key,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        created_count = len(aggregate.object_type.property_types)
        for prop_model in aggregate.object_type.property_types:
            self.session.add(prop_model)

        try:
            implements = list(schema.implements or [])
        except Exception:
            implements = []
        if implements:
            iface_entities: list[InterfaceType] = []
            for iface_api in implements:
                itf = self.repo.get_interface_type_by_api_name(
                    service=self.service,
                    instance=self.instance,
                    api_name=iface_api,
                )
                if not itf:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"InterfaceType '{iface_api}' not found",
                    )
                iface_entities.append(itf)
            object_type.interfaces = iface_entities

        t0 = perf_counter()

        if existing and migration_operations:
            task = MigrationTask(
                service=self.service,
                instance=self.instance,
                api_name=f"{api_name}_v{existing_version}_to_v{new_version}",
                display_name=f"{api_name} migration {existing_version}->{new_version}",
                object_type_api_name=api_name,
                from_version=existing_version,
                to_version=new_version,
                plan={
                    "objectType": api_name,
                    "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    "operations": migration_operations,
                },
                status=MigrationTaskStatus.PENDING,
            )
            self.session.add(task)

        self.session.commit()
        dt = perf_counter() - t0

        fresh = self.repo.get_object_type_by_api_name(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            version=new_version,
        )
        if existing:
            self._event_bus.publish(
                ObjectTypeUpdated(
                    service=self.service,
                    instance=self.instance,
                    object_type_api_name=api_name,
                    from_version=existing_version,
                    to_version=new_version,
                )
            )
        else:
            self._event_bus.publish(
                ObjectTypeCreated(
                    service=self.service,
                    instance=self.instance,
                    object_type_api_name=api_name,
                    version=new_version,
                )
            )
        logger.info(
            "object_type.versioned_upsert service=%s instance=%s api_name=%s version=%d created_props=%d duration=%.4fs",
            self.service,
            self.instance,
            api_name,
            new_version,
            created_count,
            dt,
        )
        if existing and migration_operations:
            logger.info(
                "object_type.migration_task_created service=%s instance=%s api_name=%s from_version=%d to_version=%d operations=%d",
                self.service,
                self.instance,
                api_name,
                existing_version,
                new_version,
                len(migration_operations),
            )
        return self._object_type_to_response(fresh)

    def get_object_type(
        self, api_name: str, *, version: int | None = None
    ) -> ObjectTypeReadResponse | None:
        """
        Busca um ObjectType por api_name.

        Args:
            api_name: API name do ObjectType

        Returns:
            ObjectType ou None se não encontrado
        """
        object_type = self.repo.get_object_type_by_api_name(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            version=version,
            include_inactive=bool(version is not None),
        )

        if not object_type:
            return None

        return self._object_type_to_response(object_type)

    def list_object_types(self, *, include_inactive: bool = False) -> list[ObjectTypeReadResponse]:
        """
        Lista todos os ObjectTypes.

        Returns:
            Lista de ObjectTypes
        """
        object_types = self.repo.list_object_types(
            service=self.service,
            instance=self.instance,
            include_inactive=include_inactive,
        )

        return [self._object_type_to_response(ot) for ot in object_types]

    def delete_object_type(self, api_name: str) -> bool:
        """
        Deleta um ObjectType.

        Args:
            api_name: API name do ObjectType

        Returns:
            True se deletado, False se não encontrado
        """
        # Bloquear se houver LinkTypes que referenciam este ObjectType
        ref_lts = [
            lt
            for lt in self.repo.list_link_types(self.service, self.instance)
            if lt.from_object_type_api_name == api_name or lt.to_object_type_api_name == api_name
        ]
        if ref_lts:
            names = ", ".join(sorted({lt.api_name for lt in ref_lts}))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot delete ObjectType '{api_name}': referenced by LinkTypes [{names}]"
                ),
            )
        # Bloquear se houver instâncias
        inst_exists = self.session.exec(
            select(ObjectInstance).where(ObjectInstance.object_type_api_name == api_name)
        ).first()
        if inst_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(f"Cannot delete ObjectType '{api_name}': instances exist"),
            )
        return self.repo.delete_object_type(
            service=self.service, instance=self.instance, api_name=api_name
        )

    # --- LinkType Operations ---

    def upsert_link_type(self, api_name: str, schema: LinkTypePutRequest) -> LinkTypeReadResponse:
        """
        Cria ou atualiza um LinkType.

        Args:
            api_name: API name do LinkType
            schema: Dados do LinkType (request body)

        Returns:
            LinkType criado/atualizado

        Raises:
            HTTPException: Se validações falharem
        """
        # Validação 1: ObjectTypes existem?
        from_ot = self.repo.get_object_type_by_api_name(
            self.service, self.instance, schema.fromObjectType
        )
        to_ot = self.repo.get_object_type_by_api_name(
            self.service, self.instance, schema.toObjectType
        )

        if not from_ot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ObjectType '{schema.fromObjectType}' not found",
            )

        if not to_ot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ObjectType '{schema.toObjectType}' not found",
            )

        # Conversão: string → Enum
        cardinality = Cardinality(schema.cardinality)

        # Buscar existente
        existing = self.repo.get_link_type_by_api_name(
            service=self.service, instance=self.instance, api_name=api_name
        )

        new_version = 1
        if existing:
            changing_endpoints = (
                existing.from_object_type_api_name != schema.fromObjectType
                or existing.to_object_type_api_name != schema.toObjectType
            )
            if changing_endpoints:
                edge_exists = self.session.exec(
                    select(LinkedObject).where(LinkedObject.link_type_api_name == existing.api_name)
                ).first()
                if edge_exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Cannot change endpoints of LinkType '{existing.api_name}' while links exist"
                        ),
                    )
            existing.is_latest = False
            self.session.add(existing)
            new_version = existing.version + 1

        link_type = LinkType(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            display_name=schema.displayName,
            inverse_api_name=schema.inverse.apiName,
            inverse_display_name=schema.inverse.displayName,
            cardinality=cardinality,
            from_object_type_api_name=schema.fromObjectType,
            to_object_type_api_name=schema.toObjectType,
            version=new_version,
            is_latest=True,
        )
        self.session.add(link_type)
        self.session.flush()

        # Opcional: resolver backing dataset e mappings de colunas
        backing_ds = None
        if hasattr(schema, "backingDatasetApiName") and schema.backingDatasetApiName:
            backing_ds = self.session.exec(
                select(Dataset).where(Dataset.api_name == schema.backingDatasetApiName)
            ).first()
            if not backing_ds:
                raise HTTPException(
                    status_code=400, detail=f"Dataset '{schema.backingDatasetApiName}' not found"
                )
        # Aplicar configurações de sync de relações
        link_type.backing_dataset_rid = backing_ds.rid if backing_ds else None
        if hasattr(schema, "fromPropertyMapping"):
            link_type.from_property_mapping = schema.fromPropertyMapping
        if hasattr(schema, "toPropertyMapping"):
            link_type.to_property_mapping = schema.toPropertyMapping
        if hasattr(schema, "propertyMappings") and schema.propertyMappings is not None:
            link_type.property_mappings = dict(schema.propertyMappings)
        try:
            link_type.incremental_field = getattr(schema, "incrementalField", None)
        except Exception:
            link_type.incremental_field = None

        # Resolver object types
        link_type.validate_and_resolve_object_types(self.session)

        # --- Reconciliação de Propriedades do Link ---
        try:
            schema_props = dict(schema.properties or {})
        except Exception:
            schema_props = {}
        created_props = 0
        if schema_props is not None:
            for prop_name, prop_def in schema_props.items():
                new_lp = LinkPropertyType(
                    service=self.service,
                    instance=self.instance,
                    api_name=prop_name,
                    display_name=prop_def.displayName,
                    description=prop_def.description,
                    data_type=prop_def.dataType,
                    required=bool(getattr(prop_def, "required", False) or False),
                    quality_checks=list(getattr(prop_def, "qualityChecks", []) or []),
                    link_type_rid=link_type.rid,
                    link_type_api_name=link_type.api_name,
                )
                self.session.add(new_lp)
                created_props += 1

        t0 = perf_counter()
        self.session.commit()
        dt = perf_counter() - t0

        fresh = self.repo.get_link_type_by_api_name(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            version=new_version,
        )
        logger.info(
            "link_type.versioned_upsert service=%s instance=%s api_name=%s version=%d created_props=%d duration=%.4fs",
            self.service,
            self.instance,
            api_name,
            new_version,
            created_props,
            dt,
        )

        return self._link_type_to_response(fresh)

    def get_link_type(
        self, api_name: str, *, version: int | None = None
    ) -> LinkTypeReadResponse | None:
        """
        Busca um LinkType por api_name.

        Args:
            api_name: API name do LinkType

        Returns:
            LinkType ou None se não encontrado
        """
        link_type = self.repo.get_link_type_by_api_name(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            version=version,
            include_inactive=bool(version is not None),
        )

        if not link_type:
            return None

        return self._link_type_to_response(link_type)

    def list_link_types(self, *, include_inactive: bool = False) -> list[LinkTypeReadResponse]:
        """
        Lista todos os LinkTypes.

        Returns:
            Lista de LinkTypes
        """
        link_types = self.repo.list_link_types(
            service=self.service,
            instance=self.instance,
            include_inactive=include_inactive,
        )

        return [self._link_type_to_response(lt) for lt in link_types]

    def delete_link_type(self, api_name: str) -> bool:
        """
        Deleta um LinkType.

        Args:
            api_name: API name do LinkType

        Returns:
            True se deletado, False se não encontrado
        """
        # Bloquear se existirem relações (LinkedObject) deste tipo
        edge_exists = self.session.exec(
            select(LinkedObject).where(LinkedObject.link_type_api_name == api_name)
        ).first()
        if edge_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(f"Cannot delete LinkType '{api_name}': links exist"),
            )
        return self.repo.delete_link_type(
            service=self.service, instance=self.instance, api_name=api_name
        )

    # --- ActionType Operations ---

    def upsert_action_type(
        self, api_name: str, schema: ActionTypePutRequest
    ) -> ActionTypeReadResponse:
        # Validate target ObjectType exists
        target = self.repo.get_object_type_by_api_name(
            self.service, self.instance, schema.targetObjectType
        )
        if not target:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ObjectType '{schema.targetObjectType}' not found",
            )

        # Validate rule syntax and allowed constructs early (submissionCriteria + validationRules)
        def _validate_rules(rules: list[RuleDefinition] | None, kind: str) -> None:
            allowed_names = {"params", "target_object", "context"}

            def _check_node(node: ast.AST) -> bool:
                if isinstance(node, ast.Expression):
                    return _check_node(node.body)
                if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
                    return all(_check_node(v) for v in node.values)
                if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                    return _check_node(node.operand)
                if isinstance(node, ast.Compare):
                    if not _check_node(node.left):
                        return False
                    if not all(_check_node(c) for c in node.comparators):
                        return False
                    # ops must be among the allowed set
                    allowed_ops = (
                        ast.Eq,
                        ast.NotEq,
                        ast.Lt,
                        ast.LtE,
                        ast.Gt,
                        ast.GtE,
                        ast.In,
                        ast.NotIn,
                    )
                    return all(isinstance(op, allowed_ops) for op in node.ops)
                if isinstance(node, ast.Constant):
                    return True
                if isinstance(node, ast.Name):
                    return node.id in allowed_names
                if isinstance(node, ast.Subscript):
                    # base and key must be valid; disallow slices
                    if isinstance(node.slice, ast.Slice):
                        return False
                    return _check_node(node.value) and _check_node(node.slice)
                if isinstance(node, ast.Attribute):
                    # Allow target_object.properties only
                    return (
                        isinstance(node.value, ast.Name)
                        and node.value.id == "target_object"
                        and node.attr == "properties"
                    )
                # Disallow calls, lambdas, comprehensions, etc.
                return False

            for r in rules or []:
                expr = r.ruleLogic or ""
                try:
                    tree = ast.parse(expr, mode="eval")
                except SyntaxError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid {kind} rule expression: {expr} ({e})",
                    ) from e
                if not _check_node(tree):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported {kind} rule expression: {expr}",
                    )

        _validate_rules(schema.submissionCriteria, "submissionCriteria")
        _validate_rules(schema.validationRules, "validationRules")

        existing = self.repo.get_action_type_by_api_name(self.service, self.instance, api_name)
        new_version = 1
        if existing:
            existing.is_latest = False
            self.session.add(existing)
            new_version = existing.version + 1

        act = ActionType(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            display_name=schema.displayName,
            description=schema.description,
            target_object_type_api_name=schema.targetObjectType,
            parameters={
                k: v.model_dump(by_alias=True) for k, v in (schema.parameters or {}).items()
            },
            submission_criteria=[
                {"description": r.description, "rule_logic": r.ruleLogic}
                for r in (schema.submissionCriteria or [])
            ],
            validation_rules=[
                {"description": r.description, "rule_logic": r.ruleLogic}
                for r in (schema.validationRules or [])
            ],
            executor_key=schema.executorKey,
            version=new_version,
            is_latest=True,
        )
        self.session.add(act)
        self.session.commit()
        self.session.refresh(act)
        return self._action_type_to_response(act)

    def get_action_type(
        self, api_name: str, *, version: int | None = None
    ) -> ActionTypeReadResponse | None:
        act = self.repo.get_action_type_by_api_name(
            self.service,
            self.instance,
            api_name,
            version=version,
            include_inactive=bool(version is not None),
        )
        if not act:
            return None
        return self._action_type_to_response(act)

    def list_action_types(self, *, include_inactive: bool = False) -> ActionTypeListResponse:
        items = self.repo.list_action_types(
            self.service,
            self.instance,
            include_inactive=include_inactive,
        )
        data = [self._action_type_to_response(a) for a in items]
        return ActionTypeListResponse(data=data)

    # --- QueryType Operations ---

    def upsert_query_type(
        self, api_name: str, schema: QueryTypePutRequest
    ) -> QueryTypeReadResponse:
        existing = self.repo.get_query_type_by_api_name(self.service, self.instance, api_name)

        # Resolve target via aliases (targetApiName preferred)
        target_api = schema.targetApiName or schema.targetObjectType
        if not target_api:
            raise HTTPException(
                status_code=400, detail="targetApiName/targetObjectType is required"
            )

        # Validate target exists (ObjectType or Interface)
        exists_ot = self.repo.get_object_type_by_api_name(self.service, self.instance, target_api)
        exists_itf = None if exists_ot else self.repo.get_interface_type_by_api_name(self.service, self.instance, target_api)  # type: ignore[attr-defined]
        if not (exists_ot or exists_itf):
            raise HTTPException(
                status_code=400,
                detail=f"Target '{target_api}' not found as ObjectType or Interface",
            )

        # Resolve templates from unified query alias or explicit templates
        tpl_where = list(schema.whereTemplate or [])
        tpl_order = list(schema.orderByTemplate or [])
        if schema.query and isinstance(schema.query, dict):
            qobj = dict(schema.query)
            if isinstance(qobj.get("where"), list):
                tpl_where = list(qobj.get("where") or [])
            if isinstance(qobj.get("orderBy"), list):
                tpl_order = list(qobj.get("orderBy") or [])

        new_version = 1
        if existing:
            existing.is_latest = False
            self.session.add(existing)
            new_version = existing.version + 1

        qt = QueryType(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            display_name=schema.displayName,
            description=schema.description,
            target_object_type_api_name=target_api,
            parameters={k: dict(v.model_dump()) for k, v in (schema.parameters or {}).items()},
            where_template=tpl_where,
            order_by_template=tpl_order,
            version=new_version,
            is_latest=True,
        )
        self.session.add(qt)
        self.session.commit()
        self.session.refresh(qt)
        return self._query_type_to_response(qt)

    def get_query_type(
        self, api_name: str, *, version: int | None = None
    ) -> QueryTypeReadResponse | None:
        qt = self.repo.get_query_type_by_api_name(
            self.service,
            self.instance,
            api_name,
            version=version,
            include_inactive=bool(version is not None),
        )
        if not qt:
            return None
        return self._query_type_to_response(qt)

    def list_query_types(self, *, include_inactive: bool = False) -> QueryTypeListResponse:
        items = self.repo.list_query_types(
            self.service,
            self.instance,
            include_inactive=include_inactive,
        )
        data = [self._query_type_to_response(q) for q in items]
        return QueryTypeListResponse(data=data)

    def delete_query_type(self, api_name: str) -> bool:
        return self.repo.delete_query_type(self.service, self.instance, api_name)

    def execute_query_type(
        self,
        query_api_name: str,
        parameters: dict | None = None,
        *,
        limit: int = 100,
        offset: int = 0,
    ):
        params = dict(parameters or {})
        qt = self.repo.get_query_type_by_api_name(self.service, self.instance, query_api_name)
        if not qt:
            raise HTTPException(status_code=404, detail=f"QueryType '{query_api_name}' not found")

        # Validate required parameters
        for p_name, p_def in (qt.parameters or {}).items():
            req = bool(p_def.get("required", True))
            if req and p_name not in params:
                raise HTTPException(status_code=400, detail=f"Missing required parameter: {p_name}")

        # Build WhereCondition list by substituting parameter refs
        # Supports two forms: {"param": name} and string template "{{name}}"
        where: list[WhereCondition] = []

        def _resolve_value(val: Any) -> Any:
            # Dict param reference
            if isinstance(val, dict) and "param" in val:
                return params.get(val.get("param"))
            # String template {{name}}
            if isinstance(val, str) and "{{" in val and "}}" in val:
                # If string equals single template, return typed param
                import re

                m = re.fullmatch(r"\{\{\s*([A-Za-z0-9_\-]+)\s*\}\}", val)
                if m:
                    return params.get(m.group(1))

                # Otherwise do textual substitution
                def repl(match):
                    key = match.group(1).strip()
                    v = params.get(key)
                    return "" if v is None else str(v)

                return re.sub(r"\{\{\s*([A-Za-z0-9_\-]+)\s*\}\}", repl, val)
            return val

        for cond in list(qt.where_template or []):
            prop = cond.get("property")
            op = cond.get("op")
            val = _resolve_value(cond.get("value"))
            where.append(
                WhereCondition.model_validate(
                    {
                        "property": str(prop),
                        "op": str(op or "eq"),
                        "value": val,
                    }
                )
            )

        # Build order by
        order_by: list[OrderBySpec] = []
        for ob in list(qt.order_by_template or []):
            order_by.append(
                OrderBySpec.model_validate(
                    {
                        "property": str(ob.get("property")),
                        "direction": str(ob.get("direction", "asc")),
                    }
                )
            )

        body = ObjectSearchRequest(where=where, orderBy=order_by, limit=limit, offset=offset)
        inst = InstancesService(self.session, service=self.service, instance=self.instance)
        # Try object type first
        ot = self.repo.get_object_type_by_api_name(
            self.service, self.instance, qt.target_object_type_api_name
        )
        if ot:
            return inst.search_objects(qt.target_object_type_api_name, body)

        # Interface target: graph path will be handled in InstancesService; ensure SQL fallback works too
        itf = None
        try:
            itf = self.repo.get_interface_type_by_api_name(self.service, self.instance, qt.target_object_type_api_name)  # type: ignore[attr-defined]
        except Exception:
            itf = None
        if itf and getattr(itf, "object_types", None):
            # If graph path in InstancesService is available, delegate
            try:
                return inst.search_objects(qt.target_object_type_api_name, body)
            except Exception:
                pass
            # SQL fallback union: execute per implementer and merge
            combined = []
            for impl in itf.object_types:
                res = inst.search_objects(impl.api_name, body)
                combined.extend(list(res.data or []))
            # Apply pagination on combined
            start = max(0, int(offset))
            end = start + max(0, int(limit)) if int(limit) > 0 else len(combined)
            return {"data": combined[start:end], "nextPageToken": None}

        # Fallback to empty if target invalid
        return inst.search_objects(qt.target_object_type_api_name, body)

    def delete_action_type(self, api_name: str) -> bool:
        return self.repo.delete_action_type(self.service, self.instance, api_name)

    # --- Control Plane: DataCatalog & ObjectTypeDataSource ---

    def upsert_dataset(
        self,
        api_name: str,
        *,
        source_type: str,
        source_identifier: str,
        display_name: str | None = None,
        schema_definition: dict | None = None,
    ) -> Dataset:
        existing = self.session.exec(select(Dataset).where(Dataset.api_name == api_name)).first()
        if existing:
            ds = existing
            ds.display_name = display_name or ds.display_name
            ds.source_type = source_type
            ds.source_identifier = source_identifier
            ds.schema_definition = dict(schema_definition or ds.schema_definition or {})
        else:
            ds = Dataset(
                service=self.service,
                instance=self.instance,
                api_name=api_name,
                display_name=display_name or api_name,
                source_type=source_type,
                source_identifier=source_identifier,
                schema_definition=dict(schema_definition or {}),
            )
            self.session.add(ds)
        self.session.commit()
        self.session.refresh(ds)
        return ds

    def create_transaction(
        self,
        dataset_api_name: str,
        *,
        transaction_type: TransactionType,
        commit_message: str | None = None,
    ) -> DatasetTransaction:
        ds = self.session.exec(select(Dataset).where(Dataset.api_name == dataset_api_name)).first()
        if not ds:
            raise HTTPException(status_code=400, detail=f"Dataset '{dataset_api_name}' not found")
        tx = DatasetTransaction(
            service=self.service,
            instance=self.instance,
            api_name=f"{dataset_api_name}:{len(ds.transactions)+1}",
            display_name=commit_message or transaction_type.value,
            dataset_rid=ds.rid,
            transaction_type=transaction_type,
            commit_message=commit_message,
        )
        self.session.add(tx)
        self.session.commit()
        self.session.refresh(tx)
        return tx

    def create_branch(
        self,
        dataset_api_name: str,
        *,
        branch_name: str,
        head_transaction_rid: str,
    ) -> DatasetBranch:
        ds = self.session.exec(select(Dataset).where(Dataset.api_name == dataset_api_name)).first()
        if not ds:
            raise HTTPException(status_code=400, detail=f"Dataset '{dataset_api_name}' not found")
        br = DatasetBranch(
            service=self.service,
            instance=self.instance,
            api_name=f"{dataset_api_name}:{branch_name}",
            display_name=branch_name,
            dataset_rid=ds.rid,
            branch_name=branch_name,
            head_transaction_rid=head_transaction_rid,
        )
        self.session.add(br)
        # Optionally set as default if none
        if not ds.default_branch_rid:
            ds.default_branch_rid = br.rid  # will be None until flush, set after
        self.session.commit()
        self.session.refresh(br)
        # ensure dataset.default_branch_rid set
        if not ds.default_branch_rid:
            ds.default_branch_rid = br.rid
            self.session.add(ds)
            self.session.commit()
        return br

    def add_data_source_to_object_type(
        self,
        object_type_api_name: str,
        dataset_api_name: str,
        *,
        property_mappings: dict[str, str] | None = None,
    ) -> ObjectTypeDataSource:
        ot = self.repo.get_object_type_by_api_name(
            self.service, self.instance, object_type_api_name
        )
        if not ot:
            raise HTTPException(
                status_code=400, detail=f"ObjectType '{object_type_api_name}' not found"
            )
        ds = self.session.exec(select(Dataset).where(Dataset.api_name == dataset_api_name)).first()
        if not ds:
            raise HTTPException(status_code=400, detail=f"Dataset '{dataset_api_name}' not found")
        link = ObjectTypeDataSource(
            service=self.service,
            instance=self.instance,
            api_name=f"{object_type_api_name}__{dataset_api_name}",
            display_name=f"{object_type_api_name} ← {dataset_api_name}",
            object_type_rid=ot.rid,
            dataset_rid=ds.rid,
            property_mappings=property_mappings or None,
        )
        self.session.add(link)
        self.session.commit()
        self.session.refresh(link)
        return link

    # --- Helper Methods: Model → DTO Conversion ---

    def _object_type_to_response(self, object_type: ObjectType) -> ObjectTypeReadResponse:
        """
        Converte ObjectType (modelo de DB) para ObjectTypeReadResponse (DTO).

        Args:
            object_type: Modelo de DB

        Returns:
            DTO de resposta
        """
        # Construir dicionário de propriedades
        properties: dict[str, PropertyDefinition] = {}
        for prop_type in object_type.property_types:
            properties[prop_type.api_name] = PropertyDefinition.model_validate(
                {
                    "dataType": str(prop_type.data_type),
                    "displayName": prop_type.display_name or prop_type.api_name,
                    "description": prop_type.description,
                    "required": prop_type.required,
                    "qualityChecks": list(getattr(prop_type, "quality_checks", []) or []),
                }
            )

        implements = [it.api_name for it in getattr(object_type, "interfaces", []) or []]
        return ObjectTypeReadResponse(
            apiName=object_type.api_name,
            rid=object_type.rid,
            version=object_type.version,
            isLatest=object_type.is_latest,
            displayName=object_type.display_name or object_type.api_name,
            description=object_type.description,
            primaryKey=object_type.primary_key_field,
            properties=properties,
            implements=implements,
        )

    # --- InterfaceType Operations ---

    def upsert_interface_type(
        self,
        api_name: str,
        schema: InterfacePutRequest,
    ) -> InterfaceReadResponse:
        existing = self.repo.get_interface_type_by_api_name(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
        )

        new_version = 1
        if existing:
            existing.is_latest = False
            self.session.add(existing)
            new_version = existing.version + 1

        itf = InterfaceType(
            service=self.service,
            instance=self.instance,
            api_name=api_name,
            display_name=schema.displayName,
            description=schema.description,
            properties=dict(schema.properties or {}),
            version=new_version,
            is_latest=True,
        )
        self.session.add(itf)
        self.session.commit()
        self.session.refresh(itf)
        return InterfaceReadResponse(
            apiName=itf.api_name,
            rid=itf.rid,
            version=itf.version,
            isLatest=itf.is_latest,
            displayName=itf.display_name or itf.api_name,
            description=itf.description,
            properties=dict(itf.properties or {}),
        )

    def get_interface_type(
        self, api_name: str, *, version: int | None = None
    ) -> InterfaceReadResponse | None:
        itf = self.repo.get_interface_type_by_api_name(
            self.service,
            self.instance,
            api_name,
            version=version,
            include_inactive=bool(version is not None),
        )
        if not itf:
            return None
        return InterfaceReadResponse(
            apiName=itf.api_name,
            rid=itf.rid,
            version=itf.version,
            isLatest=itf.is_latest,
            displayName=itf.display_name,
            description=itf.description,
            properties=dict(itf.properties or {}),
        )

    def list_interface_types(self, *, include_inactive: bool = False) -> InterfaceListResponse:
        items = self.repo.list_interface_types(
            self.service,
            self.instance,
            include_inactive=include_inactive,
        )
        data: list[InterfaceReadResponse] = []
        for itf in items:
            data.append(
                InterfaceReadResponse(
                    apiName=itf.api_name,
                    rid=itf.rid,
                    version=itf.version,
                    isLatest=itf.is_latest,
                    displayName=itf.display_name or itf.api_name,
                    description=itf.description,
                    properties=dict(itf.properties or {}),
                )
            )
        return InterfaceListResponse(data=data)

    def delete_interface_type(self, api_name: str) -> bool:
        return self.repo.delete_interface_type(self.service, self.instance, api_name)

    def _link_type_to_response(self, link_type: LinkType) -> LinkTypeReadResponse:
        """
        Converte LinkType (modelo de DB) para LinkTypeReadResponse (DTO).

        Args:
            link_type: Modelo de DB

        Returns:
            DTO de resposta
        """
        # Map link property types -> PropertyDefinition dict
        props_dict: dict[str, PropertyDefinition] = {}
        try:
            for p in getattr(link_type, "link_property_types", []) or []:
                props_dict[p.api_name] = PropertyDefinition.model_validate(
                    {
                        "dataType": str(p.data_type),
                        "displayName": p.display_name or p.api_name,
                        "description": p.description,
                        "required": p.required,
                        "qualityChecks": list(getattr(p, "quality_checks", []) or []),
                    }
                )
        except Exception:
            props_dict = {}
        return LinkTypeReadResponse(
            apiName=link_type.api_name,
            rid=link_type.rid,
            version=link_type.version,
            isLatest=link_type.is_latest,
            displayName=link_type.display_name or link_type.api_name,
            cardinality=link_type.cardinality.value,
            fromObjectType=link_type.from_object_type_api_name,
            toObjectType=link_type.to_object_type_api_name,
            inverse=LinkInverseDefinition(
                apiName=link_type.inverse_api_name,
                displayName=link_type.inverse_display_name or link_type.inverse_api_name,
            ),
            description=getattr(link_type, "description", None),
            properties=props_dict,
        )

    def _action_type_to_response(self, act: ActionType) -> ActionTypeReadResponse:
        return ActionTypeReadResponse(
            apiName=act.api_name,
            rid=act.rid,
            version=act.version,
            isLatest=act.is_latest,
            displayName=act.display_name or act.api_name,
            description=getattr(act, "description", None),
            targetObjectType=act.target_object_type_api_name,
            parameters={
                k: ActionParameterDefinition.model_validate(
                    {
                        "dataType": v.get("dataType"),
                        "displayName": v.get("displayName") or k,
                        "description": v.get("description"),
                        "required": v.get("required", True),
                    }
                )
                for k, v in (act.parameters or {}).items()
            },
            submissionCriteria=[
                RuleDefinition(
                    description=r.get("description", ""), ruleLogic=r.get("rule_logic", "")
                )
                for r in (act.submission_criteria or [])
            ],
            validationRules=[
                RuleDefinition(
                    description=r.get("description", ""), ruleLogic=r.get("rule_logic", "")
                )
                for r in (act.validation_rules or [])
            ],
            executorKey=act.executor_key,
        )

    def _query_type_to_response(self, qt: QueryType) -> QueryTypeReadResponse:
        # Compose unified query object
        qobj = {
            "where": list(getattr(qt, "where_template", []) or []),
            "orderBy": list(getattr(qt, "order_by_template", []) or []),
        }
        return QueryTypeReadResponse(
            apiName=qt.api_name,
            rid=qt.rid,
            version=qt.version,
            isLatest=qt.is_latest,
            displayName=qt.display_name or qt.api_name,
            description=getattr(qt, "description", None),
            targetObjectType=qt.target_object_type_api_name,
            targetApiName=qt.target_object_type_api_name,
            parameters={
                k: ActionParameterDefinition.model_validate(
                    {
                        "dataType": v.get("dataType"),
                        "displayName": v.get("displayName") or k,
                        "description": v.get("description"),
                        "required": v.get("required", True),
                    }
                )
                for k, v in (qt.parameters or {}).items()
            },
            whereTemplate=list(getattr(qt, "where_template", []) or []),
            orderByTemplate=list(getattr(qt, "order_by_template", []) or []),
            query=qobj,
        )
