import logging

from fastapi import FastAPI

from app.providers.app_service_provider import AppServiceProvider
from app.providers.logging_service_provider import LoggingServiceProvider
from app.providers.route_service_provider import RouteServiceProvider
from app.providers.service_provider import ServiceProvider

providers: list = [
    # Framework Service Providers
    AppServiceProvider,
    LoggingServiceProvider,
    RouteServiceProvider
]


def create_app() -> FastAPI:
    logging.info("App initializing")

    app = FastAPI()

    register(app)
    boot(app)

    return app


def register(app):
    for provider in providers:
        logging.info(provider.__name__ + ' registering')
        o = resolve_provider(provider, app)
        o.register()


def boot(app):
    for provider in providers:
        logging.info(provider.__name__ + ' booting')
        o = resolve_provider(provider, app)
        o.boot()


def resolve_provider(provider, app) -> ServiceProvider:
    return provider(app)


def create_instance(module_name, class_name, *args, **kwargs) -> ServiceProvider:
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    obj = class_meta(*args, **kwargs)
    return obj
