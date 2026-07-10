from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai_agent.service import BookingAgentService
from src.database import get_db

DbDep = Annotated[AsyncSession, Depends(get_db)]


def get_booking_agent_service(db: DbDep) -> BookingAgentService:
    return BookingAgentService(db)


BookingAgentServiceDep = Annotated[
    BookingAgentService, Depends(get_booking_agent_service)
]
