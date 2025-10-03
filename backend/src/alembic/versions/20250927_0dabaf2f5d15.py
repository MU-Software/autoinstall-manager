"""
20250927_214310

Revision ID: 0dabaf2f5d15
Revises:
Create Date: 2025-09-27 21:43:10.808328+09:00
"""

from collections.abc import Sequence

from alembic.op import create_index, create_table, drop_index, drop_table, f
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql.schema import Column, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime, Uuid
from sqlmodel.sql.sqltypes import AutoString

revision: str = "0dabaf2f5d15"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_table(
        "confignode",
        Column("id", Uuid(), nullable=False),
        Column("created_at", DateTime(), server_default=TextClause("now()"), nullable=False),
        Column("updated_at", DateTime(), server_default=TextClause("now()"), server_onupdate=TextClause("now()"), nullable=False),
        Column("name", AutoString(), nullable=False),
        Column("parent_id", Uuid(), nullable=True),
        Column("autoinstall_config", AutoString(), nullable=False),
        ForeignKeyConstraint(["parent_id"], ["confignode.id"], name=f("fk_confignode_parent_id_confignode")),
        PrimaryKeyConstraint("id", name=f("pk_confignode")),
    )
    create_index(f("ix_confignode_id"), "confignode", ["id"], unique=False)
    create_index(f("ix_confignode_name"), "confignode", ["name"], unique=True)

    create_table(
        "device",
        Column("id", Uuid(), nullable=False),
        Column("created_at", DateTime(), server_default=TextClause("now()"), nullable=False),
        Column("updated_at", DateTime(), server_default=TextClause("now()"), server_onupdate=TextClause("now()"), nullable=False),
        Column("name", AutoString(), nullable=False),
        Column("identifier", AutoString(), nullable=False),
        Column("config_node_id", Uuid(), nullable=False),
        ForeignKeyConstraint(["config_node_id"], ["confignode.id"], name=f("fk_device_config_node_id_confignode")),
        PrimaryKeyConstraint("id", name=f("pk_device")),
    )
    create_index(f("ix_device_id"), "device", ["id"], unique=False)
    create_index(f("ix_device_identifier"), "device", ["identifier"], unique=True)
    create_index(f("ix_device_name"), "device", ["name"], unique=True)


def downgrade() -> None:
    drop_index(f("ix_device_name"), table_name="device")
    drop_index(f("ix_device_identifier"), table_name="device")
    drop_index(f("ix_device_id"), table_name="device")
    drop_table("device")
    drop_index(f("ix_confignode_name"), table_name="confignode")
    drop_index(f("ix_confignode_id"), table_name="confignode")
    drop_table("confignode")
