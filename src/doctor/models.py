from datetime import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

doctor_dental_service = Table(
    "doctor_dental_servie",
    Base.metadata,
    Column(
        "doctor_id", ForeignKey("doctor.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "dental_service_id",
        ForeignKey("dental_service.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Doctor(Base):
    __tablename__ = "doctor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    specialization: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    appointments = relationship("Appointment", back_populates="doctor")

    dental_services = relationship(
        "DentalService", secondary=doctor_dental_service, back_populates="doctors"
    )
    working_hours = relationship(
        "DoctorWorkingHour", back_populates="doctor", cascade="all, delete-orphan"
    )
    

class DoctorWorkingHour(Base):
    __tablename__ = "doctor_working_hour"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.id", ondelete="CASCADE")
    )

    weekday: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    doctor = relationship("Doctor", back_populates="working_hours")
