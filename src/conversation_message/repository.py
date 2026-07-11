import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conversation_message.models import ConversationMessage


class ConversationMessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_message_id(
        self,
        message_id: uuid.UUID,
    ) -> ConversationMessage | None:
        return await self.db.get(ConversationMessage, message_id)

    async def get_by_session_and_sequence_no(
        self,
        session_id: uuid.UUID,
        sequence_no: int,
    ) -> ConversationMessage | None:
        result = await self.db.execute(
            select(ConversationMessage).where(
                ConversationMessage.session_id == session_id,
                ConversationMessage.sequence_no == sequence_no,
            )
        )
        return result.scalar_one_or_none()

    async def get_for_session(
        self,
        session_id: uuid.UUID,
    ) -> list[ConversationMessage]:
        result = await self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.sequence_no)
        )
        return list(result.scalars().all())

    async def create(
        self,
        message: ConversationMessage,
    ) -> ConversationMessage:
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message
