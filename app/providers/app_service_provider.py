from app.providers.service_provider import ServiceProvider
from config.config import settings


class AppServiceProvider(ServiceProvider):

    def register(self):
        self.app.debug = settings.DEBUG
        self.app.title = settings.NAME

        if self.app.debug:
            # 记录mysql日志 todo
            pass
