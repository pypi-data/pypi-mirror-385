from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.datacatalog_service import DataCatalogService
from api.v2.schemas.datasets import (
    BranchListResponse,
    BranchPutRequest,
    BranchReadResponse,
    DatasetListResponse,
    DatasetPutRequest,
    DatasetReadResponse,
    TransactionCreateRequest,
    TransactionReadResponse,
)
from datacatalog.models import TransactionType

router = APIRouter(tags=["Datasets"])


def _dataset_to_resp(ds) -> DatasetReadResponse:
    return DatasetReadResponse(
        apiName=ds.api_name,
        rid=ds.rid,
        displayName=ds.display_name,
        sourceType=ds.source_type,
        sourceIdentifier=ds.source_identifier,
        schemaDefinition=dict(ds.schema_definition or {}),
        defaultBranchName=getattr(getattr(ds, "default_branch", None), "branch_name", None),
    )


def _branch_to_resp(dataset_api: str, br) -> BranchReadResponse:
    return BranchReadResponse(
        apiName=br.api_name,
        rid=br.rid,
        datasetApiName=dataset_api,
        branchName=br.branch_name,
        headTransactionRid=br.head_transaction_rid,
    )


def _tx_to_resp(dataset_api: str, tx) -> TransactionReadResponse:
    return TransactionReadResponse(
        apiName=tx.api_name,
        rid=tx.rid,
        datasetApiName=dataset_api,
        transactionType=str(tx.transaction_type),
        commitMessage=tx.commit_message,
    )


@router.get(
    "/datasets",
    response_model=DatasetListResponse,
    summary="List datasets",
)
def list_datasets(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> DatasetListResponse:
    svc = DataCatalogService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    items = svc.list_datasets()
    return DatasetListResponse(data=[_dataset_to_resp(d) for d in items])


@router.get(
    "/datasets/{datasetApiName}",
    response_model=DatasetReadResponse,
    summary="Get dataset by API name",
)
def get_dataset(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    datasetApiName: str = Path(..., description="Dataset API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> DatasetReadResponse:
    svc = DataCatalogService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    ds = svc.get_dataset(datasetApiName)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return _dataset_to_resp(ds)


@router.delete(
    "/datasets/{datasetApiName}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete dataset",
)
def delete_dataset(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    datasetApiName: str = Path(..., description="Dataset API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("admin")),
):
    svc = DataCatalogService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    ok = svc.delete_dataset(datasetApiName)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return None


@router.put(
    "/datasets/{datasetApiName}",
    response_model=DatasetReadResponse,
    summary="Create or update a dataset",
)
def upsert_dataset(
    body: DatasetPutRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    datasetApiName: str = Path(..., description="Dataset API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> DatasetReadResponse:
    svc = DataCatalogService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    ds = svc.upsert_dataset(
        datasetApiName,
        source_type=body.sourceType,
        source_identifier=body.sourceIdentifier,
        display_name=body.displayName,
        schema_definition=dict(body.schemaDefinition or {}),
    )
    return _dataset_to_resp(ds)


@router.post(
    "/datasets/{datasetApiName}/transactions",
    response_model=TransactionReadResponse,
    summary="Create a dataset transaction",
)
def create_transaction(
    body: TransactionCreateRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    datasetApiName: str = Path(..., description="Dataset API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> TransactionReadResponse:
    svc = DataCatalogService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    tx = svc.create_transaction(
        datasetApiName,
        transaction_type=TransactionType(body.transactionType),
        commit_message=body.commitMessage,
    )
    return _tx_to_resp(datasetApiName, tx)


@router.get(
    "/datasets/{datasetApiName}/branches",
    response_model=BranchListResponse,
    summary="List dataset branches",
)
def list_branches(
    ontologyApiName: str = Path(..., description="Ontology API name"),
    datasetApiName: str = Path(..., description="Dataset API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> BranchListResponse:
    svc = DataCatalogService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    items = svc.list_branches(datasetApiName)
    return BranchListResponse(data=[_branch_to_resp(datasetApiName, b) for b in items])


@router.put(
    "/datasets/{datasetApiName}/branches/{branchName}",
    response_model=BranchReadResponse,
    summary="Create or update a dataset branch",
)
def upsert_branch(
    body: BranchPutRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    datasetApiName: str = Path(..., description="Dataset API name"),
    branchName: str = Path(..., description="Branch name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("editor")),
) -> BranchReadResponse:
    svc = DataCatalogService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    br = svc.upsert_branch(
        datasetApiName,
        branch_name=branchName,
        head_transaction_rid=body.headTransactionRid,
    )
    return _branch_to_resp(datasetApiName, br)
