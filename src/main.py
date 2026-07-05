from typing import Any

from fastapi import FastAPI

import src.models_registry  # noqa: F401
from src.appointment.router import appointment_router
from src.config import Environment, settings
from src.dental_service.router import dental_service_router
from src.doctor.router import doctor_router
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
    app.include_router(doctor_router)
    app.include_router(dental_service_router)
    app.include_router(appointment_router)

    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
