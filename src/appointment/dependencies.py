from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.appointment.service import AppointmentService
from src.database import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_appointments_service(db: SessionDep) -> AppointmentService:
    return AppointmentService(db)


AppointmentServiceDep = Annotated[
    AppointmentService, Depends(get_appointments_service)
]
