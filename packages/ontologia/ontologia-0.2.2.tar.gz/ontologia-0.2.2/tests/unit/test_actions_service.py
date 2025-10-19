from fastapi import HTTPException
from sqlmodel import SQLModel

from api.services.actions_service import ActionsService
from api.services.metamodel_service import MetamodelService
from api.v2.schemas.instances import ObjectUpsertRequest
from api.v2.schemas.metamodel import ObjectTypePutRequest, PropertyDefinition
from ontologia.domain.metamodels.types.action_type import ActionType


def _mk_expense_ot(service: MetamodelService):
    req = ObjectTypePutRequest(
        displayName="Expense",
        description=None,
        primaryKey="id",
        properties={
            "id": PropertyDefinition(dataType="string", displayName="ID", required=True),
            "status": PropertyDefinition(dataType="string", displayName="Status", required=False),
        },
    )
    service.upsert_object_type("expense", req)


def _seed_expense(session, status: str):
    isvc = ActionsService(session, service="ontology", instance="default").instances
    isvc.upsert_object("expense", "e1", ObjectUpsertRequest(properties={"status": status}))


def _mk_action(session) -> ActionType:
    # ensure table exists for the in-memory session engine
    SQLModel.metadata.create_all(session.get_bind())
    act = ActionType(
        service="ontology",
        instance="default",
        api_name="approve_expense",
        display_name="Approve Expense",
        description="Approve expense when pending",
        target_object_type_api_name="expense",
        parameters={"message": {"dataType": "string", "displayName": "Message", "required": True}},
        submission_criteria=[
            {
                "description": "Only when pending",
                "rule_logic": "target_object['properties']['status'] == 'PENDING'",
            }
        ],
        validation_rules=[],
        executor_key="system.log_message",
    )
    session.add(act)
    session.commit()
    session.refresh(act)
    return act


def test_actions_service_discovery_and_execute(session):
    mm = MetamodelService(session, service="ontology", instance="default")
    _mk_expense_ot(mm)

    # seed draft expense
    _seed_expense(session, status="DRAFT")

    # create action type
    _mk_action(session)

    svc = ActionsService(session, service="ontology", instance="default")

    # not available while DRAFT
    lst = svc.list_available_actions("expense", "e1")
    assert lst == []

    # change to PENDING
    _seed_expense(session, status="PENDING")
    lst2 = svc.list_available_actions("expense", "e1")
    assert [a.api_name for a in lst2] == ["approve_expense"]

    # execute with required params
    res = svc.execute_action("expense", "e1", "approve_expense", {"message": "ok"})
    assert res.get("status") == "success"
    assert res.get("message") == "ok"

    # missing param -> 400
    import pytest

    with pytest.raises(HTTPException) as exc:
        svc.execute_action("expense", "e1", "approve_expense", {})
    assert exc.value.status_code == 400
