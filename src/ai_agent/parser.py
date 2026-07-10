from datetime import datetime
from zoneinfo import ZoneInfo

from src.ai_agent.llm_client import OpenRouterClient
from src.ai_agent.prompts import EXTRACT_USER_DATA_PROMPT
from src.ai_agent.schemas import ExtractedUserData
from src.ai_agent.state import BookingState
from src.config import settings


class UserMessageParser:
    def __init__(self):
        self.llm = OpenRouterClient()
        
    async def parse(
        self,
        message: str,
        state: BookingState,
    ) -> ExtractedUserData:
        current_datetime = datetime.now(
            ZoneInfo(settings.clinic_timezone)
        ).strftime("%Y-%m-%d %H:%M:%S %Z")
        
        system_prompt = EXTRACT_USER_DATA_PROMPT.format(
            current_datetime=current_datetime,
            state=state,
        )
        
        return await self.llm.structured(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            response_model=ExtractedUserData
        )