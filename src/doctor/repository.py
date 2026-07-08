from collections.abc import Mapping
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.dental_service.models import DentalService
from src.doctor.models import Doctor, DoctorWorkingHour, doctor_dental_service


class DoctorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, doctor_id: int) -> Doctor | None:
        result = await self.db.execute(
            select(Doctor)
            .options(
                selectinload(Doctor.dental_services),
                selectinload(Doctor.working_hours),
            )
            .where(Doctor.id == doctor_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Doctor]:
        result = await self.db.execute(
            select(Doctor)
            .options(
                selectinload(Doctor.dental_services),
                selectinload(Doctor.working_hours),
            )
            .order_by(Doctor.id)
        )
        return list(result.scalars().all())

    async def get_active(self) -> list[Doctor]:
        result = await self.db.execute(
            select(Doctor)
            .options(
                selectinload(Doctor.dental_services),
                selectinload(Doctor.working_hours),
            )
            .where(Doctor.is_active.is_(True))
            .order_by(Doctor.id)
        )

        return list(result.scalars().all())

    async def create(self, doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        await self.db.flush()
        return doctor

    async def update(
        self,
        doctor: Doctor,
        data: Mapping[str, Any],
        dental_services: list[DentalService] | None,
        working_hours: list[DoctorWorkingHour] | None,
    ) -> Doctor:
        for field, value in data.items():
            setattr(doctor, field, value)

        if dental_services is not None:
            doctor.dental_services = dental_services

        if working_hours is not None:
            doctor.working_hours = working_hours

        await self.db.flush()
        await self.db.refresh(
            doctor, attribute_names=["dental_services", "working_hours"]
        )

        return doctor

    async def can_privide_service(self, doctor_id: int, dental_service_id: int):
        result = await self.db.execute(
            select(doctor_dental_service).where(
                doctor_dental_service.c.doctor_id == doctor_id,
                doctor_dental_service.c.dental_service_id == dental_service_id,
            )
        )

        return result.first() is not None

    async def get_doctors_by_service_id(
        self, dental_service_id: int
    ) -> list[Doctor]:
        result = await self.db.execute(
            select(Doctor)
            .options(
                selectinload(Doctor.dental_services),
                selectinload(Doctor.working_hours),
            )
            .where(
                Doctor.is_active.is_(True),
                Doctor.dental_services.any(id=dental_service_id),
            )
        )

        return list(result.scalars().all())

    async def get_working_hours_for_date(
        self, doctor_id: int, target_date: date
    ) -> list[DoctorWorkingHour]:
        result = await self.db.execute(
            select(DoctorWorkingHour).where(
                DoctorWorkingHour.doctor_id == doctor_id,
                DoctorWorkingHour.weekday == target_date.weekday(),
                DoctorWorkingHour.is_active.is_(True),
            )
        )

        return list(result.scalars().all())

    async def delete(self, doctor: Doctor):
        await self.db.delete(doctor)
        await self.db.flush()
