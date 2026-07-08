from datetime import date, datetime, time

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.appointment.models import Appointment, AppointmentStatus


class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, appointment_id: int) -> Appointment | None:
        return await self.db.get(Appointment, appointment_id)

    async def get_patient_active_appointments(
        self, patient_id: int
    ) -> list[Appointment]:
        result = await self.db.execute(
            select(Appointment)
            .where(
                Appointment.patient_id == patient_id,
                Appointment.status == AppointmentStatus.scheduled,
            )
            .order_by(Appointment.start_time)
        )

        return list(result.scalars().all())

    async def has_doctor_conflict(
        self,
        doctor_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_appointment_id: int | None = None,
    ) -> bool:
        query = select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.scheduled,
            and_(
                Appointment.start_time < end_time,
                Appointment.end_time > start_time,
            ),
        ).limit(1)

        if exclude_appointment_id is not None:
            query = query.where(Appointment.id != exclude_appointment_id)

        result = await self.db.execute(query)

        return result.scalar_one_or_none() is not None

    async def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        await self.db.flush()
        await self.db.refresh(appointment)
        return appointment

    async def get_doctor_appointments_for_date(
        self,
        doctor_id: int,
        target_date: date
    ) -> list[Appointment]:
        day_start = datetime.combine(target_date, time.min)
        day_end = datetime.combine(target_date, time.max)
        
        result = await self.db.execute(
            select(Appointment)
            .where(
                Appointment.doctor_id == doctor_id,
                Appointment.start_time > day_start,
                Appointment.end_time < day_end,
                Appointment.status == AppointmentStatus.scheduled
            )
            .order_by(Appointment.start_time)
        )
        
        return list(result.scalars().all())        