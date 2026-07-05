from fastapi import APIRouter, status

from src.dental_service.dependencies import (
    DentalServiceServiceDep,
    ValidDenatlServiceDep,
)
from src.dental_service.schemas import (
    DentalServiceCreate,
    DentalServiceRead,
    DentalServiceUpdate,
)

dental_service_router = APIRouter(
    prefix="/dental_services", tags=["dental_services"]
)


@dental_service_router.get(
    "", response_model=list[DentalServiceRead], summary="Получить все услуги"
)
async def get_all_dental_services(
    dental_service_service: DentalServiceServiceDep,
):
    return await dental_service_service.get_dental_services()


@dental_service_router.get(
    "/{dental_service_id}",
    response_model=DentalServiceRead,
    summary="Получить услугу по id",
)
async def get_dental_service(dental_service: ValidDenatlServiceDep):
    return dental_service


@dental_service_router.post(
    "",
    response_model=DentalServiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать услугу",
)
async def create_dental_service(
    data: DentalServiceCreate, dental_service_service: DentalServiceServiceDep
):
    return await dental_service_service.create_dental_service(data)


@dental_service_router.patch(
    "/{dental_service_id}",
    response_model=DentalServiceRead,
    status_code=status.HTTP_200_OK,
    summary="Обновить даннные услуги",
)
async def update_dental_service(
    dental_service_id: int,
    data: DentalServiceUpdate,
    dental_service_service: DentalServiceServiceDep,
):
    return await dental_service_service.update_dental_service(
        dental_service_id, data
    )


@dental_service_router.delete(
    "/{dental_service_id}", response_model=bool, summary="Удалить услугу по id"
)
async def delete_dental_service(
    dental_service_id: int, dental_service_service: DentalServiceServiceDep
):
    return await dental_service_service.delete_dental_service(dental_service_id)
