# 缓存模块迁移指南

## 概述

本指南帮助您从现有的缓存实现迁移到 `x-scanner-commons` 中的统一缓存模块。无论您之前使用的是自定义缓存方案、第三方缓存库，还是直接操作 Redis/Memcached，本指南都将帮助您平滑迁移。

## 主要改进

新的缓存模块提供：
- **统一接口**: 单一的 `Cache` 类，具有一致的 API
- **多层缓存**: 可选的 L1 (内存) + L2 (Redis) 架构
- **自动键哈希**: 使用 mmh3 实现更好的分布
- **查询限制**: 内置的重试风暴预防机制
- **清洁架构**: 面向对象的设计，具有清晰的抽象

### 重要说明

- 迁移完成后，建议删除原有的缓存封装层，业务模块直接从 `x_scanner_commons.infrastructure.cache` 使用 `create_cache`
- 在业务层通过单例模式（如使用 `alru_cache`）或依赖注入管理 `Cache` 实例
- 如果存在过渡期的兼容层代码，完成迁移后应及时清理

## 从现有实现迁移

### 1. 函数式到面向对象的迁移

#### 获取或设置缓存（get-or-set 模式）

**场景描述**: 许多缓存实现使用函数式编程风格，通过独立函数操作缓存，需要显式传入缓存客户端、键名、获取函数等参数。新版采用面向对象设计，通过缓存实例的方法直接操作。主要改进包括：
- 统一的 Cache 类接口，屏蔽底层实现差异
- 内置多层缓存支持（L1 内存 + L2 持久化）
- 支持从配置中心（如 Vault）自动获取连接信息
- 更符合直觉的 API 设计

**新版实现**:
```python
from x_scanner_commons.infrastructure.cache import create_cache

# 一次性创建缓存
domain_cache = await create_cache(
    namespace="domain",
    # 不需要 redis_url，自动从 Vault 获取
    cache_layers="memory,redis",  # 两层缓存
    ttls="60,3600"  # 内存 60秒，Redis 3600秒
)

async def get_domain_info(domain: str):
    return await domain_cache.get_or_set(
        key=f"domain:{domain}",
        default=lambda: fetch_from_api(domain),
        query_limit=3,
        ttl=3600
    )
```

#### 设置缓存值

**场景描述**: 传统实现通常提供独立的设置函数，需要传入客户端连接、键、值、过期时间等参数。新版通过缓存对象的 `set` 方法统一操作，接口更加简洁。

**新版实现**:
```python
user_cache = await create_cache(
    namespace="user", 
    cache_layers="redis",  # 仅使用 Redis 层
    ttls="3600"  # TTL 3600秒
)
await user_cache.set("user:123", user_data, ttl=3600)
```

### 2. 缓存实例管理

**场景描述**: 现有系统可能通过各种方式创建缓存连接：直接使用 Redis 客户端、使用第三方缓存库、自定义的工厂函数等。这些方案往往缺乏统一管理，配置分散。新版提供标准化的缓存实例创建和管理：
- 统一的工厂方法，支持多种后端（memory/redis/future extensions）
- 灵活的连接池配置，适应不同负载场景
- 可选的多层缓存架构，自动管理数据同步
- 细粒度的 TTL 控制，支持分层独立过期策略

**新版实现**:
```python
from async_lru import alru_cache
from x_scanner_commons.infrastructure.cache import create_cache, Cache

# 使用单例模式管理缓存实例（最佳实践）
@alru_cache(maxsize=None)
async def get_domain_cache() -> Cache:
    """获取域名缓存单例"""
    return await create_cache(
        namespace="icp_domain",
        # 不需要 redis_url，自动从 Vault 获取
        cache_layers="memory,redis",  # 两层缓存：L1 内存 + L2 Redis
        ttls="60,3600"  # 内存 60秒，Redis 3600秒
    )

@alru_cache(maxsize=None)
async def get_org_domain_cache() -> Cache:
    """获取组织域名缓存单例"""
    return await create_cache(
        namespace="org_domain",
        cache_layers="redis",  # 仅使用 Redis
        ttls="60"
    )

# 高流量场景的缓存配置
@alru_cache(maxsize=None)
async def get_httpx_cache() -> Cache:
    """获取 HTTP 扫描缓存单例"""
    return await create_cache(
        namespace="httpx",
        cache_layers="memory,redis",  # 两层缓存
        ttls="30,300",  # 内存 30秒，Redis 300秒
    )

# 使用示例
async def get_domain_info(domain: str):
    cache = await get_domain_cache()  # 获取单例
    return await cache.get_or_set(
        f"domain:{domain}",
        default=lambda: fetch_from_api(domain),
        ttl=3600
    )
```

### 3. 查询限制和防雪崩机制

**场景描述**: 传统缓存实现可能通过独立的计数器或布隆过滤器来防止缓存穿透和雪崩。这通常需要额外的逻辑来跟踪失败次数并决定是否继续查询。新版将防护机制内置到核心 API 中，通过 `query_limit` 参数自动管理：
- 自动跟踪查询失败次数
- 达到阈值后自动熔断，避免雪崩
- 无需手动编写防护逻辑

**新版实现**:
```python
# 内置于 get_or_set 的 query_limit 参数中
result = await cache.get_or_set(
    key=key,
    default=fetch_data,
    query_limit=3  # 自动处理重试限制
)
```

### 4. 多层缓存架构

**场景描述**: 高性能系统常采用多层缓存策略：本地内存作为一级缓存，Redis/Memcached 作为二级缓存。传统实现需要手动编写复杂的同步和失效逻辑。新版提供开箱即用的多层缓存支持：
- 透明的多层数据访问，自动查找最快的数据源
- 智能的数据回填策略，热数据自动提升到上层
- 一致的失效机制，避免脏数据
- 可与应用层缓存（如 `alru_cache`）无缝集成

**新版实现（结合单例模式）**:
```python
from async_lru import alru_cache

# 推荐：自动两层缓存 + 单例模式
@alru_cache(maxsize=None)
async def get_domain_cache() -> Cache:
    return await create_cache(
        namespace="domain",
        cache_layers="memory,redis",  # 自动 L1+L2
        ttls="60,3600"  # L1: 60秒，L2: 3600秒
    )

# 使用时自动获取单例
async def get_value(key: str):
    cache = await get_domain_cache()
    return await cache.get(key)
```

## 迁移过程（一次性完成）

### 步骤 1: 更新依赖

**推荐方式（开发阶段）**：

由于 x-scanner-commons 尚未发布到 PyPI，建议使用本地路径依赖：

```toml
# pyproject.toml
[tool.poetry.dependencies]
# 使用相对路径指向本地的 x-scanner-commons 目录
x-scanner-commons = { path = "../x-scanner-commons", develop = true, extras = ["cache"] }
```

或者使用 Git 仓库依赖：

```toml
# pyproject.toml
[tool.poetry.dependencies]
x-scanner-commons = { git = "https://github.com/yourusername/x-scanner-commons.git", branch = "main", extras = ["cache"] }
```

**未来方式（发布后）**：

```toml
# pyproject.toml
[tool.poetry.dependencies]
x-scanner-commons = { version = "^0.1.0", extras = ["cache"] }
```

### 步骤 2: 直接在业务模块中使用

**重要**：
- 删除所有 `app/core/cache.py` 中的二次封装
- 直接在每个业务模块中使用 `x_scanner_commons.infrastructure.cache`
- 一次性完成所有迁移，不要逐步进行

```python
# 直接在业务模块中使用，例如 app/modules/domain/service.py
from async_lru import alru_cache
from x_scanner_commons.infrastructure.cache import create_cache, Cache  # 直接导入

@alru_cache(maxsize=None)
async def get_domain_cache() -> Cache:
    """获取域名缓存单例"""
    return await create_cache(
        namespace="icp_domain",
        # 不需要 redis_url，自动从 Vault 获取
        cache_layers="memory,redis",
        ttls="60,3600"
    )

# 使用缓存
async def get_domain_info(domain: str):
    cache = await get_domain_cache()
    return await cache.get_or_set(
        f"domain:{domain}",
        default=lambda: fetch_from_api(domain),
        ttl=3600
    )
```

### 步骤 3: 删除旧的缓存代码

1. 删除 `app/core/cache.py` 文件（如果存在）
2. 删除 `app/core/cache_migration.py` 文件（如果存在）
3. 移除所有对这些文件的引用

### 步骤 4: 更新所有业务模块

在每个需要缓存的业务模块中，直接定义和使用缓存：

```python
# app/modules/user/service.py
from async_lru import alru_cache
from x_scanner_commons.infrastructure.cache import create_cache, Cache

@alru_cache(maxsize=None)
async def get_user_cache() -> Cache:
    return await create_cache(
        namespace="user",
        cache_layers="memory,redis",
        ttls="3600,43200"  # 内存 1小时，Redis 12小时
    )

async def get_user(user_id: int):
    cache = await get_user_cache()
    return await cache.get_or_set(
        f"user:{user_id}",
        default=lambda: fetch_from_db(user_id),
        ttl=3600
    )
```

```python
# app/modules/product/service.py
from async_lru import alru_cache
from x_scanner_commons.infrastructure.cache import create_cache, Cache

@alru_cache(maxsize=None)
async def get_product_cache() -> Cache:
    return await create_cache(
        namespace="product",
        ttl=7200
    )

async def get_product(product_id: int):
    cache = await get_product_cache()
    return await cache.get_or_set(
        f"product:{product_id}",
        default=lambda: fetch_from_db(product_id),
        ttl=3600
    )
```

### 步骤 5: 更新缓存键

如果使用 auto_hash_key (默认)，键会自动哈希：

```python
# 旧版使用原始键或手动哈希
key = mmh3.hash64(f"domain:{domain}")

# 新版自动哈希 (如果 auto_hash_key=True)
key = f"domain:{domain}"  # 将在内部哈希
```

### 步骤 6: 测试迁移

```python
import pytest
from x_scanner_commons.infrastructure.cache import create_cache

@pytest.fixture
async def test_cache():
    """使用内存后端进行测试。"""
    return await create_cache(
        namespace="test",
        cache_layers="memory",
        ttls="60"
    )

async def test_cache_operations(test_cache):
    # 测试 set/get
    await test_cache.set("key", "value")
    assert await test_cache.get("key") == "value"
    
    # 测试 get_or_set
    calls = 0
    async def fetcher():
        nonlocal calls
        calls += 1
        return "fetched"
    
    # 第一次调用获取
    result = await test_cache.get_or_set("new_key", fetcher)
    assert result == "fetched"
    assert calls == 1
    
    # 第二次调用使用缓存
    result = await test_cache.get_or_set("new_key", fetcher)
    assert result == "fetched"
    assert calls == 1  # 没有额外的获取
```

## 常见迁移模式

### 模式 1: 服务类的缓存集成

**场景描述**: 业务服务需要缓存支持。传统做法可能是在服务内部创建缓存连接、使用全局变量、或硬编码缓存逻辑。这些方式导致代码耦合度高，难以测试和维护。新版推荐通过依赖注入模式：
- 服务依赖抽象的 Cache 接口而非具体实现
- 便于单元测试时注入模拟缓存
- 支持运行时切换不同缓存策略

**新版实现**:
```python
class UserService:
    def __init__(self, cache: Cache):
        self.cache = cache
    
    async def get_user(self, user_id):
        return await self.cache.get_or_set(
            f"user:{user_id}",
            lambda: self.fetch_from_db(user_id),
            ttl=3600
        )

# 初始化
from x_scanner_commons.infrastructure.cache import create_cache

user_cache = await create_cache(namespace="user", cache_layers="redis", ttls="3600")
service = UserService(cache=user_cache)
```

### 模式 2: 批量操作优化

**场景描述**: 批量缓存操作是常见需求。许多实现通过循环单次操作来完成，导致大量网络开销。新版提供原生批量操作支持：
- 批量设置（mset）和获取（mget）方法
- 管道化执行，减少网络往返
- 原子性保证，避免部分失败

**新版实现**:
```python
# 单次批量操作
await domain_cache.mset({
    f"domain:{domain}": data[domain]
    for domain in domains
})
```

## 配置映射

| 旧版设置 | 新版设置 | 描述 |
|----------------|-------------|-------------|
| `namespace` | `namespace` | 键前缀 (相同) |
| `timeout` | `timeout` | 操作超时 |
| N/A | `ttl` | 键的默认 TTL |
| N/A | `cache_layers` | 缓存层配置（如 "memory,redis"）|
| N/A | `ttls` | 各层 TTL 配置（如 "60,3600"）|
| N/A | `auto_hash_key` | 使用 mmh3 自动哈希 |

## 注意事项

1. **一次性完成**：不要逐步迁移，应该一次性完成所有迁移
2. **不要二次封装**：直接使用 x_scanner_commons 提供的功能
3. **单例模式**：使用 alru_cache 确保每个命名空间只有一个缓存实例
4. **监控指标**：迁移后密切监控缓存命中率和性能

## 迁移清单

- [ ] 安装 x-scanner-commons[cache]
- [ ] 删除 app/core/cache.py 和 app/core/cache_migration.py
- [ ] 在每个业务模块中直接使用 create_cache
- [ ] 替换所有 cache_get_or_set 调用为 Cache.get_or_set
- [ ] 替换所有 cache_set 调用为 Cache.set
- [ ] 更新所有 has_query_cache 用法
- [ ] 运行所有测试确保通过
- [ ] 在开发环境中验证
- [ ] 部署到生产环境

## 性能改进

迁移后，您应该会看到：

1.  **减少延迟**: L1 缓存从内存中提供热点数据
2.  **更好的分布**: mmh3 哈希可防止热点
3.  **更少的失败**: 查询限制可防止级联失败
4.  **更清晰的代码**: 面向对象的 API 更易于维护

## 支持

对于迁移问题：

1.  启用调试日志：
```python
import logging
logging.getLogger("x_scanner_commons.infrastructure.cache").setLevel(logging.DEBUG)
```

2.  测试连接性：
```python
cache = await create_cache("test", cache_layers="redis", redis_url="...")
await cache.set("test", "value")
assert await cache.get("test") == "value"
print("缓存工作正常！")
```

3.  查看 [最佳实践](BEST_PRACTICES.md) 指南
4.  查看主 [README](README.md) 以获取 API 参考
