
from pydantic import Field

from src.models import CustomModel


class DentalServiceCreate(CustomModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price_from: int
    price_to: int | None = None
    duration_minutes: int


class DentalServiceUpdate(CustomModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price_from: int | None = None
    price_to: int | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None


class DentalServiceRead(CustomModel):
    id: int
    name: str
    description: str | None = None
    price_from: int
    price_to: int | None = None
    duration_minutes: int
    is_active: bool
