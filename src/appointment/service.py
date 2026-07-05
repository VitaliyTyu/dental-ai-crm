from sqlalchemy.ext.asyncio import AsyncSession

from src.appointment.models import Appointment, AppointmentStatus
from src.appointment.repository import AppointmentRepository
from src.appointment.schemas import AppointmentCreate, AppointmentMove
from src.dental_service.repository import DentalServiceRepository
from src.doctor.repository import DoctorRepository
from src.exceptions import ConflictException, NotFoundException
from src.patient.repository import PatientRepository


class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.doctor_repository = DoctorRepository(db)
        self.appointment_repository = AppointmentRepository(db)
        self.patient_repository = PatientRepository(db)
        self.dental_service_repository = DentalServiceRepository(db)

    async def book_appointment(self, data: AppointmentCreate) -> Appointment:
        patient = await self.patient_repository.get_by_id(data.patient_id)
        if not patient:
            raise NotFoundException("Пациент не найден")

        doctor = await self.doctor_repository.get_by_id(data.doctor_id)
        if not doctor:
            raise NotFoundException("Доктор не найден")

        dental_service = await self.dental_service_repository.get_by_id(
            data.dental_service_id
        )
        if not dental_service:
            raise NotFoundException("Услуга не найдена")

        has_doctor_conflict = (
            await self.appointment_repository.has_doctor_conflict(
                data.doctor_id,
                data.start_time,
                data.end_time,
            )
        )
        if has_doctor_conflict:
            raise ConflictException("Время для встречи занято")

        appointment = await self.appointment_repository.create(
            Appointment(**data.model_dump())
        )
        await self.db.commit()

        return appointment

    async def move_appointment(
        self, appointment_id: int, data: AppointmentMove
    ) -> Appointment:
        appointment = await self.appointment_repository.get_by_id(appointment_id)

        if not appointment:
            raise NotFoundException("Встреча не найдена")

        if appointment.status is not AppointmentStatus.scheduled:
            raise ConflictException(
                "Только запланированные записи могут быть передвинуты"
            )

        has_conflict = await self.appointment_repository.has_doctor_conflict(
            appointment.doctor_id,
            data.new_start_time,
            data.new_end_time,
            exclude_appointment_id=appointment.id,
        )

        if has_conflict:
            raise ConflictException("Время для встречи занято")

        appointment.start_time = data.new_start_time
        appointment.end_time = data.new_end_time
        await self.db.commit()
        await self.db.refresh(appointment)

        return appointment

    async def cancel_appointment(self, appointment_id: int) -> Appointment:
        appointment = await self.appointment_repository.get_by_id(appointment_id)

        if not appointment:
            raise NotFoundException("Встреча не найдена")

        appointment.status = AppointmentStatus.cancelled
        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment

    async def get_patient_active_appointments(
        self, patient_id: int
    ) -> list[Appointment]:
        patient = await self.patient_repository.get_by_id(patient_id)

        if not patient:
            raise NotFoundException("Пациент не найден")
        
        appointments = (
            await self.appointment_repository.get_patient_active_appointments(
                patient_id
            )
        )
        
        return appointments
