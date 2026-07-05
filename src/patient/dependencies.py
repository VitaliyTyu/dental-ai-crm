from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.patient.models import Patient
from src.patient.service import PatientService

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_patient_service(db: SessionDep) -> PatientService:
    return PatientService(db)


PatientServiceDep = Annotated[PatientService, Depends(get_patient_service)]


async def get_valid_patient(
    patient_id: int, service: PatientServiceDep
) -> Patient:
    return await service.get_patient_by_id(patient_id)


ValidPatientDep = Annotated[Patient, Depends(get_valid_patient)]
