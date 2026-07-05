from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dental_service.models import DentalService
from src.dental_service.service import DentalServiceService

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_dental_service_service(db: SessionDep) -> DentalServiceService:
    return DentalServiceService(db)


DentalServiceServiceDep = Annotated[
    DentalServiceService, Depends(get_dental_service_service)
]


async def get_valid_dental_service(
    dental_serivce_id: int, dental_serivce_service: DentalServiceServiceDep
) -> DentalService:
    return await dental_serivce_service.get_dental_service_by_id(
        dental_serivce_id
    )


ValidDenatlServiceDep = Annotated[
    DentalService, Depends(get_valid_dental_service)
]
