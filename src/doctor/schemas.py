

from datetime import time

from pydantic import Field, model_validator

from src.models import CustomModel


class DoctorDentalServiceRead(CustomModel):
    id: int
    name: str
    description: str | None = None
    price_from: int
    price_to: int | None = None
    duration_minutes: int
    is_active: bool
    

class DoctorWorkingHourInput(CustomModel):
    weekday: int
    start_time: time
    end_time: time
    
    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time >= self.end_time:
            raise ValueError("Время начала работы должно быть раньше конца")
        
        return self
    
    
class DoctorWorkingHourRead(CustomModel):
    id: int
    weekday: int
    start_time: time
    end_time: time
    is_active: bool


class DoctorCreate(CustomModel):
    name: str = Field(min_length=1, max_length=255)
    specialization: str = Field(min_length=1, max_length=255)
    dental_service_ids: list[int] = []
    working_hours: list[DoctorWorkingHourInput] = []


class DoctorUpdate(CustomModel):
    name: str | None = None
    specialization: str | None = None
    is_active: bool | None = None
    dental_service_ids: list[int] | None = None
    working_hours: list[DoctorWorkingHourInput] | None = None


class DoctorRead(CustomModel):
    id: int
    name: str
    specialization: str
    is_active: bool
    dental_services: list[DoctorDentalServiceRead] = []
    working_hours: list[DoctorWorkingHourRead] = []