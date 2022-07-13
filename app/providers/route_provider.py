from app.providers.provider import Provider
from routes.api import api_router


class RouteProvider(Provider):

    def boot(self):
        # 注册api路由[routes/api.py]
        self.app.include_router(api_router, prefix="/api")

        # 打印路由
        if self.app.debug:
            for route in self.app.routes:
                print({'path': route.path, 'name': route.name, 'methods': route.methods})
