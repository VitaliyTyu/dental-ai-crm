from typing import Any

from fastapi import FastAPI

import src.models_registry
from src.config import Environment, settings
from src.exceptions import AppException, app_exception_handler
from src.patient.router import patient_router


def create_app() -> FastAPI:
    app_kwargs: dict[str, Any] = {
        "title": settings.app_name,
    }

    if settings.environment == Environment.PRODUCTION:
        app_kwargs["openapi_url"] = None

    app = FastAPI(**app_kwargs)

    app.add_exception_handler(AppException, app_exception_handler)
    
    app.include_router(patient_router)

    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
