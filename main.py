from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.exceptions.handlers import register_exception_handlers
from config.settings import (
    API_V1_PREFIX,
    CORS_ALLOW_CREDENTIALS,
    CORS_ORIGINS,
    get_app_settings,
    validate_runtime_safety,
)
from routes.api import api_router


def create_app() -> FastAPI:
    validate_runtime_safety()
    settings = get_app_settings()
    configure_logging()
    app = FastAPI(title=settings.name, debug=settings.debug, lifespan=lifespan)

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=API_V1_PREFIX)
    return app


app = create_app()
