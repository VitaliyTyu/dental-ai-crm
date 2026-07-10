import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | event=%(event)s | %(data)s"
)
CHAT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "session_id=%(session_id)s | event=%(event)s | %(data)s"
)


class AgentTraceFormatter(logging.Formatter):
    """Supplies defaults for records emitted by the ai_agent logger."""

    def format(self, record: logging.LogRecord) -> str:
        for field, default in (
            ("session_id", "-"),
            ("event", "-"),
            ("data", {}),
        ):
            if not hasattr(record, field):
                setattr(record, field, default)
        return super().format(record)

    def formatMessage(self, record: logging.LogRecord) -> str:
        if record.name == "ai_agent":
            return CHAT_LOG_FORMAT % record.__dict__
        return LOG_FORMAT % record.__dict__


def configure_ai_agent_logging() -> None:
    """Write AI-agent trace events to console and a rotating local log file."""
    logger = logging.getLogger("ai_agent")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return

    formatter = AgentTraceFormatter(LOG_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    log_path = Path("logs") / "ai_agent.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
