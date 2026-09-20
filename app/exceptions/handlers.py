from http import HTTPStatus

import structlog
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.exceptions.errors import AppError
from config.settings import get_app_settings

logger = structlog.get_logger(__name__)


def _problem(
    status_code: int,
    type_: str,
    title: str,
    detail=None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    content: dict = {"type": type_, "title": title}
    if detail is not None:
        content["detail"] = detail
    return JSONResponse(status_code=status_code, content=content, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return _problem(exc.status_code, exc.code, exc.title, exc.detail, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _problem(
            422, "validation_error", "Unprocessable Entity", jsonable_encoder(exc.errors())
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        try:
            title = HTTPStatus(exc.status_code).phrase
        except ValueError:  # 非标准状态码没有 phrase
            title = ""
        return _problem(exc.status_code, "http_error", title, exc.detail, headers=exc.headers)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", error=str(exc))
        if get_app_settings().is_production:
            return _problem(500, "internal_error", "Internal Server Error")
        return _problem(500, "internal_error", "Internal Server Error", str(exc))
