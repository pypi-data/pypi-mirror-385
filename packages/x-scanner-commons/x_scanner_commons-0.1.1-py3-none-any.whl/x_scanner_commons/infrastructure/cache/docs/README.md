# 缓存模块文档

## 概述

缓存模块提供了一个统一、灵活的缓存解决方案，支持多种后端和多层缓存策略。它基于 aiocache 构建，提供了一个清晰的面向对象的接口，同时保持与 aiocache 设计原则的兼容性。

## 架构

### 核心组件

1.  **Cache** - 提供统一接口的主要缓存类
2.  **CacheInterface** - 定义缓存后端契约的抽象基类
3.  **RedisBackend** - Redis 缓存后端实现
4.  **MemoryBackend** - 内存缓存后端实现

### 设计原则

-   **YAGNI (You Aren't Gonna Need It)**: 只实现被证明是必要的功能
-   **简单性**: 遵循 aiocache 惯例的清晰、直观的 API
-   **灵活性**: 使用功能开关而非复杂的策略模式
-   **性能**: 可选的两层缓存以减少延迟

## 快速入门

### 安装

```bash
pip install x-scanner-commons[cache]
```

这将安装：
-   `aiocache[redis]` - 支持 Redis 的异步缓存库
-   `redis` - Redis 客户端库
-   `hiredis` - 用于提高性能的 C 解析器
-   `mmh3` - 用于键哈希的 MurmurHash3

### 基本用法

#### 推荐使用模式（单例模式）


使用 `alru_cache` 装饰器确保缓存实例的单例模式，这是**推荐的最佳实践**：

```python
# 直接在业务模块中使用，例如 app/modules/user/service.py
from async_lru import alru_cache
from x_scanner_commons.infrastructure.cache import create_cache, Cache  # 直接导入，不二次封装

@alru_cache(maxsize=None)
async def get_user_cache() -> Cache:
    """获取用户缓存单例实例（推荐方式）"""
    return await create_cache(
        namespace="user",
        ttl=3600  # 默认 TTL
        # 不需要 redis_url，自动从 Vault 获取
    )

# 在同一模块中使用
async def get_user(user_id: int):
    cache = await get_user_cache()  # 自动获取单例
    return await cache.get_or_set(
        f"user:{user_id}",
        default=lambda: fetch_user_from_db(user_id),
        ttl=3600
    )
```

#### FastAPI 应用中的最佳实践

在 FastAPI 应用中，可以在启动事件中预热缓存连接：

```python
# app/main.py
from fastapi import FastAPI
from server.app import get_user_cache
from server.app import get_product_cache

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """应用启动时预热缓存连接"""
    # 预热缓存连接（可选）
    await get_user_cache()
    await get_product_cache()
    # 由于使用了 alru_cache，这些连接会被缓存并在后续请求中复用
    print("Cache connections warmed up")


# 在路由中使用
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    cache = await get_user_cache()  # 获取缓存的单例
    return await cache.get_or_set(
        f"user:{user_id}",
        default=lambda: fetch_user_from_db(user_id),
        ttl=3600
    )
```

#### 配置方式

使用 Vault 自动配置：

```python
# 设置环境变量
# export VAULT_ADDR=http://vault.example.com:8200
# export VAULT_TOKEN=your-vault-token

# create_cache 自动从 Vault 获取 Redis 配置
cache = await create_cache(namespace="my_app")

# 存储和检索数据
await cache.set("user:1", {"name": "John", "age": 30})
user = await cache.get("user:1")

# 使用 get_or_set 模式
async def fetch_from_db():
    # 昂贵的数据库操作
    return await db.get_user(1)

user = await cache.get_or_set(
    "user:1",
    default=fetch_from_db,
    ttl=3600
)
```

### 高级功能

#### 多层缓存

启用本地内存缓存作为 L1，Redis 作为 L2：

```python
# 两层缓存：内存 (L1) + Redis (L2)
cache = await create_cache(
    namespace="my_app",
    cache_layers="memory,redis",  # 按优先级排序：快速层在前
    ttls="60,3600"               # 对应的 TTL：内存 60秒，Redis 3600秒
)

# 单层 Redis 缓存（默认）
cache = await create_cache(
    namespace="my_app",
    cache_layers="redis",  # 或省略此参数，默认为 "redis"
    ttls="3600"           # Redis TTL
)

# 单层内存缓存（适用于测试）
cache = await create_cache(
    namespace="my_app",
    cache_layers="memory",
    ttls="300"  # 内存 TTL
)
```

#### 自动键哈希

使用 mmh3 自动哈希键以实现更好的分布：

```python
cache = await create_cache(
    namespace="my_app",
    auto_hash_key=True  # 默认启用
)
```

#### 查询限制

防止失败查询的重试风暴：

```python
# 失败 3 次后停止重试
data = await cache.get_or_set(
    "api:endpoint",
    default=fetch_from_api,
    query_limit=3
)
```

## 后端配置

### Redis 后端

#### 自动从 Vault 获取配置（推荐）

**推荐方式**：所有环境都应该从 Vault 获取 Redis 配置，不要在代码中硬编码 `redis_url`。

在业务模块中根据实际需求配置缓存：

```python
# 设置环境变量
# export VAULT_ADDR=http://vault.example.com:8200
# export VAULT_TOKEN=your-vault-token

# 示例 1：热点数据使用两层缓存
@alru_cache(maxsize=None)
async def get_hot_data_cache() -> Cache:
    return await create_cache(
        namespace="hot_data",
        cache_layers="memory,redis",  # 两层缓存提高性能
        ttls="60,3600"  # 内存 1 分钟，Redis 1 小时
    )

# 示例 2：普通数据仅使用 Redis
@alru_cache(maxsize=None)
async def get_normal_cache() -> Cache:
    return await create_cache(
        namespace="normal_data",
        cache_layers="redis",  # 仅 Redis，或省略此参数
        ttls="7200"  # 2 小时
    )

# 示例 3：不同 Vault 路径的配置
@alru_cache(maxsize=None)
async def get_special_cache() -> Cache:
    return await create_cache(
        namespace="special_data",
        vault_path="x-scanner/prod/special/redis"  # 特定的 Vault 路径
    )
```

#### 直接指定 Redis URL（不推荐）

虽然支持直接指定 `redis_url`，但**强烈不推荐使用**，因为这会导致配置硬编码和安全问题：

```python
# ❌ 不推荐：硬编码配置不安全且难以管理
cache = await create_cache(
    namespace="my_app",
    redis_url="redis://localhost:6379/0"  # 非必要不使用
)
```


### 内存后端

```python
cache = await create_cache(
    namespace="my_app",
    cache_layers="memory",
    ttls="300"
)
```

## API 参考

### Cache 类

提供所有缓存操作的主要缓存类。

#### 核心方法

| 方法 | 描述                  |
|--------|---------------------|
| `get(key: str) -> Optional[Any]` | 从缓存中检索值             |
| `set(key: str, value: Any, ttl: Optional[int] = None) -> bool` | 在缓存中存储值             |
| `get_or_set(key: str, default: Callable, ttl: Optional[int] = None, query_limit: int = 0) -> Optional[Any]` | 获取值或使用默认可调用对象设置它    |
| `exists(key: str) -> bool` | 检查键是否存在             |
| `delete(key: str) -> bool` | 删除键                 |
| `clear() -> int` | 清除所有键               |
| `keys(pattern: str = "*") -> list[str]` | 获取匹配的键 (仅后端)        |
| `mget(keys: list[str]) -> dict[str, Any]` | 获取多个值 (内部使用单独的 get) |
| `mset(mapping: dict[str, Any], ttl: Optional[int] = None) -> bool` | 设置多个值 (内部使用单独的 set) |
| `close()` | 关闭缓存连接              |

### 配置选项

| 选项 | 类型 | 默认值 | 描述 |
|--------|------|---------|-------------|
| `namespace` | str | (必需) | 用于隔离的键命名空间 |
| `cache_layers` | str | "redis" | 缓存层配置 (如 "memory,redis") |
| `ttls` | str | 根据层类型 | 逗号分隔的 TTL，如 "60,300" |
| `redis_url` | str | None | Redis 连接 URL (允许但非必要不使用，推荐从 Vault 自动获取) |
| `vault_path` | str | "x-scanner/prod/main/redis" | 用于 Redis 配置的 Vault 路径 |
| `auto_hash_key` | bool | True | 使用 mmh3 自动哈希键 |

## 性能考虑

1.  **多层缓存**: 通过在内存中缓存频繁访问的数据来减少 Redis 的往返次数
2.  **键哈希**: 改善键分布并防止热点
3.  **连接池**: 重用连接以获得更好的性能
4.  **查询限制**: 防止重复失败查询导致的级联失败
5.  **批量操作**: 目前 `mget` 和 `mset` 在内部使用单独的操作以保证缓存层之间的一致性。为了在大型批处理中获得最佳性能，请考虑直接使用后端。

## 环境变量

当使用 Vault 集成自动配置 Redis 时：

```bash
VAULT_ADDR=http://vault.example.com:8200
VAULT_TOKEN=your-vault-token
```

## Vault 密钥格式

在 Vault 中存储 Redis 配置，使用 `url` 键：

```json
{
  "url": "redis://:password@redis.example.com:6379/0"
}
```

## 从旧代码迁移

有关从旧缓存实现迁移的详细说明，请参阅 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)。

## 最佳实践

有关推荐的模式和实践，请参阅 [BEST_PRACTICES.md](BEST_PRACTICES.md)。

## 许可证

MIT
