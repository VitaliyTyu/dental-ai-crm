import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.call_session.models import CallSession, CallSessionStatus


class CallSessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, session_id: uuid.UUID) -> CallSession | None:
        return await self.db.get(CallSession, session_id)

    async def get_by_asterisk_uniqueid(
        self,
        asterisk_uniqueid: str,
    ) -> CallSession | None:
        result = await self.db.execute(
            select(CallSession).where(
                CallSession.asterisk_uniqueid == asterisk_uniqueid
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_caller_phone(
        self,
        caller_phone: str,
    ) -> list[CallSession]:
        result = await self.db.execute(
            select(CallSession)
            .where(
                CallSession.caller_phone == caller_phone,
                CallSession.status.in_(
                    [CallSessionStatus.starting, CallSessionStatus.active]
                ),
            )
            .order_by(CallSession.started_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, session: CallSession) -> CallSession:
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def update(
        self,
        session: CallSession,
        data: Mapping[str, Any],
    ) -> CallSession:
        for field, value in data.items():
            setattr(session, field, value)

        await self.db.flush()
        await self.db.refresh(session)
        return session
