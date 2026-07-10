from difflib import SequenceMatcher

from sqlalchemy.ext.asyncio import AsyncSession

from src.dental_service.exceptions import DentalServiceNotFoundException
from src.dental_service.models import DentalService
from src.dental_service.repository import DentalServiceRepository
from src.dental_service.schemas import DentalServiceCreate, DentalServiceUpdate

MIN_SERVICE_NAME_SIMILARITY = 0.55


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

    async def get_dental_service_by_name(
        self, service_name: str
    ) -> DentalService:
        dental_service = await self.dental_service_repository.get_by_name(
            service_name
        )

        if dental_service is None:
            query_name = self._normalize_service_name(service_name)
            dental_services = await self.dental_service_repository.get_all()
            best_match: DentalService | None = None
            best_score = 0.0

            for service in dental_services:
                score = self._service_name_similarity(
                    query_name, self._normalize_service_name(service.name)
                )

                if score > best_score:
                    best_score = score
                    best_match = service

            if best_score >= MIN_SERVICE_NAME_SIMILARITY:
                dental_service = best_match

        if dental_service is None:
            raise DentalServiceNotFoundException()

        return dental_service

    def _normalize_service_name(self, service_name: str) -> str:
        return " ".join(
            service_name.casefold().replace("\u0451", "\u0435").split()
        )

    def _service_name_similarity(self, query: str, service_name: str) -> float:
        if not query or not service_name:
            return 0.0

        if query == service_name:
            return 1.0

        if query in service_name or service_name in query:
            return 0.95

        query_tokens = set(query.split())
        service_tokens = set(service_name.split())
        token_match = len(query_tokens & service_tokens) / len(query_tokens)

        return max(
            token_match,
            SequenceMatcher(None, query, service_name).ratio(),
        )

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
