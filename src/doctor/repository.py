
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.doctor.models import Doctor


class DoctorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, doctor_id: int) -> Doctor | None:
        return await self.db.get(Doctor, doctor_id)

    async def get_all(self) -> list[Doctor]:
        result = await self.db.execute(select(Doctor).order_by(Doctor.id))
        return list(result.scalars().all())

    async def get_active(self) -> list[Doctor]:
        result = await self.db.execute(
            select(Doctor).where(Doctor.is_active.is_(True)).order_by(Doctor.id)
        )
        return list(result.scalars().all())

    async def create(self, doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        await self.db.flush()
        await self.db.refresh(doctor)
        return doctor