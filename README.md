# FastAPI Skeleton

FastAPI 异步骨架：MySQL + Redis + APScheduler，SQLAlchemy 2.0 异步 ORM、pydantic-settings
配置、RFC7807 风格错误契约、structlog 结构化日志、Alembic 迁移、unit/integration 双层测试。

要求：Python 3.13+ / [uv](https://docs.astral.sh/uv/) / MySQL 5.7+ / Redis

## 快速开始

```bash
uv sync
cp .env.example .env        # 填 DB/Redis/AUTH_JWT_SECRET
make upgrade                # alembic 建库（种子用户 fake_user1/2，密码 123456）
make dev                    # uv run uvicorn main:app --reload
```

## 常用命令

| 命令 | 作用 |
|---|---|
| `make install` / `make dev` | 安装依赖 / 本地起服务 |
| `make test` | unit 测试（默认排除 integration） |
| `make test-integration` | integration 测试（需 `.env.test`，见 `.env.test.example`） |
| `make lint` / `make format` | ruff + import-linter / 格式化 |
| `make migrate m="msg"` / `make upgrade` | 生成迁移 / 执行迁移 |
| `uv run python scheduler.py` | 启动调度器 |

## 目录结构

```
├── main.py / scheduler.py     # Web / 调度器入口
├── alembic/                   # 数据库迁移
├── config/                    # pydantic-settings 配置 + 结构常量
├── routes/                    # 路由聚合
├── app/
│   ├── core/                  # 基础设施：db/redis、lifespan、日志、中间件
│   ├── http/                  # 入口层：deps（事务边界）+ API 路由
│   ├── jobs/                  # 定时任务（显式注册表）
│   ├── services/              # 业务逻辑
│   ├── repositories/          # 仓储
│   ├── models/                # SQLAlchemy 模型
│   ├── schemas/               # 响应模型（datetime 统一时区格式化）
│   ├── exceptions/            # AppError 体系 + 全局处理器
│   └── utils/
└── tests/{unit,integration}/
```

## 分层契约

`app.http / app.jobs` > `app.services` > `app.repositories` > `app.models`，由 import-linter
强制（`make lint`）；`app.core` / `app.exceptions` / `app.utils` 为叶子模块，禁止依赖业务层。

**事务边界只在入口层**：HTTP 请求由 `get_db_session` 统一 commit/rollback，Job 自管
session；service / repository 永不 commit。

## 错误契约

错误响应统一 `{"type", "title", "detail"}`（RFC7807 风格），业务代码抛 `AppError` 子类；
FastAPI 参数校验 422 的 `detail` 为错误数组；生产环境 500 不泄露内部 detail。

## 认证

| 端点 | 说明 |
|---|---|
| `POST /api/v1/auth/token` | 用户名 + 密码 |
| `POST /api/v1/auth/cellphone/token` | 手机号 + 验证码（通过即自动注册） |
| `POST /api/v1/auth/cellphone/verification_code` | 发码（限流：60s 间隔 + 每日上限） |

万能验证码仅 `APP_ENV ∈ {local, testing}` 且 `AUTH_DEBUG_VERIFICATION_CODE` 非空时生效。
