import logging
from fastapi.exception_handlers import request_validation_exception_handler, http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.exceptions.exception import AuthenticationError, AuthorizationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request

logger = logging.getLogger(__name__)


def register(app):

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, e: AuthenticationError):
        """
        认证异常处理
        """
        return JSONResponse(status_code=401, content={"message": e.message})

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, e: AuthorizationError):
        """
        权限异常处理
        """
        return JSONResponse(status_code=403, content={"message": e.message})

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc):
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc):
        return await request_validation_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        全局异常处理器 - 捕获所有未处理的异常
        """
        # 记录异常日志
        logger.exception(f"Unhandled exception: {exc}")

        # 在开发模式下返回详细错误信息
        from config.config import settings
        if settings.debug:
            return JSONResponse(
                status_code=500,
                content={
                    "message": "Internal Server Error",
                    "detail": str(exc),
                    "type": type(exc).__name__
                }
            )

        # 生产环境返回通用错误信息
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"}
        )
