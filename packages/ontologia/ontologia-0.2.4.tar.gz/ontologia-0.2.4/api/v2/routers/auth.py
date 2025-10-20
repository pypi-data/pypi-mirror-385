"""Authentication endpoints (token issuance)."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.core.auth import TokenResponse, authenticate_user, create_access_token
from api.core.docs import ApiError
from api.core.settings import get_settings

router = APIRouter(tags=["Auth"])


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obtain access token",
    description="Exchange a username/password credential pair for a short-lived JWT access token.",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ApiError,
            "description": "Credentials were invalid or the user is disabled.",
        }
    },
)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    settings = get_settings()
    expires = timedelta(minutes=settings.jwt_access_token_ttl_minutes)
    token = create_access_token(
        subject=user.username,
        roles=user.roles,
        tenants=user.tenants,
        expires_delta=expires,
    )
    return TokenResponse(access_token=token)
