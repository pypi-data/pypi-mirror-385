"""Utility script to mint a long-lived token for the architect agent."""

from __future__ import annotations

import json

from api.core.auth import USERS_DB, create_service_account_token


def main() -> None:
    record = USERS_DB.get("agent-architect-01")
    if record is None:
        raise SystemExit("agent-architect-01 is not configured in USERS_DB")

    token = create_service_account_token(
        subject=record.username,
        roles=list(record.roles),
        tenants=dict(record.tenants),
        audience="service-agent",
    )

    payload = {
        "username": record.username,
        "roles": record.roles,
        "tenants": record.tenants,
        "token": token,
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":  # pragma: no cover - script entrypoint
    main()
