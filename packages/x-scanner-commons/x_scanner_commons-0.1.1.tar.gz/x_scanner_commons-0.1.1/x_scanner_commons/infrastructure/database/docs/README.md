# Database Module Documentation

## 概述

`x_scanner_commons.infrastructure.database` 模块提供了高性能的异步数据库连接管理，支持 SQLAlchemy 2.0+ 和 PostgreSQL，并与 Vault 深度集成实现零配置。

## 核心组件

### AsyncSessionManager
异步数据库会话管理器，负责管理连接池和会话生命周期。

**特性：**
- 连接池管理（可配置大小和溢出）
- 自动连接健康检查（pool_pre_ping）
- 零配置模式（惰性从 Vault 获取凭据，或显式提供 database_url）
- 支持自定义引擎参数
- 惰性初始化：首次使用时创建引擎

### get_async_session (推荐使用)
获取异步数据库会话的依赖注入函数（基于 lifespan + app.state 的 `AsyncSessionManager`）。

**特性：**
- 生命周期托管：由 FastAPI lifespan 注册的 `AsyncSessionManager` 管理连接池
- 自动管理会话生命周期
- 自动提交/回滚事务
- 零配置支持（惰性从 Vault 获取凭据）

### 工具函数（脚本/一次性任务场景）

在非 FastAPI 进程（脚本/一次性任务）中可使用 `utils.py` 提供的底层函数手动创建资源，并自行 `dispose()` 释放：

```python
from x_scanner_commons.infrastructure.database.utils import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

engine = create_async_engine(database_url)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async with Session() as db:
    ...
await engine.dispose()
```

## 使用指南

### 1. 应用集成（lifespan，推荐）

在 FastAPI 应用入口注册 lifespan，自动从 Vault 获取凭据并管理连接池：

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from x_scanner_commons.infrastructure.database.session import (
  create_db_lifespan,
  get_async_session,
)

app = FastAPI(
  lifespan=create_db_lifespan(
    vault_path="x-scanner/prod/main/database",
    pool_size=30,
    echo=False,
    eager_init=True,
  )
)

@app.get("/users")
async def list_users(db: Annotated[AsyncSession, Depends(get_async_session)]):
  result = await db.execute(select(User).limit(100))
  return result.scalars().all()
```

说明：`eager_init=True` 可在启动时预热连接，便于尽早暴露 Vault/网络配置问题；默认惰性初始化。

### 2. 脚本/任务模式

在非 FastAPI 进程中，优先使用惰性的 `AsyncSessionManager` 构建并手动关闭：

```python
import asyncio
from x_scanner_commons.infrastructure.database.session import AsyncSessionManager

async def main():
  manager = AsyncSessionManager(vault_path="x-scanner/prod/main/database")  # 惰性：首次使用时从 Vault 获取 DSN
  async for db in manager.get_session():
    ...
  await manager.close()

asyncio.run(main())
```

## 性能优化

### 连接池与性能

连接池由 `AsyncSessionManager` 统一管理；如需多配置连接，请创建多个 `AsyncSessionManager` 实例并在对应上下文中使用。

## SQLAlchemy 2.0 最佳实践

### 使用新式查询语法

```python
# ✅ 推荐：SQLAlchemy 2.0 Core 风格
from sqlalchemy import select, update, delete

# 查询
result = await db.execute(select(User).where(User.active == True))
users = result.scalars().all()

# 更新
await db.execute(
  update(User)
  .where(User.id == user_id)
  .values(last_login=datetime.now())
)

# 删除
await db.execute(
  delete(User).where(User.id == user_id)
)

# ❌ 避免：旧式 Query API
# users = db.query(User).filter(User.active == True).all()
```

### 事务管理

```python
# 自动事务（推荐）
async def create_user(db: AsyncSession, user_data: dict):
  user = User(**user_data)
  db.add(user)
  await db.commit()
  return user

# 手动事务控制
async def transfer_funds(db: AsyncSession, from_id: int, to_id: int, amount: float):
  async with db.begin():
    from_account = await db.get(Account, from_id)
    to_account = await db.get(Account, to_id)
    from_account.balance -= amount
    to_account.balance += amount
```

### 批量操作

```python
# 批量插入
from sqlalchemy import insert

users_data = [
  {"name": "Alice", "email": "alice@example.com"},
  {"name": "Bob", "email": "bob@example.com"},
]

await db.execute(insert(User), users_data)
await db.commit()

# 批量更新
from sqlalchemy import bindparam

stmt = (
  update(User)
  .where(User.id == bindparam("user_id"))
  .values(status=bindparam("new_status"))
)

await db.execute(stmt, [
  {"user_id": 1, "new_status": "active"},
  {"user_id": 2, "new_status": "inactive"},
])
```

## 故障排除

### 常见问题

1. **连接池耗尽**
   ```python
   # 错误：TimeoutError: QueuePool limit exceeded
   # 解决：增加 pool_size 和 max_overflow
   ```

2. **Vault 连接失败**
   ```python
   # 错误：RuntimeError: Vault not configured
   # 解决：确保设置 VAULT_ADDR 和 VAULT_TOKEN 环境变量
   ```

3. **异步上下文错误**
   ```python
   # 错误：RuntimeError: This event loop is already running
   # 解决：确保使用 async def 和 await
   ```

### 调试技巧

```python
# 启用 SQL 日志
manager = AsyncSessionManager(
  vault_path="x-scanner/prod/main/database",
  echo=True,
)

# 检查连接池状态
from sqlalchemy.pool import QueuePool
if isinstance(engine.pool, QueuePool):
  print(f"Pool size: {engine.pool.size()}")
  print(f"Checked in connections: {engine.pool.checkedin()}")
```

## 核心原则

### 1. YAGNI (You Aren't Gonna Need It)
- 只实现当前需要的功能
- 避免过度设计和预留扩展
- 最好的代码是不存在的代码

### 2. 直接使用，禁止二次封装
- **必须直接导入使用 commons database 模块**
- **严禁创建本地适配器或包装器**
- 统一的接口确保跨项目的一致性

### 3. 异步优先
- **使用 AsyncSession 而非 Session**
- **使用 async def 路由函数**
- **充分利用 SQLAlchemy 2.0 的异步特性**

### 4. SQLAlchemy 2.0 新式语法
- **禁止使用旧式 Query API**（如 `db.query(Model)`）
- **必须使用 SQLAlchemy 2.0 Core 语法**（`select`/`insert`/`update`/`delete`）

## 测试最佳实践

### 测试数据库配置

```python
import pytest
from typing import Annotated
from fastapi import Depends
from x_scanner_commons.infrastructure.database.session import AsyncSessionManager, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def test_db():
  manager = AsyncSessionManager(
    vault_path="x-scanner/test/database",
    echo=True,
  )
  async for session in manager.get_session():
    yield session
    await session.rollback()
  await manager.close()
```

### 集成测试

```python
@pytest.fixture
async def app_with_test_db():
  app = FastAPI(lifespan=create_db_lifespan(vault_path="x-scanner/test/database"))
  yield app
```

## 相关文档

- [最佳实践指南](./BEST_PRACTICES.md) - 使用模式和代码示例
- [迁移指南](./MIGRATION_GUIDE.md) - 从旧版本迁移的详细步骤
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/) - 官方文档
