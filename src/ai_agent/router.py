


from fastapi import APIRouter

from src.ai_agent.dependencies import BookingAgentServiceDep
from src.ai_agent.schemas import AgentChatRequest, AgentChatResponse

ai_agent_router = APIRouter(prefix="/ai-agent", tags=["ai-agent"])


@ai_agent_router.post(
    "/booking/chat",
    response_model=AgentChatResponse,
    summary="Текстовый AI-агент для записи пациента"
)
async def booking_chat(
    data: AgentChatRequest,
    agent_service: BookingAgentServiceDep
):
    return await agent_service.chat(
        session_id=data.session_id,
        message=data.message,
        phone=data.phone
    )
