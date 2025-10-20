from __future__ import annotations

from dataclasses import dataclass

import pytest
from hypothesis import given
from hypothesis import strategies as st

from api.services.actions_service import ActionsService
from ontologia.domain.metamodels.instances.dtos import ObjectInstanceDTO


@dataclass
class RuleCase:
    expr: str
    params: dict[str, object]
    target: ObjectInstanceDTO
    context: dict[str, object]


def _build_target(data: dict[str, object]) -> ObjectInstanceDTO:
    return ObjectInstanceDTO(
        object_type_api_name="employee",
        object_type_rid="rid",
        pk_value="pk",
        data=data,
    )


@st.composite
def rule_cases(draw) -> RuleCase:
    status = draw(st.sampled_from(["ACTIVE", "INACTIVE", "PENDING"]))
    dept = draw(st.sampled_from(["ENG", "OPS", "FINANCE"]))
    count = draw(st.integers(min_value=0, max_value=500))
    threshold = draw(st.integers(min_value=0, max_value=500))
    flag = draw(st.booleans())
    role = draw(st.sampled_from(["admin", "manager", "user"]))
    context_role = draw(st.sampled_from(["admin", "manager", "user"]))

    params = {"threshold": threshold, "flag": flag, "role": role}
    target_data = {"status": status, "dept": dept, "count": count}
    context = {"user": {"role": context_role}}

    clauses: list[str] = []
    clause_pool = [
        f"target_object['properties']['status'] == {status!r}",
        f"target_object['properties']['dept'] == {dept!r}",
        "target_object['properties']['count'] >= params['threshold']",
        "params['flag'] == True" if flag else "params['flag'] == False",
        "context['user']['role'] == params['role']",
        f"context['user']['role'] == {context_role!r}",
    ]

    size = draw(st.integers(min_value=1, max_value=3))
    indices = draw(
        st.lists(
            st.integers(min_value=0, max_value=len(clause_pool) - 1),
            unique=True,
            min_size=size,
            max_size=size,
        )
    )
    for idx in indices:
        clauses.append(clause_pool[idx])

    expr = clauses[0]
    for clause in clauses[1:]:
        op = draw(st.sampled_from([" and ", " or "]))
        expr = f"({expr}){op}({clause})"

    if draw(st.booleans()):
        expr = f"not ({expr})"

    return RuleCase(expr=expr, params=params, target=_build_target(target_data), context=context)


@given(rule_cases())
def test_safe_rule_eval_matches_python_eval(case: RuleCase):
    svc = ActionsService.__new__(ActionsService)
    expected_env = {
        "params": dict(case.params),
        "context": dict(case.context),
        "target_object": {
            "properties": dict(case.target.data),
            "pkValue": case.target.pk_value,
            "objectType": case.target.object_type_api_name,
        },
    }
    try:
        expected = bool(eval(case.expr, {}, expected_env))  # noqa: S307 - controlled inputs
    except Exception:
        expected = False

    actual = svc._safe_rule_eval(case.expr, case.target, case.params, case.context)
    assert actual == expected


@pytest.mark.parametrize(
    "expr",
    [
        "__import__('os').system('echo blocked')",
        "(lambda x: x)(1)",
        "target_object['properties'].get('status')",
        "params['threshold'] + 1",
        "(x for x in [1,2,3])",
    ],
)
def test_safe_rule_eval_rejects_disallowed_constructs(expr: str):
    svc = ActionsService.__new__(ActionsService)
    target = _build_target({"status": "ACTIVE"})
    result = svc._safe_rule_eval(expr, target, {"threshold": 10}, {"user": {"role": "admin"}})
    assert result is False
