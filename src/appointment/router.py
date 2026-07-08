from datetime import datetime

from fastapi import APIRouter, status

from src.appointment.dependencies import AppointmentServiceDep
from src.appointment.schemas import (
    AppointmentCreate,
    AppointmentMove,
    AppointmentRead,
    AppointmentSlotRead,
)

appointment_router = APIRouter(prefix="/appointments", tags=["appointments"])


@appointment_router.post(
    "/",
    response_model=AppointmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать встречу",
)
async def book_appointment(
    data: AppointmentCreate, appointment_service: AppointmentServiceDep
):
    return await appointment_service.book_appointment(data)


@appointment_router.patch(
    "/{appointment_id}/move",
    response_model=AppointmentRead,
    summary="Перенести встречу",
)
async def move_appointment(
    appointment_id: int,
    data: AppointmentMove,
    appointment_service: AppointmentServiceDep,
):
    return await appointment_service.move_appointment(appointment_id, data)


@appointment_router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentRead,
    summary="Отменить встречу",
)
async def cancel_appointment(
    appointment_id: int,
    appointment_service: AppointmentServiceDep,
):
    return await appointment_service.cancel_appointment(appointment_id)


@appointment_router.get(
    "/patient/{patient_id}/active",
    response_model=list[AppointmentRead],
    summary="Назначенные встречи пациента",
)
async def get_patient_active_appointments(
    patient_id: int, appointment_service: AppointmentServiceDep
):
    return await appointment_service.get_patient_active_appointments(patient_id)


@appointment_router.get(
    "/free-slots",
    response_model=list[AppointmentSlotRead],
    summary="Свободные слоты для записи",
)
async def get_free_slots(
    dental_service_id: int,
    target_date: datetime,
    appointment_service: AppointmentServiceDep,
):
    return await appointment_service.get_free_slots(
        dental_service_id, target_date
    )
