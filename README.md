这是一个开箱即用的FastAPI脚手架，集成了ORM模型、JWT认证、日志系统、异常处理、路由注册、系统配置、调度任务等常用的模块。

## 设计思想

- 层级结构清晰
- 简洁优雅
- 易于扩展
- 开箱即用

## 项目结构

```
/kaxiluo/fastapi-skeleton/
|-- app
|   |-- commands                                ----- 放置一些命令行
|   |   `-- __init__.py
|   |-- exceptions                              ----- 自定义的异常类
|   |   |-- __init__.py
|   |   `-- exception.py
|   |-- http                                    ----- http目录
|   |   |-- api                                 ----- api控制器目录
|   |   |   |-- __init__.py
|   |   |   |-- auth.py                         ----- 登录认证api的控制器
|   |   |   |-- demo.py
|   |   |   `-- users.py
|   |   |-- middleware                          ----- 放置自定义中间件
|   |   |   `-- __init__.py
|   |   |-- __init__.py
|   |   `-- deps.py                             ----- 依赖
|   |-- jobs                                    ----- 调度任务
|   |   |-- __init__.py
|   |   `-- demo_job.py
|   |-- models                                  ----- 模型目录
|   |   |-- __init__.py
|   |   |-- base_model.py                       ----- 定义模型的基类
|   |   `-- user.py
|   |-- providers                               ----- 核心服务提供者
|   |   |-- __init__.py
|   |   |-- app_provider.py                     ----- 注册应用的全局事件、中间件等
|   |   |-- database.py                         ----- 数据库连接
|   |   |-- handle_exception.py                 ----- 异常处理器
|   |   |-- logging_provider.py                 ----- 集成loguru日志系统
|   |   `-- route_provider.py                   ----- 注册路由文件routes/*
|   |-- schemas                                 ----- 数据模型，负责请求和响应资源数据的定义和格式转换
|   |   |-- __init__.py
|   |   `-- user.py
|   |-- services                                ----- 服务层，业务逻辑层
|   |   |-- auth                                ----- 认证相关服务
|   |   |   |-- __init__.py
|   |   |   |-- grant.py                        ----- 认证核心类
|   |   |   |-- hashing.py
|   |   |   |-- jwt_helper.py
|   |   |   |-- oauth2_schema.py
|   |   |   `-- random_code_verifier.py
|   |   `-- __init__.py
|   |-- support                                 ----- 公共方法
|   |   |-- __init__.py
|   |   `-- helper.py
|   `-- __init__.py
|-- bootstrap                                   ----- 启动项
|   |-- __init__.py
|   |-- application.py                          ----- 创建app实例
|   `-- scheduler.py                            ----- 创建调度器实例
|-- config                                      ----- 配置目录
|   |-- auth.py                                 ----- 认证-JWT配置
|   |-- config.py                               ----- app配置
|   |-- database.py                             ----- 数据库配置
|   `-- logging.py                              ----- 日志配置
|-- database
|   `-- migrations                              ----- 初始化SQL
|       `-- 2022_09_07_create_users_table.sql
|-- routes                                      ----- 路由目录
|   |-- __init__.py
|   `-- api.py                                  ----- api路由
|-- storage
|   `-- logs                                    ----- 日志目录
|-- README.md
|-- main.py                                     ----- app/api启动入口
|-- requirements.txt
`-- scheduler.py                                ----- 调度任务启动入口
```

## 集成的模块

- 日志系统

集成 `loguru`，一个优雅、简洁的日志库

- 异常处理

定义认证异常类，注册 `Exception Handler`

- 路由注册

路由集中注册，按模块划分为不同的文件，代码层次结构清晰

- 系统配置

基于 `pydantic.BaseSettings`，使用 `.env` 文件设置环境变量。配置文件按功能模块划分，默认定义了app基础配置、数据库配置、日志配置、认证配置

- 数据库 ORM模型

基于 `peewee`，一个轻量级的Python ORM框架

- 中间件

默认注册了全局CORS中间件

- JWT认证

默认提供了账号密码和手机号验证码两种认证方式。框架易于扩展新的认证方式。

测试登录认证请先执行初始化的SQL：`fastapi-skeleton/database/migrations/*.sql`

注：验证码的存储和校验方法请自行实现

- 调度任务

基于 `APScheduler` 调度任务框架

注：定时任务与api是分开启动的

## 运行

1. 执行初始化SQL：`/database/migrations/2022_09_07_create_users_table.sql`

2. API：`main.py`

3. 调度器： `scheduler.py`

## 参考

[FastAPI官方中文文档](https://fastapi.tiangolo.com/zh/)

FastAPI作者的全栈项目脚手架 [full-stack-fastapi-postgresql](https://github.com/tiangolo/full-stack-fastapi-postgresql)

代码结构组织风格参考 [Laravel框架](https://github.com/laravel/laravel)
