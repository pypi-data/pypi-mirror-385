"""Business service for change set workflow."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlmodel import Session, select

from api.core.auth import UserPrincipal
from api.services.datacatalog_service import DataCatalogService
from api.v2.schemas.change_sets import ChangeSetApproveRequest, ChangeSetCreateRequest
from datacatalog.models import Dataset, TransactionType
from ontologia.domain.change_sets.models_sql import ChangeSet


class ChangeSetService:
    def __init__(
        self,
        session: Session,
        *,
        service: str = "ontology",
        instance: str = "default",
        principal: UserPrincipal | None = None,
    ) -> None:
        self.session = session
        self.service = service
        self.instance = instance
        self.principal = principal
        self.catalog = DataCatalogService(
            session,
            service=service,
            instance=instance,
            principal=principal,
        )

    # --- Helpers ---
    def _current_user(self) -> str | None:
        return getattr(self.principal, "user_id", None) if self.principal else None

    def _dataset_by_rid(self, rid: str) -> Dataset | None:
        return self.session.get(Dataset, rid)

    # --- Operations ---
    def create_change_set(self, body: ChangeSetCreateRequest) -> ChangeSet:
        dataset_api_name = ChangeSet.generate_api_name(body.name)

        dataset = self.catalog.upsert_dataset(
            dataset_api_name,
            source_type="change_set",
            source_identifier=body.name,
            display_name=f"Change Set {body.name}",
            schema_definition={
                "targetObjectType": body.targetObjectType,
                "changesSchema": "opaque-json",
            },
        )

        tx = self.catalog.create_transaction(
            dataset_api_name,
            transaction_type=TransactionType.SNAPSHOT,
            commit_message=body.description or f"Initialize change set '{body.name}'",
        )

        branch_name = body.baseBranch or "draft"
        branch = self.catalog.upsert_branch(
            dataset_api_name,
            branch_name=branch_name,
            head_transaction_rid=tx.rid,
        )

        change_set = ChangeSet(
            service=self.service,
            instance=self.instance,
            api_name=dataset_api_name,
            display_name=body.name,
            dataset_rid=dataset.rid,
            name=body.name,
            status="pending",
            target_object_type=body.targetObjectType,
            base_branch=branch.branch_name,
            description=body.description,
            created_by=self._current_user(),
            payload={
                "changes": body.changes,
                "initialTransactionRid": tx.rid,
            },
        )
        self.session.add(change_set)
        self.session.commit()
        self.session.refresh(change_set)
        return change_set

    def list_change_sets(self, status_filter: str | None = None) -> list[ChangeSet]:
        stmt = select(ChangeSet)
        if status_filter:
            stmt = stmt.where(ChangeSet.status == status_filter)
        stmt = stmt.order_by(desc(ChangeSet.created_at))
        return list(self.session.exec(stmt).all())

    def get_change_set(self, rid: str) -> ChangeSet | None:
        cs = self.session.get(ChangeSet, rid)
        if not cs:
            return None
        if cs.service != self.service or cs.instance != self.instance:
            return None
        return cs

    def approve_change_set(self, rid: str, body: ChangeSetApproveRequest) -> ChangeSet:
        cs = self.get_change_set(rid)
        if not cs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Change set not found"
            )
        if cs.status == "approved":
            return cs

        dataset = self._dataset_by_rid(cs.dataset_rid)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Associated dataset missing for change set",
            )

        commit_message = body.commitMessage or f"Approve change set '{cs.name}'"
        tx = self.catalog.create_transaction(
            dataset.api_name,
            transaction_type=TransactionType.APPEND,
            commit_message=commit_message,
        )

        branch_name = cs.base_branch or "draft"
        self.catalog.upsert_branch(
            dataset.api_name,
            branch_name=branch_name,
            head_transaction_rid=tx.rid,
        )

        cs.status = "approved"
        cs.approved_at = datetime.now(UTC)
        approver = body.approvedBy or self._current_user()
        if approver:
            cs.payload["approvedBy"] = approver
        cs.payload["approvalTransactionRid"] = tx.rid
        if body.commitMessage:
            cs.payload["approvalMessage"] = body.commitMessage
        self.session.add(cs)
        self.session.commit()
        self.session.refresh(cs)
        if cs.approved_at and cs.approved_at.tzinfo is None:
            cs.approved_at = cs.approved_at.replace(tzinfo=UTC)
        return cs
