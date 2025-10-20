# 缓存模块最佳实践

本文档提供使用缓存模块的高级模式和最佳实践。基础用法和 API 参考请查看 [README.md](README.md)。

## 1. 单例模式（推荐）

### 为什么使用单例模式

1. **资源效率**：避免重复创建 Redis 连接
2. **性能优化**：复用连接池
3. **一致性保证**：确保同一命名空间使用相同的缓存实例
4. **避免二次封装**：直接使用 `x_scanner_commons` 提供的功能，减少代码层次

### 实现方式

使用 `alru_cache` 装饰器创建单例缓存实例：

```python
from async_lru import alru_cache
from x_scanner_commons.infrastructure.cache import create_cache, Cache

@alru_cache(maxsize=None)
async def get_domain_cache() -> Cache:
    """获取域名缓存单例"""
    return await create_cache(
        namespace="icp_domain",
        cache_layers="memory,redis",  # 两层缓存
        ttls="60,3600"  # 内存 60秒，Redis 3600秒
    )
```

## 2. 命名空间策略

### 使用描述性的命名空间

命名空间用于隔离不同服务或模块之间的缓存键：

```python
# ✅ 好的 - 清晰且具体
namespace="user_session"
namespace="product_catalog"
namespace="api_rate_limit"

# ❌ 坏的 - 太通用
namespace="cache1"
namespace="temp"
namespace="data"
```

### 版本控制策略

当数据结构发生变化时，在命名空间中包含版本号：

```python
# 当更改缓存数据结构时
old_cache = await create_cache(namespace="products_v1", backend="redis")
new_cache = await create_cache(namespace="products_v2", backend="redis")
```

## 3. 多层缓存策略

根据数据访问模式选择合适的缓存层：

| 数据类型 | 缓存层配置 | TTL 建议 | 使用场景 |
|---------|-----------|---------|---------|
| 热点数据 | `memory,redis` | 内存: 30-60s, Redis: 1-6h | 高频访问的配置、权限数据 |
| 普通数据 | `redis` | 1-24h | API 响应、查询结果 |
| 冷数据 | `redis` | 24-72h | 报表数据、历史记录 |

## 4. TTL (生存时间) 策略

### 设置适当的 TTL

不同的数据类型需要不同的 TTL 策略：

```python
cache = await create_cache(namespace="app")

# 短生命周期数据 (用户会话, 临时令牌)
await cache.set("session_123", session_data, ttl=300)  # 5 分钟

# 中等生命周期数据 (API 响应, 计算结果)
await cache.set("api_response", data, ttl=3600)  # 1 小时

# 长生命周期数据 (配置, 引用数据)
await cache.set("config", config_data, ttl=86400)  # 24 小时
```

## 5. 查询限制模式

### 防止重试风暴

使用查询限制来防止重复失败：

```python
# 失败 3 次后停止重试
user_data = await cache.get_or_set(
    "user:profile:123",
    default=fetch_user_from_db,
    ttl=3600,
    query_limit=3  # 3 次失败尝试后放弃
)

# 对于关键数据，允许更多重试
critical_data = await cache.get_or_set(
    "system:config",
    default=fetch_system_config,
    ttl=7200,
    query_limit=10  # 关键数据允许更多重试
)
```

## 6. 键设计

### 使用结构化的键模式

一致的键模式使缓存管理更容易：

```python
# 使用冒号作为分隔符
key = f"service:entity:identifier:version"

# 示例
user_key = f"user:profile:{user_id}"
api_key = f"api:endpoint:{endpoint}:{params_hash}"
domain_key = f"domain:icp:{domain_name}"
```

### 利用自动键哈希

缓存使用 mmh3 自动哈希键以实现更好的分布：

```python
# auto_hash_key 默认启用
cache = await create_cache(
    namespace="app",
    cache_layers="redis",
    auto_hash_key=True  # 键被自动哈希
)

# 禁用以进行调试或需要确切键时
debug_cache = await create_cache(
    namespace="debug",
    cache_layers="redis",
    auto_hash_key=False  # 使用原始键
)
```

## 7. 错误处理

### 始终使用 get_or_set 以保证弹性

`get_or_set` 方法提供内置的错误处理：

```python
async def get_user_data(user_id: int):
    """使用自动缓存获取用户数据。"""
    
    async def fetch_from_db():
        # 仅在缓存未命中时调用
        return await db.get_user(user_id)
    
    # 优雅地处理缓存失败
    return await cache.get_or_set(
        f"user:{user_id}",
        default=fetch_from_db,
        ttl=3600
    )
```

### 在 Try-Except 中处理缓存操作

```python
async def safe_cache_operation(cache, key: str, value: Any):
    """安全地设置缓存值，不会因失败而中断。"""
    try:
        return await cache.set(key, value, ttl=3600)
    except Exception as e:
        logger.warning(f"为 {key} 设置缓存失败: {e}")
        # 在没有缓存的情况下继续
        return False
```

## 8. 配置管理

### 推荐：从 Vault 自动获取配置

```python
# 设置环境变量
export VAULT_ADDR=http://vault.example.com:8200
export VAULT_TOKEN=your-vault-token

# 自动从 Vault 获取 Redis 配置
cache = await create_cache(namespace="my_app")
```

### 避免硬编码配置

永远不要在代码中硬编码 Redis URL 或密码。

## 9. 批量操作

### 对多个键使用批量方法

```python
# ❌ 坏的 - 多次往返
for key in keys:
    await cache.set(key, values[key])

# ✅ 好的 - 单次批量操作
await cache.mset({
    "user:1": user1_data,
    "user:2": user2_data,
    "user:3": user3_data
})

# 批量获取
users = await cache.mget(["user:1", "user:2", "user:3"])
```

## 10. 资源管理

### 应用生命周期管理

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时预热缓存
    cache = await get_user_cache()
    yield
    # 关闭时清理资源
    await cache.close()
    get_user_cache.cache_clear()  # 清理 alru_cache

app = FastAPI(lifespan=lifespan)
```

## 核心原则

1. **单例模式**: 使用 `alru_cache` 确保缓存实例单例
2. **安全配置**: 从 Vault 自动获取配置，避免硬编码
3. **分层缓存**: 根据数据访问模式选择合适的缓存层
4. **容错设计**: 使用 `get_or_set` 和查询限制防止故障扩散
5. **命名空间隔离**: 不同模块使用独立的命名空间
6. **合理的 TTL**: 根据数据特性设置过期时间
7. **优雅降级**: 缓存失败不应影响业务运行
