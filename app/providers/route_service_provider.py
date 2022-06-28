from app.providers.service_provider import ServiceProvider
from routes.api import api_router


class RouteServiceProvider(ServiceProvider):

    def boot(self):
        # 注册api路由[routes/api.py]
        self.app.include_router(api_router, prefix="/api")

        # 打印路由
        if self.app.debug:
            for route in self.app.routes:
                print({'path': route.path, 'name': route.name, 'methods': route.methods})
