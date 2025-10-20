"""add metamodel versioning columns and constraints

Revision ID: 3d47cf7fa5eb
Revises: d0b63df993c6
Create Date: 2025-02-14 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from ontologia.domain.metamodels.migrations.migration_task import MigrationTask

# revision identifiers, used by Alembic.
revision: str = "3d47cf7fa5eb"
down_revision: str | Sequence[str] | None = "d0b63df993c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    MigrationTask.__table__.create(bind=bind, checkfirst=True)
    op.create_foreign_key(
        "fk_migrationtask_resource_rid",
        "migrationtask",
        "resource",
        ["rid"],
        ["rid"],
    )
    op.create_index(
        "ix_migrationtask_object_type_api_name",
        "migrationtask",
        ["object_type_api_name"],
        unique=False,
    )
    op.create_index("ix_migrationtask_status", "migrationtask", ["status"], unique=False)

    op.add_column(
        "objecttype",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "objecttype",
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_objecttype_version", "objecttype", ["version"], unique=False)
    op.create_index("ix_objecttype_is_latest", "objecttype", ["is_latest"], unique=False)

    op.add_column(
        "linktype",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "linktype",
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.drop_constraint("uq_linktype_complete", "linktype", type_="unique")
    op.drop_constraint("uq_linktype_inverse_api_name", "linktype", type_="unique")
    op.create_unique_constraint(
        "uq_linktype_complete_versioned",
        "linktype",
        [
            "from_object_type_api_name",
            "to_object_type_api_name",
            "api_name",
            "version",
        ],
    )
    op.create_unique_constraint(
        "uq_linktype_inverse_api_name_versioned",
        "linktype",
        ["inverse_api_name", "version"],
    )
    op.create_index("ix_linktype_version", "linktype", ["version"], unique=False)
    op.create_index("ix_linktype_is_latest", "linktype", ["is_latest"], unique=False)

    op.add_column(
        "interfacetype",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "interfacetype",
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_unique_constraint(
        "uq_interfacetype_api_version",
        "interfacetype",
        ["api_name", "version"],
    )
    op.create_index("ix_interfacetype_version", "interfacetype", ["version"], unique=False)
    op.create_index("ix_interfacetype_is_latest", "interfacetype", ["is_latest"], unique=False)

    op.add_column(
        "actiontype",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "actiontype",
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.drop_constraint("actiontype_executor_key_key", "actiontype", type_="unique")
    op.create_unique_constraint(
        "uq_actiontype_executor_version",
        "actiontype",
        ["executor_key", "version"],
    )
    op.create_unique_constraint(
        "uq_actiontype_api_version",
        "actiontype",
        ["api_name", "version"],
    )
    op.create_index("ix_actiontype_version", "actiontype", ["version"], unique=False)
    op.create_index("ix_actiontype_is_latest", "actiontype", ["is_latest"], unique=False)

    op.add_column(
        "querytype",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "querytype",
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_unique_constraint(
        "uq_querytype_api_version",
        "querytype",
        ["api_name", "version"],
    )
    op.create_index("ix_querytype_version", "querytype", ["version"], unique=False)
    op.create_index("ix_querytype_is_latest", "querytype", ["is_latest"], unique=False)

    # clear server defaults to avoid affecting future inserts
    op.alter_column("objecttype", "version", server_default=None)
    op.alter_column("objecttype", "is_latest", server_default=None)
    op.alter_column("linktype", "version", server_default=None)
    op.alter_column("linktype", "is_latest", server_default=None)
    op.alter_column("interfacetype", "version", server_default=None)
    op.alter_column("interfacetype", "is_latest", server_default=None)
    op.alter_column("actiontype", "version", server_default=None)
    op.alter_column("actiontype", "is_latest", server_default=None)
    op.alter_column("querytype", "version", server_default=None)
    op.alter_column("querytype", "is_latest", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_migrationtask_status", table_name="migrationtask")
    op.drop_index(
        "ix_migrationtask_object_type_api_name",
        table_name="migrationtask",
    )
    op.drop_constraint("fk_migrationtask_resource_rid", "migrationtask", type_="foreignkey")
    op.drop_table("migrationtask")

    op.alter_column("querytype", "is_latest", server_default=sa.true())
    op.alter_column("querytype", "version", server_default="1")
    op.alter_column("actiontype", "is_latest", server_default=sa.true())
    op.alter_column("actiontype", "version", server_default="1")
    op.alter_column("interfacetype", "is_latest", server_default=sa.true())
    op.alter_column("interfacetype", "version", server_default="1")
    op.alter_column("linktype", "is_latest", server_default=sa.true())
    op.alter_column("linktype", "version", server_default="1")
    op.alter_column("objecttype", "is_latest", server_default=sa.true())
    op.alter_column("objecttype", "version", server_default="1")

    op.drop_index("ix_querytype_is_latest", table_name="querytype")
    op.drop_index("ix_querytype_version", table_name="querytype")
    op.drop_constraint("uq_querytype_api_version", "querytype", type_="unique")
    op.drop_column("querytype", "is_latest")
    op.drop_column("querytype", "version")

    op.drop_index("ix_actiontype_is_latest", table_name="actiontype")
    op.drop_index("ix_actiontype_version", table_name="actiontype")
    op.drop_constraint("uq_actiontype_api_version", "actiontype", type_="unique")
    op.drop_constraint("uq_actiontype_executor_version", "actiontype", type_="unique")
    op.create_unique_constraint(
        "actiontype_executor_key_key",
        "actiontype",
        ["executor_key"],
    )
    op.drop_column("actiontype", "is_latest")
    op.drop_column("actiontype", "version")

    op.drop_index("ix_interfacetype_is_latest", table_name="interfacetype")
    op.drop_index("ix_interfacetype_version", table_name="interfacetype")
    op.drop_constraint("uq_interfacetype_api_version", "interfacetype", type_="unique")
    op.drop_column("interfacetype", "is_latest")
    op.drop_column("interfacetype", "version")

    op.drop_index("ix_linktype_is_latest", table_name="linktype")
    op.drop_index("ix_linktype_version", table_name="linktype")
    op.drop_constraint("uq_linktype_inverse_api_name_versioned", "linktype", type_="unique")
    op.drop_constraint("uq_linktype_complete_versioned", "linktype", type_="unique")
    op.create_unique_constraint(
        "uq_linktype_inverse_api_name",
        "linktype",
        ["inverse_api_name"],
    )
    op.create_unique_constraint(
        "uq_linktype_complete",
        "linktype",
        ["from_object_type_api_name", "to_object_type_api_name", "api_name"],
    )
    op.drop_column("linktype", "is_latest")
    op.drop_column("linktype", "version")

    op.drop_index("ix_objecttype_is_latest", table_name="objecttype")
    op.drop_index("ix_objecttype_version", table_name="objecttype")
    op.drop_column("objecttype", "is_latest")
    op.drop_column("objecttype", "version")
