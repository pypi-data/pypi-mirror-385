# Database 模块最佳实践指南

## 概述

`x_scanner_commons.infrastructure.database` 模块提供了统一的数据库连接管理接口，支持 SQLAlchemy 2.0+ 异步操作，并与 Vault 模块深度集成实现零配置连接。本文档描述了使用该模块的最佳实践。

## 核心原则

核心原则请参考 [README.md - 核心原则](./README.md#核心原则) 章节。

## 使用指南

基本用法和零配置集成请参考 [README.md - 使用指南](./README.md#使用指南) 章节。


## 使用最佳实践

### 1. SQLAlchemy 2.0 语法要求

SQLAlchemy 2.0 语法要求请参考 [README.md - 核心原则](./README.md#核心原则) 章节。

### 2. 事务管理

**使用 `get_async_session` 时，事务会自动管理（commit/rollback）。**

```python
# get_async_session 自动处理事务
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@router.post("/items")
async def create_item(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    data: ItemCreate
):
    stmt = insert(Item).values(**data.dict())
    await db.execute(stmt)
    # 自动 commit 或 rollback 的处理由 get_async_session 完成
```



## 服务器集成

FastAPI 应用集成方式请参考 [README.md - 应用集成（lifespan）](./README.md#1-应用集成lifespan-推荐) 章节。

### 2. 路由参数迁移（重要）

**不推荐**：
- 使用同步的 `Session` 类型
- 使用旧式 Query API（`db.query(Model)`）
- 从本地模块导入数据库会话函数

**推荐做法**：

```python
# 推荐：使用异步会话并采用 Annotated 依赖注入
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, Query
from x_scanner_commons.infrastructure.database.session import get_async_session


@router.get("/items")
async def list_items(
        db: Annotated[AsyncSession, Depends(get_async_session)],
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=1000)] = 10,
):
    stmt = select(Item).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
```


## 测试最佳实践

测试配置和示例请参考 [README.md - 测试最佳实践](./README.md#测试最佳实践) 章节。

## 性能优化

连接池由 FastAPI lifespan 中注册于 `app.state.db_manager` 的 `AsyncSessionManager` 统一管理，避免重复创建；不再依赖缓存装饰器。

更多性能优化建议请参考 [README.md - 性能优化](./README.md#性能优化) 章节。

## 常见错误

常见错误和解决方案请参考 [README.md - 常见问题](./README.md#常见问题) 章节。


## 总结


记住核心原则：
- **直接使用 commons database，禁止二次封装**
- **优先使用 AsyncSession 和 SQLAlchemy 2.0 语法**
- **充分利用 Vault 集成实现零配置**