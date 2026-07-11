import logging
from typing import Any

logger = logging.getLogger("ai_agent")


class AgentTrace:
    def __init__(self, session_id: str):
        self.session_id = session_id

    def log(self, event: str, data: dict[str, Any] | None = None) -> None:
        logger.info(
            "agent_event",
            extra={
                "session_id": self.session_id,
                "event": event,
                "data": data or {},
            },
        )
