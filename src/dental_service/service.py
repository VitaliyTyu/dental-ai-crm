from sqlalchemy.ext.asyncio import AsyncSession

from src.dental_service.exceptions import DentalServiceNotFoundException
from src.dental_service.models import DentalService
from src.dental_service.repository import DentalServiceRepository
from src.dental_service.schemas import DentalServiceCreate, DentalServiceUpdate


class DentalServiceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dental_service_repository = DentalServiceRepository(db)

    async def get_dental_service_by_id(
        self, dental_service_id: int
    ) -> DentalService:
        dental_service = await self.dental_service_repository.get_by_id(
            dental_service_id
        )
        if dental_service is None:
            raise DentalServiceNotFoundException()
        return dental_service

    async def get_dental_services(self) -> list[DentalService]:
        return await self.dental_service_repository.get_all()

    async def create_dental_service(
        self, data: DentalServiceCreate
    ) -> DentalService:
        dental_service = DentalService(**data.model_dump())
        dental_service = await self.dental_service_repository.create(
            dental_service
        )
        await self.db.commit()
        return dental_service

    async def update_dental_service(
        self, dental_service_id: int, data: DentalServiceUpdate
    ) -> DentalService:
        dental_service = await self.get_dental_service_by_id(dental_service_id)
        update_data = data.model_dump(exclude_unset=True)
        dental_service = await self.dental_service_repository.update(
            dental_service, update_data
        )
        await self.db.commit()
        return dental_service

    async def delete_dental_service(self, dental_service_id) -> bool:
        dental_service = await self.get_dental_service_by_id(dental_service_id)
        await self.dental_service_repository.delete(dental_service)
        await self.db.commit()
        return True
