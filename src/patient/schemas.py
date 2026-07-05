from pydantic import Field

from src.models import CustomModel


class PatientCreate(CustomModel):
    phone: str = Field(min_length=5, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    notes: str | None = None


class PatientUpdate(CustomModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    notes: str | None = None


class PatientRead(CustomModel):
    id: int
    phone: str
    name: str
    notes: str | None = None
