

from pydantic import Field

from src.models import CustomModel


class DoctorCreate(CustomModel):
    name: str = Field(min_length=1, max_length=255)
    specialization: str = Field(min_length=1, max_length=255)


class DoctorUpdate(CustomModel):
    name: str | None = None
    specialization: str | None = None
    is_active: bool | None = None


class DoctorRead(CustomModel):
    id: int
    name: str
    specialization: str
    is_active: bool