

from enum import StrEnum

from pydantic import Field

from src.models import CustomModel


class AgentChatRequest(CustomModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    phone: str | None = None
    

class AgentChatResponse(CustomModel):
    session_id: str
    answer: str
    
    
class UserIntent(StrEnum):
    BOOK_APPOINTMENT = "book_appointment"
    ASK_PRICE = "ask_price"
    CONSULTATION = "consultation"
    TRANSFER_TO_OPERATOR = "transfer_to_operator"
    UNKNOWN = "unknown"
    
    
class ExtractedUserData(CustomModel):
    intent: UserIntent = UserIntent.UNKNOWN

    patient_name: str | None = None
    phone: str | None = None

    service_query: str | None = None
    target_date: str | None = Field(
        default=None,
        description="Дата в формате YYYY-MM-DD",
    )

    selected_slot_index: int | None = Field(
        default=None,
        description="Номер выбранного слота: 1, 2 или 3",
    )

    confirmation: bool | None = Field(
        default=None,
        description="true если пациент явно подтвердил запись",
    )

    wants_operator: bool = False