from fastapi.exception_handlers import request_validation_exception_handler, http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.exceptions.exception import AuthenticationError, AuthorizationError
from app.providers.service_provider import ServiceProvider
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request


class HandleException(ServiceProvider):

    def register(self):
        app = self.app

        @app.exception_handler(AuthenticationError)
        async def custom_http_exception_handler(request: Request, e: AuthenticationError):
            return JSONResponse(status_code=401, content={"message": e.message})

        @app.exception_handler(AuthorizationError)
        async def custom_http_exception_handler(request: Request, e: AuthorizationError):
            return JSONResponse(status_code=403, content={"message": e.message})

        @app.exception_handler(StarletteHTTPException)
        async def custom_http_exception_handler(request: Request, exc):
            return await http_exception_handler(request, exc)

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc):
            return await request_validation_exception_handler(request, exc)
