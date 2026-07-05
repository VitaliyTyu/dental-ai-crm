import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class AppointmentStatus(enum.StrEnum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    moved = "moved"


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.id"))
    dental_service_id: Mapped[int] = mapped_column(
        ForeignKey("dental_service.id")
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.scheduled
    )

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    dental_service = relationship("DentalService", back_populates="appointments")
