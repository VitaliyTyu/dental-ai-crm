

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Doctor(Base):
    __tablename__ = "doctor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    specialization: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    appointments = relationship("Appointment", back_populates="doctor")