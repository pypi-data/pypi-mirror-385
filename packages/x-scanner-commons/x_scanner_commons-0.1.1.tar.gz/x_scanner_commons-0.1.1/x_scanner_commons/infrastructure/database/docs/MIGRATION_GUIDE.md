# Database 模块迁移指南

## 概述

本文档指导如何将现有项目从自定义数据库实现或同步 SQLAlchemy 迁移到 `x_scanner_commons.infrastructure.database` 统一实现，充分利用 SQLAlchemy 2.0+ 的异步特性。

## 迁移原则

迁移原则请参考 [README.md - 核心原则](./README.md#核心原则) 章节。

## 重要提示：服务器端集成

**在 X-Scanner 服务端，数据库配置应该集中在 `server/app/core/database.py`**，与 Vault 集成获取凭据，为整个应用提供统一的数据库访问接口。

## 迁移步骤

### 步骤 1: 评估现有实现

确认项目是否使用旧的同步数据库实现，需要迁移到 `x_scanner_commons.infrastructure.database`。

### 步骤 2: 安装依赖

```bash
# 使用 Poetry 安装 commons 包的数据库功能
poetry add "x-scanner-commons[database]"

# 或在本地开发环境中使用路径依赖
poetry add --editable ../x-scanner-commons --extras database

# 或直接在 pyproject.toml 中添加
[tool.poetry.dependencies]
x-scanner-commons = {path = "../x-scanner-commons", extras = ["database"], develop = true}

# 更新依赖
poetry update x-scanner-commons
```

### 步骤 3: 更新导入语句

**关键导入替换：**
- 将本地的 `get_db` 替换为 `from x_scanner_commons.infrastructure.database.session import get_async_session`
- 使用 `from x_scanner_commons.infrastructure.database.session import create_db_lifespan` 在应用入口注册生命周期
- 移除所有本地数据库配置代码

### 步骤 4: 迁移数据库配置

**注意：需要移除旧的同步配置，包括 `create_engine`、`sessionmaker`、同步的 `get_db` 函数等。**

#### 推荐配置（使用 lifespan + app.state）

```python
# ✅ 在应用入口注册 lifespan
from fastapi import FastAPI
from x_scanner_commons.infrastructure.database.session import create_db_lifespan

app = FastAPI(
    lifespan=create_db_lifespan(
        vault_path="x-scanner/prod/main/database",
        pool_size=30,
        echo=False,
        eager_init=True,
    )
)

# 路由中直接使用 get_async_session 依赖
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from x_scanner_commons.infrastructure.database.session import get_async_session
from sqlalchemy import select

from typing import Annotated

@app.get("/items")
async def list_items(db: Annotated[AsyncSession, Depends(get_async_session)]):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

> 说明：不再提供 `init_database/close_database` 全局初始化函数；请统一使用 lifespan。

**关键优势：**
- 生命周期明确，资源创建与释放受 FastAPI 管理
- 零配置支持：`AsyncSessionManager.from_vault` 自动从 Vault 获取凭据
- 避免重复创建数据库连接池，提高性能与稳定性

### 步骤 5: 迁移 FastAPI 路由

使用 `x_scanner_commons.infrastructure.database.session` 的 `get_async_session` 替换本地数据库依赖：

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from x_scanner_commons.infrastructure.database.session import get_async_session

@router.get("/items")
async def list_items(db: Annotated[AsyncSession, Depends(get_async_session)]):
    # 使用 SQLAlchemy 2.0 语法
    pass
```

### 步骤 6: 迁移 CRUD 操作

将同步的 CRUD 操作迁移到异步，并使用 SQLAlchemy 2.0 语法。具体 SQLAlchemy 迁移请参考官方文档。

### 步骤 7: 迁移查询语法

SQLAlchemy 2.0 语法要求请参考 [README.md - 核心原则](./README.md#核心原则) 章节。

```python
# 分页示例
    .offset((page - 1) * per_page)\
    .limit(per_page)\
    .all()

# ✅ 新式
page = 1
per_page = 20
stmt = select(Item).offset((page - 1) * per_page).limit(per_page)
result = await db.execute(stmt)
items = result.scalars().all()
```

### 步骤 8: 迁移 Model 定义

```python
# ❌ 旧式 Model
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship("Post", back_populates="author")

# ✅ 新式 Model（SQLAlchemy 2.0）
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, func
from datetime import datetime
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    
    # 关系
    posts: Mapped[List["Post"]] = relationship(back_populates="author")
    
    # 添加有用的方法
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
```

### 步骤 9: 迁移 Alembic 配置

```python
# alembic/env.py

# ❌ 旧配置（同步）
from sqlalchemy import engine_from_config, pool
from alembic import context

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

# ✅ 新配置（异步）
import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()  # 从 Vault 获取
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    
    await connectable.dispose()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())
```

### 步骤 10: 迁移测试代码

测试代码迁移指南请参考 [README.md - 测试最佳实践](./README.md#测试最佳实践) 章节。

**注意：需要移除旧的同步测试代码，包括：**
- 同步的 `create_engine` 和 `sessionmaker`
- 同步的 fixture 和测试函数
- 旧式 Query API 的使用

## 特殊场景处理

### 1. Celery 集成

```python
# tasks.py - Celery 任务中使用异步数据库

import asyncio
from celery import Task
from x_scanner_commons.infrastructure.database.session import AsyncSessionManager

class DatabaseTask(Task):
    """带数据库连接的 Celery 任务基类"""
    _db_manager = None
    
    @property
    def db_manager(self):
        if self._db_manager is None:
            # 惰性：首次使用时从 Vault 获取 DSN
            self._db_manager = AsyncSessionManager(
                vault_path="x-scanner/prod/main/database",
            )
        return self._db_manager

@app.task(base=DatabaseTask)
def process_items(item_ids: list[int]):
    """在 Celery 任务中处理项目"""
    # 在同步上下文中运行异步代码
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(
            _async_process_items(
                process_items.db_manager,
                item_ids
            )
        )
    finally:
        loop.close()

async def _async_process_items(db_manager, item_ids):
    """异步处理逻辑"""
    async for session in db_manager.get_session():
        stmt = select(Item).where(Item.id.in_(item_ids))
        result = await session.execute(stmt)
        items = result.scalars().all()
        
        for item in items:
            # 处理项目
            pass
        
        await session.commit()
        return len(items)
```

### 2. 后台任务

```python
# FastAPI 后台任务
from fastapi import BackgroundTasks

@router.post("/process")
async def trigger_processing(
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_async_session)]
):
    # 获取需要处理的项目
    stmt = select(Item).where(Item.status == "pending")
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    # 添加后台任务
    for item in items:
        background_tasks.add_task(process_item_async, item.id)
    
    return {"message": f"Processing {len(items)} items"}

async def process_item_async(item_id: int):
    """异步后台任务"""
    # 创建新的数据库会话
    manager = AsyncSessionManager(vault_path="x-scanner/prod/main/database")
    async for session in manager.get_session():
        # 处理项目
        stmt = update(Item).where(Item.id == item_id)
        await session.execute(stmt.values(status="processed"))
        await session.commit()
    await manager.close()
```

### 3. 多数据库支持

```python
# 直接使用 AsyncSessionManager 管理不同数据库
from x_scanner_commons.infrastructure.database.session import AsyncSessionManager

# 为不同数据库创建独立的管理器
analytics_manager = AsyncSessionManager(vault_path="x-scanner/main/database/analytics")
primary_manager = AsyncSessionManager(vault_path="x-scanner/main/database/primary")
replica_manager = AsyncSessionManager(vault_path="x-scanner/main/database/replica")

@router.get("/report")
async def get_report():
    # 使用分析数据库
    async for session in analytics_manager.get_session():
        # 查询分析数据
        result = await session.execute(select(Report))
        reports = result.scalars().all()
    
    # 使用主数据库
    async for session in primary_manager.get_session():
        # 查询主数据
        result = await session.execute(select(User))
        users = result.scalars().all()
    
    return {"reports": reports, "users": users}
```

## 常见问题

常见问题和解决方案请参考 [README.md - 常见问题](./README.md#常见问题) 章节。

## 迁移检查清单

- [ ] 安装 `x-scanner-commons[database]` 依赖
- [ ] 将本地 `get_db` 替换为 `get_async_session`
- [ ] 移除所有本地数据库配置代码
- [ ] 使用 SQLAlchemy 2.0 新式语法
- [ ] 配置 Vault 路径

## 总结

迁移到 `x_scanner_commons.infrastructure.database` 的关键点请参考 [README.md - 核心原则](./README.md#核心原则) 章节。

重点提醒：
- **直接使用 `get_async_session`**，已包含 `@alru_cache` 优化
- **充分利用 Vault 集成**实现零配置
