from fastapi.middleware.cors import CORSMiddleware

from app.providers.provider import Provider
from config.config import settings


class AppProvider(Provider):

    def register(self):
        self.app.debug = settings.DEBUG
        self.app.title = settings.NAME

        self.add_global_middleware()

    def add_global_middleware(self):
        """
        注册全局中间件
        """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
