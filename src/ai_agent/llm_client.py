

import json
import logging
from typing import Any, TypeVar

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from src.config import settings

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger("ai_agent.llm")


def make_strict_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Adapt a Pydantic schema to OpenAI's strict structured-output format."""
    schema.pop("default", None)

    if schema.get("type") == "object" and "properties" in schema:
        schema["required"] = list(schema["properties"])
        schema["additionalProperties"] = False

    for value in schema.values():
        if isinstance(value, dict):
            make_strict_json_schema(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    make_strict_json_schema(item)

    return schema


class OpenRouterClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Dental AI CRM",
            },
        )
        
    async def structured(
        self,
        messages: list[ChatCompletionMessageParam],
        response_model: type[T],
    ) -> T:
        schema = make_strict_json_schema(response_model.model_json_schema())
        # self._log_request(
        #     method="structured",
        #     messages=messages,
        #     temperature=0.1,
        #     response_model=response_model.__name__,
        # )

        response = await self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            temperature=0.1,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": schema,
                },
            },
        )
        
        content = response.choices[0].message.content
        # self._log_response(
        #     method="structured",
        #     content=content,
        #     response_model=response_model.__name__,
        # )
        
        if not content:
            raise ValueError("Empty structured response from LLM")
        
        return response_model.model_validate(json.loads(content))
    
    async def text(self, messages: list[ChatCompletionMessageParam]) -> str:
        response = await self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            temperature=0.3,
        )
        content = response.choices[0].message.content or ""
        return content

    @staticmethod
    def _log_request(
        method: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float,
        response_model: str | None = None,
    ) -> None:
        data: dict[str, Any] = {
            "method": method,
            "model": settings.openrouter_model,
            "temperature": temperature,
            "messages": messages,
        }
        if response_model:
            data["response_model"] = response_model

        logger.info("llm_request", extra={"event": "llm_request", "data": data})

    @staticmethod
    def _log_response(
        method: str,
        content: str | None,
        response_model: str | None = None,
    ) -> None:
        data: dict[str, Any] = {
            "method": method,
            "model": settings.openrouter_model,
            "content": content,
        }
        if response_model:
            data["response_model"] = response_model

        logger.info("llm_response", extra={"event": "llm_response", "data": data})
