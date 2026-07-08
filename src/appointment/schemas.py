

from datetime import datetime

from src.appointment.models import AppointmentStatus
from src.models import CustomModel


class AppointmentCreate(CustomModel):
    patient_id: int
    doctor_id: int
    dental_service_id: int
    start_time: datetime
    end_time: datetime
    comment: str | None = None


class AppointmentMove(CustomModel):
    new_start_time: datetime
    new_end_time: datetime


class AppointmentRead(CustomModel):
    id: int
    patient_id: int
    doctor_id: int
    dental_service_id: int
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    comment: str | None = None


class AppointmentSlotRead(CustomModel):
    doctor_id: int
    doctor_name: str
    dental_service_id: int
    start_time: datetime
    end_time: datetime