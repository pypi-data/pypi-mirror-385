# Vault 模块迁移指南

## 概述

本文档指导如何将现有项目从自定义 Vault 实现迁移到 `x_scanner_commons.infrastructure.vault` 统一实现。

## 迁移原则

### 核心基线
1. **禁止二次包装** - 不允许创建本地适配器或包装器
2. **直接使用** - 必须直接导入和使用 commons vault 模块
3. **YAGNI 原则** - 只迁移实际使用的功能，删除冗余代码
4. **统一接口** - 使用标准化的方法名和参数

## 重要提示：服务器端集成

**在 X-Scanner 服务端，Vault 客户端实例必须放在 `server/app/core/vault.py`**，因为它不仅用于 API 密钥管理，还用于数据库、Redis、RabbitMQ 等基础设施的凭据管理。

## 迁移步骤

### 步骤 1: 评估现有实现

检查项目中的 Vault 相关代码：
```bash
# 查找 vault 相关文件
find . -path "*/vault/*" -name "*.py"

# 查找 vault 导入
grep -r "from.*vault import" --include="*.py"
grep -r "import.*vault" --include="*.py"
```

### 步骤 2: 删除本地实现（保留 app/core/vault.py）

```bash
# 删除本地 vault 实现目录（但保留 app/core/vault.py）
rm -rf app/infrastructure/vault/
rm -rf src/vault/
# 注意：不要删除 app/core/vault.py，这是服务器端的集成点
```

### 步骤 3: 更新导入语句

#### 导入映射表

| 旧导入 | 新导入 |
|--------|--------|
| `from app.infrastructure.vault import VaultClient` | `from x_scanner_commons.infrastructure.vault import VaultClient` |
| `from app.infrastructure.vault.exceptions import *` | `from x_scanner_commons.infrastructure.vault import *` |
| `from app.infrastructure.vault.models import *` | `from x_scanner_commons.infrastructure.vault import VaultSecret, VaultCredential` |
| `from app.vault import get_vault_client` | 删除，直接创建 VaultClient 实例 |

#### 批量替换示例

```python
# 替换所有文件中的导入
# 方法 1: 使用 sed (Linux/Mac)
find . -name "*.py" -exec sed -i '' 's/from app\.infrastructure\.vault/from x_scanner_commons.infrastructure.vault/g' {} \;

# 方法 2: 使用 Python 脚本
import os
import re

def update_imports(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 替换导入
    content = re.sub(
        r'from app\.infrastructure\.vault(?:\.\w+)? import',
        'from x_scanner_commons.infrastructure.vault import',
        content
    )
    
    with open(filepath, 'w') as f:
        f.write(content)

# 遍历所有 Python 文件
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            update_imports(os.path.join(root, file))
```

### 步骤 4: 更新初始化参数

#### 参数映射表

| 旧参数 | 新参数 | 说明 |
|--------|--------|------|
| `address` | `url` | Vault 服务器地址 |
| `mount_path` | `mount_point` | KV 挂载点 |
| `namespace` | 删除 | commons 版本不支持 namespace |
| `verify` | `verify` | 保持不变（可选） |
| `timeout` | `timeout` | 保持不变（可选） |
| `max_retries` | 删除 | 在应用层处理重试 |
| `retry_delay` | 删除 | 在应用层处理重试 |
| `cache_ttl` | 删除 | 在应用层处理缓存 |

#### 更新示例

```python
# ❌ 旧代码
vault_client = VaultClient(
    address=settings.VAULT.ADDRESS,
    token=settings.VAULT.TOKEN,
    mount_path=settings.VAULT.MOUNT_PATH,
    namespace=settings.VAULT.NAMESPACE,
    verify=settings.VAULT.VERIFY_SSL,
    timeout=settings.VAULT.TIMEOUT,
    max_retries=settings.VAULT.MAX_RETRIES,
    retry_delay=settings.VAULT.RETRY_DELAY,
    cache_ttl=settings.VAULT.CACHE_TTL,
)
await vault_client.initialize()

# ✅ 新代码
vault_client = VaultClient(
    url=settings.VAULT.ADDRESS,
    token=settings.VAULT.TOKEN,
    mount_point=settings.VAULT.MOUNT_PATH,
    kv_version=2,  # 添加 KV 版本
    verify=settings.VAULT.VERIFY_SSL,
    timeout=settings.VAULT.TIMEOUT,
)
# 不需要显式初始化
```

### 步骤 5: 更新方法调用

#### 方法映射表

| 旧方法 | 新方法 | 参数变化 |
|--------|--------|----------|
| `initialize()` | 删除 | 不需要显式初始化 |
| `read_secret(path)` | `get_secret(path)` | 参数相同 |
| `write_secret(path, data)` | `set_secret(path, data)` | 参数相同 |
| `delete_secret(path, versions)` | `delete_secret(path)` | 不支持 versions 参数 |
| `list_secrets(path)` | `list_secrets(path)` | 参数相同 |
| `check_health()` | `health()` | 返回格式可能不同 |
| `get_provider_credentials(name)` | `get_credential(name)` | 自定义路径需要调整 |
| `store_provider_credentials(name, data)` | `set_credential(credential)` | 需要创建 VaultCredential 对象 |

#### 批量替换方法名

```python
# 使用正则表达式批量替换
replacements = [
    (r'\.initialize\(\)', ''),  # 删除 initialize 调用
    (r'\.read_secret\(', '.get_secret('),
    (r'\.write_secret\(', '.set_secret('),
    (r'\.check_health\(', '.health('),
    (r'await vault_client\.initialize\(\)\n', ''),  # 删除初始化行
]

for old, new in replacements:
    content = re.sub(old, new, content)
```

### 步骤 6: 更新异常处理

#### 异常映射表

| 旧异常 | 新异常 | 说明 |
|--------|--------|------|
| `VaultSecretNotFoundError` | `VaultNotFoundError` | 合并为单一异常 |
| `VaultClientError` | `VaultClientError` | 保持不变 |
| `VaultConfigurationError` | `VaultConfigurationError` | 保持不变 |
| `VaultConnectionError(msg, original_error)` | `VaultConnectionError(msg, original_error)` | 保持不变 |

#### 更新示例

```python
# ❌ 旧代码
try:
    secret = await vault_client.read_secret(path)
except VaultSecretNotFoundError as e:
    logger.error(f"Secret not found: {e}")

# ✅ 新代码  
try:
    secret = await vault_client.get_secret(path)
except VaultNotFoundError as e:
    logger.error(f"Secret not found: {e}")
```

### 步骤 7: 创建服务器端集成点 (app/core/vault.py)

对于 X-Scanner 服务端，创建统一的 Vault 集成点：

```python
# server/app/core/vault.py
"""
Vault 集成模块 - 服务器端统一入口点
用于管理数据库、Redis、RabbitMQ 和 API 密钥等所有凭据
"""
from typing import Optional, Dict, Any
from functools import lru_cache
import asyncio

from x_scanner_commons.infrastructure.vault import (
    VaultClient,
    VaultCredential,
    VaultSecret,
    VaultSettings,
    VaultNotFoundError,
    VaultConnectionError,
)
import logging

logger = logging.getLogger(__name__)

# ========== 推荐的最佳实践实现 ==========

@lru_cache(maxsize=1)
def get_vault_client() -> VaultClient:
    """
    Get or create a singleton Vault client instance.
    
    这是推荐的最佳实践实现方式：
    - 使用 @lru_cache(maxsize=1) 确保单例
    - 使用 VaultSettings 进行配置验证
    - 提供清晰的错误信息
    
    Returns:
        VaultClient: Configured Vault client
        
    Raises:
        RuntimeError: If Vault is not properly configured
    """
    vault_settings = VaultSettings()
    if not vault_settings.is_configured:
        raise RuntimeError(
            "Vault is not properly configured. "
            "Set VAULT_ADDR and VAULT_TOKEN environment variables."
        )
    
    return VaultClient(**vault_settings.get_client_kwargs())

# ========== Vault 路径常量（最佳实践） ==========

class VaultPaths:
    """
    集中定义所有 Vault 路径常量
    这是推荐的最佳实践，便于维护和避免硬编码
    """
    # 数据库凭据路径
    DATABASE_POSTGRESQL = "database/postgresql"
    DATABASE_MYSQL = "database/mysql"
    DATABASE_MONGODB = "database/mongodb"
    
    # 基础设施凭据路径
    INFRASTRUCTURE_REDIS = "infrastructure/redis"
    INFRASTRUCTURE_RABBITMQ = "infrastructure/rabbitmq"
    INFRASTRUCTURE_ELASTICSEARCH = "infrastructure/elasticsearch"
    
    # API 提供商凭据路径前缀
    PROVIDERS_PREFIX = "providers"
    
    # 项目特定配置路径前缀
    PROJECT_PREFIX = "x-scanner"
    
    @classmethod
    def provider(cls, name: str) -> str:
        """生成提供商路径"""
        return f"{cls.PROVIDERS_PREFIX}/{name}"
    
    @classmethod
    def project(cls, env: str, config: str) -> str:
        """生成项目配置路径"""
        return f"{cls.PROJECT_PREFIX}/{env}/{config}"

# ========== 数据库凭据管理 ==========

async def get_database_credentials(db_name: str = "postgresql") -> VaultCredential:
    """
    从 Vault 获取数据库凭据
    
    Args:
        db_name: 数据库名称 (postgresql, mongodb, mysql 等)
    
    Returns:
        VaultCredential 对象，可以转换为连接字符串
    """
    client = get_vault_client()  # 使用同步单例
    path = getattr(VaultPaths, f"DATABASE_{db_name.upper()}", VaultPaths.DATABASE_POSTGRESQL)
    try:
        return await client.get_credential(path)
    except VaultNotFoundError:
        logger.error(f"Database credentials not found for: {db_name}")
        raise

async def get_database_url(db_name: str = "postgresql", async_driver: bool = True) -> str:
    """
    获取数据库连接 URL
    
    Args:
        db_name: 数据库名称
        async_driver: 是否使用异步驱动
    
    Returns:
        数据库连接 URL
    """
    credential = await get_database_credentials(db_name)
    
    # 根据数据库类型选择驱动
    if db_name == "postgresql":
        scheme = "postgresql+asyncpg" if async_driver else "postgresql"
    elif db_name == "mysql":
        scheme = "mysql+aiomysql" if async_driver else "mysql+pymysql"
    elif db_name == "mongodb":
        scheme = "mongodb"
    else:
        scheme = db_name
    
    return credential.to_uri(scheme)

# ========== Redis 凭据管理 ==========

async def get_redis_credentials() -> Dict[str, Any]:
    """从 Vault 获取 Redis 凭据"""
    client = get_vault_client()  # 使用同步单例
    try:
        secret = await client.get_secret(VaultPaths.INFRASTRUCTURE_REDIS)
        return secret.data
    except VaultNotFoundError:
        logger.warning("Redis credentials not found, using defaults")
        return {
            "host": "localhost",
            "port": 6379,
            "password": None,
            "db": 0,
        }

async def get_redis_url() -> str:
    """获取 Redis 连接 URL"""
    config = await get_redis_credentials()
    password = config.get("password", "")
    host = config.get("host", "localhost")
    port = config.get("port", 6379)
    db = config.get("db", 0)
    
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    else:
        return f"redis://{host}:{port}/{db}"

# ========== RabbitMQ 凭据管理 ==========

async def get_rabbitmq_credentials() -> Dict[str, Any]:
    """从 Vault 获取 RabbitMQ 凭据"""
    client = get_vault_client()  # 使用同步单例
    try:
        secret = await client.get_secret(VaultPaths.INFRASTRUCTURE_RABBITMQ)
        return secret.data
    except VaultNotFoundError:
        logger.warning("RabbitMQ credentials not found, using defaults")
        return {
            "host": "localhost",
            "port": 5672,
            "username": "guest",
            "password": "guest",
            "vhost": "/",
        }

async def get_rabbitmq_url() -> str:
    """获取 RabbitMQ 连接 URL"""
    config = await get_rabbitmq_credentials()
    username = config.get("username", "guest")
    password = config.get("password", "guest")
    host = config.get("host", "localhost")
    port = config.get("port", 5672)
    vhost = config.get("vhost", "/")
    
    return f"amqp://{username}:{password}@{host}:{port}/{vhost}"

# ========== API 密钥管理 ==========

async def get_api_credentials(provider: str) -> Dict[str, Any]:
    """
    从 Vault 获取第三方 API 凭据
    
    Args:
        provider: 提供商名称 (fofa, shodan, chinaz, hunter, quake 等)
    
    Returns:
        包含 API 凭据的字典
    """
    client = get_vault_client()  # 使用同步单例
    try:
        secret = await client.get_secret(VaultPaths.provider(provider))
        return secret.data
    except VaultNotFoundError:
        logger.error(f"API credentials not found for provider: {provider}")
        raise

# ========== 健康检查 ==========

async def check_vault_health() -> Dict[str, Any]:
    """检查 Vault 健康状态"""
    try:
        client = get_vault_client()  # 使用同步单例
        health = await client.health()
        return {
            "healthy": health.get("healthy", False),
            "version": health.get("version", "unknown"),
            "sealed": health.get("sealed", False),
        }
    except Exception as e:
        logger.error(f"Vault health check failed: {e}")
        return {
            "healthy": False,
            "error": str(e),
        }
```

### 步骤 8: 特殊场景处理

#### 1. 数据库集成

```python
# server/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from server.app.core.vault import get_database_url


# 使用 Vault 获取数据库连接
async def init_database():
    """初始化数据库连接池"""
    database_url = await get_database_url("postgresql", async_driver=True)

    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
    )

    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine, async_session_maker
```

#### 2. Redis 集成

```python
# server/app/core/cache.py
import redis.asyncio as redis
from server.app.core.vault import get_redis_url


async def init_redis() -> redis.Redis:
    """初始化 Redis 连接池"""
    redis_url = await get_redis_url()

    return redis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50,
    )
```

#### 3. Celery/RabbitMQ 集成

```python
# server/app/core/celery.py
from celery import Celery
from server.app.core.vault import get_rabbitmq_url, get_redis_url
import asyncio


def create_celery_app():
    """创建 Celery 应用实例"""
    # 在同步上下文中获取凭据
    loop = asyncio.new_event_loop()
    broker_url = loop.run_until_complete(get_rabbitmq_url())
    backend_url = loop.run_until_complete(get_redis_url())
    loop.close()

    celery_app = Celery(
        "x-scanner",
        broker=broker_url,
        backend=backend_url,
        include=["app.tasks"],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )

    return celery_app
```


#### 5. 缓存处理

Commons vault 不包含内置缓存，需要在应用层实现：

```python
# 添加应用层缓存
from functools import lru_cache
from datetime import datetime, timedelta

class CachedVaultClient:
    def __init__(self, client, cache_ttl=300):
        self.client = client
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    async def get_secret(self, path):
        if path in self.cache:
            secret, timestamp = self.cache[path]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return secret
        
        secret = await self.client.get_secret(path)
        self.cache[path] = (secret, datetime.now())
        return secret
```

#### 6. 重试逻辑

Commons vault 不包含重试逻辑，需要在应用层实现：

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_async(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    *args,
    **kwargs
) -> T:
    """通用异步重试函数"""
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except VaultNotFoundError:
            raise  # 不重试 404 错误
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay * (2 ** attempt))
    
    raise last_exception

# 使用示例
secret = await retry_async(vault_client.get_secret, 3, 1.0, "my/path")
```

## 常见问题和解决方案

### 问题 1: 找不到模块

```python
# 错误：ModuleNotFoundError: No module named 'x_scanner_commons'

# 解决方案：确保安装了 x-scanner-commons
pip install -e /path/to/x-scanner-commons[vault]
# 或在 pyproject.toml 中添加
x-scanner-commons = {path = "../x-scanner-commons", extras = ["vault"], develop = true}
```

### 问题 2: 参数不兼容

```python
# 错误：TypeError: __init__() got an unexpected keyword argument 'address'

# 解决方案：更新参数名
# address -> url
# mount_path -> mount_point
```

### 问题 3: 方法不存在

```python
# 错误：AttributeError: 'VaultClient' object has no attribute 'write_secret'

# 解决方案：更新方法名
# write_secret -> set_secret
# read_secret -> get_secret
# check_health -> health
```

### 问题 4: 异常类型不匹配

```python
# 错误：NameError: name 'VaultSecretNotFoundError' is not defined

# 解决方案：使用 VaultNotFoundError 替代
```

## 迁移检查清单

- [ ] 删除所有本地 vault 实现目录（保留 app/core/vault.py）
- [ ] 创建 server/app/core/vault.py 作为服务器端集成点
- [ ] 更新所有导入语句为 `from x_scanner_commons.infrastructure.vault import ...`
- [ ] 更新 VaultClient 初始化参数
- [ ] 删除所有 `await vault_client.initialize()` 调用
- [ ] 更新所有方法调用（read_secret -> get_secret 等）
- [ ] 更新异常处理（VaultSecretNotFoundError -> VaultNotFoundError）
- [ ] 集成数据库凭据管理到 Vault
- [ ] 集成 Redis 凭据管理到 Vault
- [ ] 集成 RabbitMQ 凭据管理到 Vault
- [ ] 集成 API 密钥管理到 Vault
- [ ] 实现应用层缓存（如需要）
- [ ] 实现应用层重试（如需要）
- [ ] 运行测试确保功能正常
- [ ] 更新文档和注释

## 迁移后的代码示例

### 完整示例：Provider Factory

```python
# 迁移后的完整代码
from typing import Optional, Dict, Any
import asyncio
from x_scanner_commons.infrastructure.vault import (
    VaultClient,
    VaultNotFoundError,
    VaultCredential,
)

class ProviderFactory:
    _vault_client: Optional[VaultClient] = None
    _vault_lock = asyncio.Lock()
    _credential_cache: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    async def _get_vault_client(cls):
        """获取或初始化 Vault 客户端"""
        async with cls._vault_lock:
            if cls._vault_client is None:
                cls._vault_client = VaultClient(
                    url=settings.VAULT.ADDRESS,
                    token=settings.VAULT.TOKEN,
                    mount_point=settings.VAULT.MOUNT_PATH,
                    kv_version=2,
                )
            return cls._vault_client
    
    @classmethod
    async def get_credentials(cls, provider: str):
        """获取提供商凭据"""
        # 检查缓存
        if provider in cls._credential_cache:
            return cls._credential_cache[provider]
        
        vault_client = await cls._get_vault_client()
        
        try:
            # 标准路径
            credential = await vault_client.get_credential(provider)
            cred_dict = credential.to_dict()
            
            # 缓存结果
            cls._credential_cache[provider] = cred_dict
            return cred_dict
            
        except VaultNotFoundError:
            logger.error(f"Credentials not found for {provider}")
            raise
```

### 完整示例：健康检查

```python
# 迁移后的健康检查
from x_scanner_commons.infrastructure.vault import VaultClient

class VaultHealthChecker:
    def __init__(self):
        self._vault_client = None
    
    async def check_health(self) -> Dict[str, Any]:
        """检查 Vault 健康状态"""
        try:
            if self._vault_client is None:
                self._vault_client = VaultClient(
                    url=settings.VAULT.ADDRESS,
                    token=settings.VAULT.TOKEN,
                    mount_point=settings.VAULT.MOUNT_PATH,
                    kv_version=2,
                )
            
            health = await self._vault_client.health()
            
            return {
                "status": "healthy" if health.get("healthy") else "unhealthy",
                "healthy": health.get("healthy", False),
                "version": health.get("version", "unknown"),
            }
            
        except Exception as e:
            logger.error(f"Vault health check failed: {e}")
            return {
                "status": "error",
                "healthy": False,
                "error": str(e)
            }
```

## 总结

成功迁移的关键点：

1. **彻底删除** - 完全移除本地 vault 实现，避免混淆
2. **直接使用** - 不创建任何包装器或适配器
3. **参数更新** - 正确映射所有参数名称
4. **方法更新** - 使用新的标准方法名
5. **异常统一** - 使用 commons 提供的异常类
6. **应用层补充** - 在需要时在应用层添加缓存和重试

记住：**禁止二次包装，直接使用 commons vault**。这确保了代码的一致性和可维护性。