"""
api/v2/schemas/datasets.py
--------------------------
DTOs for Data Catalog API: Datasets, Transactions, Branches.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DatasetPutRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    displayName: str | None = None
    sourceType: str
    sourceIdentifier: str
    schemaDefinition: dict[str, Any] | None = Field(default_factory=dict)


class DatasetReadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    apiName: str
    rid: str
    displayName: str
    sourceType: str
    sourceIdentifier: str
    schemaDefinition: dict[str, Any] = Field(default_factory=dict)
    defaultBranchName: str | None = None


class DatasetListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data: list[DatasetReadResponse] = Field(default_factory=list)
    nextPageToken: str | None = None


class TransactionCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    transactionType: Literal["SNAPSHOT", "APPEND"]
    commitMessage: str | None = None


class TransactionReadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    apiName: str
    rid: str
    datasetApiName: str
    transactionType: str
    commitMessage: str | None = None


class BranchPutRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    headTransactionRid: str


class BranchReadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    apiName: str
    rid: str
    datasetApiName: str
    branchName: str
    headTransactionRid: str


class BranchListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data: list[BranchReadResponse] = Field(default_factory=list)
    nextPageToken: str | None = None
