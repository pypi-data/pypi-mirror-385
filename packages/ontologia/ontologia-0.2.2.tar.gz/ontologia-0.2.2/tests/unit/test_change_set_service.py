from datetime import UTC, datetime

from sqlmodel import select

from api.services.change_set_service import ChangeSetService
from api.v2.schemas.change_sets import ChangeSetApproveRequest, ChangeSetCreateRequest
from datacatalog.models import Dataset, DatasetBranch, DatasetTransaction, TransactionType


def test_change_set_create_and_approve(session) -> None:
    service = ChangeSetService(session, service="ontology", instance="default", principal=None)

    request = ChangeSetCreateRequest(
        name="Scenario Alpha",
        targetObjectType="contract",
        description="Scenario test",
        changes=[{"op": "upsert", "pk": "c1"}],
    )

    change_set = service.create_change_set(request)
    assert change_set.status == "pending"
    assert change_set.base_branch == "draft"

    dataset = session.get(Dataset, change_set.dataset_rid)
    assert dataset is not None
    assert dataset.source_type == "change_set"

    transactions = session.exec(
        select(DatasetTransaction).where(DatasetTransaction.dataset_rid == dataset.rid)
    ).all()
    assert transactions
    assert transactions[0].transaction_type == TransactionType.SNAPSHOT

    branches = session.exec(
        select(DatasetBranch).where(DatasetBranch.dataset_rid == dataset.rid)
    ).all()
    assert branches
    assert branches[0].branch_name == "draft"

    listed = service.list_change_sets()
    assert listed and listed[0].rid == change_set.rid

    approve = ChangeSetApproveRequest(approvedBy="qa_tester", commitMessage="Looks good")
    approved = service.approve_change_set(change_set.rid, approve)
    assert approved.status == "approved"
    assert approved.approved_at is not None
    assert approved.payload.get("approvedBy") == "qa_tester"
    assert "approvalTransactionRid" in approved.payload
    assert approved.approved_at is not None
    assert approved.approved_at.tzinfo is not None
    assert approved.approved_at <= datetime.now(UTC)
