"""
services/datacatalog_service.py
--------------------------------
Business service for Data Catalog (Datasets, Transactions, Branches).
"""

from __future__ import annotations

from sqlmodel import Session, select

from api.core.auth import UserPrincipal
from datacatalog.models import Dataset, DatasetBranch, DatasetTransaction, TransactionType


class DataCatalogService:
    def __init__(
        self,
        session: Session,
        service: str = "ontology",
        instance: str = "default",
        principal: UserPrincipal | None = None,
    ):
        self.session = session
        self.service = service
        self.instance = instance
        self.principal = principal

    # --- Datasets ---
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

    def get_dataset(self, api_name: str) -> Dataset | None:
        return self.session.exec(select(Dataset).where(Dataset.api_name == api_name)).first()

    def list_datasets(self) -> list[Dataset]:
        return list(self.session.exec(select(Dataset)).all())

    # --- Transactions ---
    def create_transaction(
        self,
        dataset_api_name: str,
        *,
        transaction_type: TransactionType,
        commit_message: str | None = None,
    ) -> DatasetTransaction:
        ds = self.session.exec(select(Dataset).where(Dataset.api_name == dataset_api_name)).first()
        if not ds:
            raise ValueError(f"Dataset '{dataset_api_name}' not found")
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

    # --- Branches ---
    def list_branches(self, dataset_api_name: str) -> list[DatasetBranch]:
        ds = self.session.exec(select(Dataset).where(Dataset.api_name == dataset_api_name)).first()
        if not ds:
            return []
        return list(ds.branches or [])

    def upsert_branch(
        self,
        dataset_api_name: str,
        *,
        branch_name: str,
        head_transaction_rid: str,
    ) -> DatasetBranch:
        ds = self.session.exec(select(Dataset).where(Dataset.api_name == dataset_api_name)).first()
        if not ds:
            raise ValueError(f"Dataset '{dataset_api_name}' not found")
        # Try find existing by dataset and branch_name
        existing = None
        for b in ds.branches or []:
            if b.branch_name == branch_name:
                existing = b
                break
        if existing:
            br = existing
            br.head_transaction_rid = head_transaction_rid
        else:
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
        # set as default if none
        self.session.commit()
        self.session.refresh(br)
        if not ds.default_branch_rid:
            ds.default_branch_rid = br.rid
            self.session.add(ds)
            self.session.commit()
        return br

    # --- Delete Dataset (and dependents) ---
    def delete_dataset(self, api_name: str) -> bool:
        ds = self.session.exec(select(Dataset).where(Dataset.api_name == api_name)).first()
        if not ds:
            return False
        # Delete branches
        for br in list(ds.branches or []):
            self.session.delete(br)
        # Delete transactions
        for tx in list(ds.transactions or []):
            self.session.delete(tx)
        # Clear default branch to avoid FK issues
        ds.default_branch_rid = None
        self.session.add(ds)
        self.session.commit()
        # Delete dataset
        self.session.delete(ds)
        self.session.commit()
        return True
