"""
api/v2/routers/analytics.py
---------------------------
Endpoints for analytics (aggregations) over object instances.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from api.core.auth import UserPrincipal, require_role
from api.core.database import get_session
from api.services.analytics_service import AnalyticsService
from api.v2.schemas.search import AggregateRequest, AggregateResponse

router = APIRouter(tags=["Analytics"])


@router.post(
    "/aggregate",
    response_model=AggregateResponse,
    summary="Aggregate over object instances",
    description="Execute COUNT/SUM/AVG with optional groupBy and filters.",
)
def aggregate(
    body: AggregateRequest,
    ontologyApiName: str = Path(..., description="Ontology API name"),
    session: Session = Depends(get_session),
    principal: UserPrincipal = Depends(require_role("viewer")),
) -> AggregateResponse:
    svc = AnalyticsService(
        session, service="ontology", instance=ontologyApiName, principal=principal
    )
    return svc.aggregate(body)
