"""add call sessions and conversation messages

Revision ID: 7c92f39b4a1d
Revises: f3e2510bc01c
Create Date: 2026-07-11 15:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7c92f39b4a1d"
down_revision: str | Sequence[str] | None = "f3e2510bc01c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


call_session_status = postgresql.ENUM(
    "starting",
    "active",
    "ended",
    "failed",
    name="call_session_status",
    create_type=False,
)
conversation_message_role = postgresql.ENUM(
    "patient",
    "assistant",
    "system",
    name="conversation_message_role",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    call_session_status.create(bind, checkfirst=True)
    conversation_message_role.create(bind, checkfirst=True)

    op.create_table(
        "call_session",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("asterisk_uniqueid", sa.String(length=150), nullable=False),
        sa.Column("caller_phone", sa.String(length=32), nullable=True),
        sa.Column(
            "status",
            call_session_status,
            server_default="starting",
            nullable=False,
        ),
        sa.Column(
            "state",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "state_version",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hangup_cause", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("call_session_pkey")),
    )
    op.create_index(
        op.f("call_session_asterisk_uniqueid_idx"),
        "call_session",
        ["asterisk_uniqueid"],
        unique=True,
    )
    op.create_index(
        op.f("call_session_caller_phone_idx"),
        "call_session",
        ["caller_phone"],
        unique=False,
    )

    op.create_table(
        "conversation_message",
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("role", conversation_message_role, nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["call_session.id"],
            name=op.f("conversation_message_session_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "message_id",
            name=op.f("conversation_message_pkey"),
        ),
        sa.UniqueConstraint(
            "session_id",
            "sequence_no",
            name=op.f("conversation_message_session_id_key"),
        ),
    )


def downgrade() -> None:
    op.drop_table("conversation_message")
    op.drop_index(
        op.f("call_session_caller_phone_idx"),
        table_name="call_session",
    )
    op.drop_index(
        op.f("call_session_asterisk_uniqueid_idx"),
        table_name="call_session",
    )
    op.drop_table("call_session")

    bind = op.get_bind()
    conversation_message_role.drop(bind, checkfirst=True)
    call_session_status.drop(bind, checkfirst=True)
