"""add governance metadata columns to dataset

Revision ID: 8f5b8f7e2c6d
Revises: 3d47cf7fa5eb
Create Date: 2025-02-16 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f5b8f7e2c6d"
down_revision: str | Sequence[str] | None = "3d47cf7fa5eb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "dataset",
        sa.Column("owner_team", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "dataset",
        sa.Column("contact_email", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "dataset",
        sa.Column("update_frequency", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dataset", "update_frequency")
    op.drop_column("dataset", "contact_email")
    op.drop_column("dataset", "owner_team")
