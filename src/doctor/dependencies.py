from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.doctor.models import Doctor
from src.doctor.service import DoctorService

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_doctor_service(db: SessionDep) -> DoctorService:
    return DoctorService(db)


DoctorServiceDep = Annotated[DoctorService, Depends(get_doctor_service)]


async def get_valid_doctor(
    doctor_id: int, doctor_service: DoctorServiceDep
) -> Doctor:
    return await doctor_service.get_doctor_by_id(doctor_id)


ValidDoctorDep = Annotated[Doctor, Depends(get_valid_doctor)]
