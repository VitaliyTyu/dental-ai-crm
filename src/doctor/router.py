from fastapi import APIRouter, status

from src.doctor.dependencies import DoctorServiceDep, ValidDoctorDep
from src.doctor.schemas import DoctorCreate, DoctorRead, DoctorUpdate

doctor_router = APIRouter(prefix="/doctors", tags=["doctors"])


@doctor_router.get(
    "", response_model=list[DoctorRead], summary="Получить всех докоторов"
)
async def get_all_doctors(doctor_service: DoctorServiceDep):
    return await doctor_service.get_doctors()


@doctor_router.get(
    "/active",
    response_model=list[DoctorRead],
    summary="Получить активных докторов",
)
async def get_active_doctors(doctor_service: DoctorServiceDep):
    return await doctor_service.get_active_doctors()


@doctor_router.get(
    "/{doctor_id}", response_model=DoctorRead, summary="Получить доктора по id"
)
async def get_doctor(doctor: ValidDoctorDep):
    return doctor


@doctor_router.post(
    "",
    response_model=DoctorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать доктора",
)
async def create_doctor(data: DoctorCreate, doctor_service: DoctorServiceDep):
    return await doctor_service.create_doctor(data)


@doctor_router.patch(
    "/{doctor_id}",
    response_model=DoctorRead,
    status_code=status.HTTP_200_OK,
    summary="Обновить даннные доктора",
)
async def update_doctor(
    doctor_id: int, data: DoctorUpdate, doctor_service: DoctorServiceDep
):
    return await doctor_service.update_doctor(doctor_id, data)


@doctor_router.delete(
    "/{doctor_id}",
    response_model=bool,
    summary="Удалить доктора по id"
)
async def delete_doctor(doctor_id: int, doctor_service: DoctorServiceDep):
    return await doctor_service.delete_doctor(doctor_id)