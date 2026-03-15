#!/usr/bin/env python3
"""
FastAPI Skeleton Web API 服务启动器
"""

import asyncio
import sys
import os

from fastapi import FastAPI
from config.config import settings
import uvicorn

# 导入应用提供者和日志配置
from app.providers import app_provider, handle_exception, route_provider
from app.providers.logging_provider import configure_web_logging

# 创建全局应用实例
app = FastAPI(
    title=settings.name,
    debug=settings.debug
)


async def create_app():
    """创建并配置应用实例（供测试使用）"""
    # 创建应用实例
    test_app = FastAPI(
        title=settings.name,
        debug=settings.debug
    )

    # 注册提供者
    await app_provider.register(test_app)
    handle_exception.register(test_app)

    # 启动路由提供者
    route_provider.boot(test_app)

    return test_app


def main():
    """启动 Web API 服务"""
    print("=" * 50)
    print("FastAPI Skeleton Web API Service")
    print("=" * 50)
    print(f"Starting server on {settings.server_host}:{settings.server_port}")
    print("Press Ctrl+C to stop")
    print()

    # 配置 Web 服务的日志系统（包括 uvicorn 特殊处理）
    configure_web_logging()

    # 设置应用
    async def init_app():
        # 注册提供者
        await app_provider.register(app)
        handle_exception.register(app)
        # 启动路由提供者
        route_provider.boot(app)

    asyncio.run(init_app())

    # 启动 uvicorn 服务器
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        log_config=None,  # 禁用 uvicorn 默认的日志配置
        access_log=False,
        reload=False
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped gracefully")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
