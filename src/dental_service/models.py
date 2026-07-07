from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.doctor.models import doctor_dental_service
from src.models import Base


class DentalService(Base):
    __tablename__ = "dental_service"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_from: Mapped[int] = mapped_column(Integer)
    price_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(default=True)

    appointments = relationship("Appointment", back_populates="dental_service")

    doctors = relationship(
        "Doctor",
        secondary=doctor_dental_service,
        back_populates="dental_services",
    )
