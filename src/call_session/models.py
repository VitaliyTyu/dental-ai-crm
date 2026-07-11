import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Integer, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class CallSessionStatus(enum.StrEnum):
    starting = "starting"
    active = "active"
    ended = "ended"
    failed = "failed"


class CallSession(Base):
    __tablename__ = "call_session"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    asterisk_uniqueid: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
    )
    caller_phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        index=True,
    )
    status: Mapped[CallSessionStatus] = mapped_column(
        Enum(
            CallSessionStatus,
            name="call_session_status",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        default=CallSessionStatus.starting,
        server_default=CallSessionStatus.starting.value,
    )
    state: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    state_version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    hangup_cause: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    messages = relationship(
        "ConversationMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
