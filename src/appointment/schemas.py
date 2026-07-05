

from datetime import datetime

from src.appointment.models import AppointmentStatus
from src.models import CustomModel


class CreateAppointment(CustomModel):
    patient_id: int
    doctor_id: int
    dental_service_id: int
    start_time: datetime
    end_time: datetime
    comment: str | None = None


class AppointmentMove(CustomModel):
    new_strart_time: datetime


class ReadAppointment(CustomModel):
    id: int
    patient_id: int
    doctor_id: int
    dental_service_id: int
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    comment: str | None = None