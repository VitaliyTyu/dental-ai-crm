

from pydantic import Field

from src.models import CustomModel


class DoctorDentalServiceRead(CustomModel):
    id: int
    name: str
    description: str | None = None
    price_from: int
    price_to: int | None = None
    duration_minutes: int
    is_active: bool

class DoctorCreate(CustomModel):
    name: str = Field(min_length=1, max_length=255)
    specialization: str = Field(min_length=1, max_length=255)
    dental_service_ids: list[int] = []


class DoctorUpdate(CustomModel):
    name: str | None = None
    specialization: str | None = None
    is_active: bool | None = None
    dental_service_ids: list[int] | None = None


class DoctorRead(CustomModel):
    id: int
    name: str
    specialization: str
    is_active: bool
    dental_services: list[DoctorDentalServiceRead] = []