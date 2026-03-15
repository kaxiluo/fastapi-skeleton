# FastAPI Skeleton

基于 FastAPI + SQLModel + SQLAlchemy 2.0 的异步 API 项目骨架，完全异步化，开箱即用。

## 环境要求

- Python 3.12+
- MySQL 5.7+
- Redis
- uv (Python 包管理器)

## 安装依赖

```bash
# 开发环境
uv sync --frozen --no-install-project

# 生产环境
uv sync --frozen --no-dev --no-install-project
```

## 配置

复制 `config.example.yaml` 为 `config.yaml`，并根据实际环境修改配置：

```bash
cp config.example.yaml config.yaml
```

配置支持环境变量替换，格式：`${VAR_NAME:默认值}`

## 启动服务

### Web API 服务
```bash
uv run main.py
```

### 定时任务调度器
```bash
uv run scheduler.py
```

## 项目结构

```
fastapi-skeleton/
├── main.py                 # Web API 服务启动器
├── scheduler.py            # 定时任务调度器启动器
├── config.yaml             # 配置文件（不提交到版本控制）
├── config.example.yaml     # 配置文件示例
├── pyproject.toml          # uv 依赖配置
├── uv.toml                 # uv 配置
├── app/
│   ├── exceptions/         # 自定义异常
│   ├── http/               # HTTP 层
│   │   ├── api/           # API 路由
│   │   └── deps.py        # 依赖注入
│   ├── jobs/               # 定时任务
│   │   ├── base_job.py    # Job 基类
│   │   ├── job_registry.py# Job 注册器
│   │   └── demo_job.py    # 示例任务
│   ├── models/             # 数据模型（SQLModel）
│   │   ├── base_model.py  # 基础模型
│   │   └── user.py        # 用户模型
│   ├── providers/          # 服务提供者
│   │   ├── app_provider.py # 应用配置
│   │   ├── database.py    # 数据库连接（异步）
│   │   ├── logging_provider.py
│   │   ├── handle_exception.py
│   │   └── route_provider.py
│   ├── schemas/            # Pydantic 模型
│   ├── services/           # 业务逻辑（异步）
│   │   └── auth/          # 认证服务
│   └── utils/              # 工具类
├── config/                 # 配置类
└── routes/                 # 路由聚合
```

## 核心特性

### 异步架构
- 完全异步化的路由、服务、数据库访问
- SQLAlchemy 2.0 + aiomysql
- Redis 异步客户端

### 配置管理
- YAML 配置文件
- 环境变量替换
- 按功能模块划分配置

### 认证系统
- JWT 认证
- 用户名+密码登录
- 手机号+验证码登录

### 日志系统
- 基于标准库 logging
- 时区感知
- 文件轮转
- 分级日志

### 定时任务
- 基于 APScheduler
- 自动发现和注册
- 异步执行

### 中间件
- 全局 CORS 中间件

### 异常处理
- 统一的异常处理器
- 认证异常类

## 设计思想

- 层级结构清晰
- 简洁优雅
- 易于扩展
- 开箱即用

代码结构组织风格参考 [Laravel 框架](https://github.com/laravel/laravel)
