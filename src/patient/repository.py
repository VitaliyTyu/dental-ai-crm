from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.patient.models import Patient


class PatientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, patient_id: int) -> Patient | None:
        return await self.db.get(Patient, patient_id)

    async def get_by_phone(self, phone: str) -> Patient | None:
        result = await self.db.execute(
            select(Patient).where(Patient.phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Patient]:
        result = await self.db.execute(select(Patient).order_by(Patient.id))
        return list(result.scalars().all())

    async def create(self, patient: Patient) -> Patient:
        self.db.add(patient)
        await self.db.flush()
        await self.db.refresh(patient)
        return patient

    async def update(self, patient: Patient, data: Mapping[str, Any]) -> Patient:
        for field, value in data.items():
            setattr(patient, field, value)
        await self.db.flush()
        await self.db.refresh(patient)
        return patient

    async def delete(self, patient: Patient) -> None:
        await self.db.delete(patient)
