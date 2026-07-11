import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.models import Base


class ConversationMessageRole(enum.StrEnum):
    patient = "patient"
    assistant = "assistant"
    system = "system"


class ConversationMessage(Base):
    __tablename__ = "conversation_message"
    __table_args__ = (
        UniqueConstraint("session_id", "sequence_no"),
    )

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("call_session.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence_no: Mapped[int] = mapped_column(Integer)
    role: Mapped[ConversationMessageRole] = mapped_column(
        Enum(
            ConversationMessageRole,
            name="conversation_message_role",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        )
    )
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    session = relationship("CallSession", back_populates="messages")
