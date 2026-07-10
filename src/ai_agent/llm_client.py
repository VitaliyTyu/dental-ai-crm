

import json
from typing import TypeVar

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from src.config import settings

T = TypeVar("T", bound=BaseModel)


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
        response = await self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            temperature=0.1,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": response_model.model_json_schema(),
                },
            },
        )
        
        content = response.choices[0].message.content
        
        if not content:
            raise ValueError("Empty structured response from LLM")
        
        return response_model.model_validate(json.loads(content))
    
    async def text(self, messages: list[ChatCompletionMessageParam]) -> str:
        response = await self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            temperature=0.3,
        )
        
        return response.choices[0].message.content or ""