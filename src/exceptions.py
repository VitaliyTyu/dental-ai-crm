from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    status_code = 400
    detail = "Ошибка приложения"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class NotFoundException(AppException):
    status_code = 404
    detail = "Объект не найден"


class ConflictException(AppException):
    status_code = 409
    detail = "Конфликт"


async def app_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if (isinstance(exc, AppException)):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
        
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
