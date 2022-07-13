import logging

from fastapi import FastAPI

from app.providers.app_provider import AppProvider
from app.providers.handle_exception import HandleException
from app.providers.logging_provider import LoggingProvider
from app.providers.route_provider import RouteProvider
from app.providers.provider import Provider

providers: list = [
    # Framework Service Providers
    AppProvider,
    LoggingProvider,
    HandleException,
    RouteProvider
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


def resolve_provider(provider, app) -> Provider:
    return provider(app)


def create_instance(module_name, class_name, *args, **kwargs) -> Provider:
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    obj = class_meta(*args, **kwargs)
    return obj
