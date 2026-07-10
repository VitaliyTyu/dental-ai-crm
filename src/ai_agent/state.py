from enum import StrEnum
from typing import Any

from pydantic import Field

from src.models import CustomModel

# TODO: перенести хранение состояния в бд

class BookingStep(StrEnum):
    COLLECTING_SERVICE = "collecting_service"
    COLLECTING_PATIENT_NAME = "collecting_patient_name"
    COLLECTING_PHONE = "collecting_phone"
    COLLECTING_DATE = "collecting_date"
    OFFERING_SLOTS = "offering_slots"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETED = "completed"
    TRANSFERRED_TO_OPERATOR = "transferred_to_operator"


class BookingState(CustomModel):
    session_id: str

    step: BookingStep = BookingStep.COLLECTING_SERVICE

    patient_name: str | None = None
    phone: str | None = None

    dental_service_id: int | None = None
    dental_service_name: str | None = None
    service_query: str | None = None

    target_date: str | None = None

    offered_slots: list[dict[str, Any]] = Field(default_factory=list)
    selected_slot: dict[str, Any] | None = None

    messages_count: int = 0


BOOKING_SESSIONS: dict[str, BookingState] = {}