from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dental_service.models import DentalService


class DentalServiceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, service_id: int) -> DentalService | None:
        return await self.db.get(DentalService, service_id)

    async def get_by_name(self, name: str) -> DentalService | None:
        result = await self.db.execute(
            select(DentalService).where(DentalService.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[DentalService]:
        result = await self.db.execute(
            select(DentalService).order_by(DentalService.id)
        )
        return list(result.scalars().all())

    async def create(self, service: DentalService) -> DentalService:
        self.db.add(service)
        await self.db.flush()
        await self.db.refresh(service)
        return service

    async def update(
        self, dental_service: DentalService, data: Mapping[str, Any]
    ) -> DentalService:
        for field, value in data.items():
            setattr(dental_service, field, value)
        await self.db.flush()
        await self.db.refresh(dental_service)
        return dental_service

    async def delete(self, dental_service: DentalService) -> None:
        await self.db.delete(dental_service)
        await self.db.flush()
