# Vault 模块最佳实践指南

## 概述

`x_scanner_commons.infrastructure.vault` 模块提供了统一的 HashiCorp Vault 集成接口，用于安全地管理密钥和凭据。本文档描述了使用该模块的最佳实践。

## 核心原则

### 1. YAGNI (You Aren't Gonna Need It)
- 只实现当前需要的功能
- 避免过度设计和预留扩展
- 最好的代码是不存在的代码

### 2. 直接使用，禁止二次封装
- **必须直接导入使用 commons vault 模块**
- **严禁创建本地适配器或包装器**
- 统一的接口确保跨项目的一致性

## 使用指南

### 基本用法

```python
from x_scanner_commons.infrastructure.vault import (
    VaultClient,
    VaultCredential,
    VaultSecret,
    VaultNotFoundError,
    VaultConnectionError,
)

# 初始化客户端
client = VaultClient(
    url="http://vault.example.com:8200",
    token="your-token",
    mount_point="secret",  # KV v2 挂载点
    kv_version=2,          # KV 版本
)

# 异步操作
async def manage_secrets():
    # 存储密钥
    await client.set_secret(
        path="myapp/config",
        data={"api_key": "xxx", "api_secret": "yyy"}
    )
    
    # 读取密钥
    secret = await client.get_secret("myapp/config")
    api_key = secret.data.get("api_key")
    
    # 处理凭据
    credential = await client.get_credential("database")
    db_url = credential.to_uri("postgresql")
```

### 异常处理

```python
from x_scanner_commons.infrastructure.vault import (
    VaultNotFoundError,
    VaultConnectionError,
    VaultAuthenticationError,
)

try:
    secret = await client.get_secret("nonexistent")
except VaultNotFoundError as e:
    # 密钥不存在
    logger.warning(f"Secret not found: {e}")
except VaultConnectionError as e:
    # 连接失败
    logger.error(f"Vault connection failed: {e}")
    # 可以访问原始异常
    if e.original_error:
        logger.debug(f"Original error: {e.original_error}")
except VaultAuthenticationError as e:
    # 认证失败
    logger.error(f"Authentication failed: {e}")
```

### 凭据管理

```python
# 使用 VaultCredential 管理结构化凭据
from x_scanner_commons.infrastructure.vault import VaultCredential

# 从 URI 创建凭据
credential = VaultCredential.from_uri(
    name="database",
    uri="postgresql://user:pass@host:5432/dbname"
)

# 存储凭据
await client.set_credential(credential)

# 读取并使用凭据
db_cred = await client.get_credential("database")
connection_string = db_cred.to_uri("postgresql")

# 访问凭据字段
print(f"Host: {db_cred.host}")
print(f"Port: {db_cred.port}")
print(f"Database: {db_cred.database}")
```

## 配置最佳实践

### 1. 环境变量配置

```python
# 推荐的配置结构
class VaultSettings:
    ADDRESS: str = "http://vault:8200"
    TOKEN: str = os.getenv("VAULT_TOKEN")
    MOUNT_PATH: str = "secret"
    KV_VERSION: int = 2
    VERIFY_SSL: bool = True
    TIMEOUT: int = 30

# 使用配置
client = VaultClient(
    url=settings.VAULT.ADDRESS,
    token=settings.VAULT.TOKEN,
    mount_point=settings.VAULT.MOUNT_PATH,
    kv_version=settings.VAULT.KV_VERSION,
)
```

### 2. 服务器集成（重要）

**在 X-Scanner 服务端，Vault 客户端实例应该放在 `server/app/core/vault.py`**，因为它不仅用于 API 密钥管理，还用于数据库和 Redis 等基础设施的凭据管理。

```python
# server/app/core/vault.py
from x_scanner_commons.infrastructure.vault import VaultClient, VaultCredential, VaultSettings
from functools import lru_cache
import asyncio

# 推荐的最佳实践：使用 @lru_cache(maxsize=1) 实现单例模式
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

# 异步版本（如果需要）
_async_vault_client = None
_vault_lock = asyncio.Lock()

async def get_async_vault_client() -> VaultClient:
    """
    获取 Vault 客户端单例（异步版本）
    
    注意：优先使用同步版本的 get_vault_client()，
    只在必须异步初始化的场景使用此函数。
    """
    global _async_vault_client, _vault_lock
    async with _vault_lock:
        if _async_vault_client is None:
            vault_settings = VaultSettings()
            if not vault_settings.is_configured:
                raise RuntimeError(
                    "Vault is not properly configured. "
                    "Set VAULT_ADDR and VAULT_TOKEN environment variables."
                )
            _async_vault_client = VaultClient(**vault_settings.get_client_kwargs())
    return _async_vault_client

# Vault 路径常量（最佳实践：集中管理所有路径）
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
    
    @classmethod
    def provider(cls, name: str) -> str:
        """生成提供商路径"""
        return f"{cls.PROVIDERS_PREFIX}/{name}"

# API 密钥管理
async def get_api_credentials(provider: str) -> dict:
    """从 Vault 获取第三方 API 凭据"""
    client = get_vault_client()  # 使用同步单例
    secret = await client.get_secret(VaultPaths.provider(provider))
    return secret.data
```

### 3. 路径规范

```python
# 推荐的路径结构
# providers/服务名 - 用于外部服务 API 凭据
await client.set_secret("providers/fofa", fofa_credentials)
await client.set_secret("providers/shodan", shodan_credentials)
await client.set_secret("providers/chinaz", chinaz_credentials)

# infrastructure/服务名 - 用于基础设施凭据
await client.set_secret("infrastructure/redis", redis_config)
await client.set_secret("infrastructure/rabbitmq", rabbitmq_config)

# database/名称 - 用于数据库凭据（使用 VaultCredential）
await client.set_credential(postgresql_credential)  # 自动存储到 credentials/database/postgresql
await client.set_credential(mongodb_credential)     # 自动存储到 credentials/database/mongodb

# 项目特定路径
await client.set_secret("x-scanner/main/config", main_config)
await client.set_secret("x-scanner/test/config", test_config)
```

### 4. 缓存策略

Vault 客户端内部实现了缓存机制，但建议：

```python
class ProviderFactory:
    _vault_client = None
    _credential_cache = {}
    
    @classmethod
    async def get_credentials(cls, provider):
        # 先检查本地缓存
        if provider in cls._credential_cache:
            return cls._credential_cache[provider]
        
        # 从 Vault 获取（Vault 客户端有自己的缓存）
        credential = await cls._vault_client.get_credential(provider)
        
        # 缓存到本地
        cls._credential_cache[provider] = credential.to_dict()
        return cls._credential_cache[provider]
```

## 安全最佳实践

### 1. Token 管理
- **永远不要硬编码 token**
- 使用环境变量或配置文件
- 定期轮换 token
- 使用最小权限原则

### 2. SSL/TLS
- 生产环境必须启用 SSL 验证
- 开发环境可以临时禁用：`verify=False`

### 3. 错误处理
- 不要在日志中暴露敏感信息
- 捕获并适当处理所有 Vault 异常
- 实现重试机制处理临时故障

### 4. 密钥轮换
```python
# 使用 rotate_secret 进行密钥轮换
rotated = await client.rotate_secret("providers/api")
```

## 测试最佳实践

### 1. Mock Vault 客户端

```python
from unittest.mock import AsyncMock, MagicMock
from x_scanner_commons.infrastructure.vault import VaultSecret

@pytest.fixture
async def mock_vault_client():
    client = AsyncMock()
    client.get_secret.return_value = VaultSecret(
        path="test/path",
        data={"key": "value"}
    )
    return client
```

### 2. 集成测试

```python
import pytest
from x_scanner_commons.infrastructure.vault import VaultClient

@pytest.mark.integration
async def test_vault_operations():
    client = VaultClient(
        url=TEST_VAULT_URL,
        token=TEST_VAULT_TOKEN,
        mount_point="test",
        kv_version=2,
    )
    
    # 测试 CRUD 操作
    test_path = f"test/integration/{uuid.uuid4()}"
    test_data = {"test": "data"}
    
    try:
        await client.set_secret(test_path, test_data)
        secret = await client.get_secret(test_path)
        assert secret.data == test_data
    finally:
        # 清理测试数据
        await client.delete_secret(test_path)
```

## 常见错误和解决方案

### 1. 导入错误

```python
# ❌ 错误：从本地 vault 包装器导入
from server.app.infrastructure import VaultClient

# ✅ 正确：直接从 commons 导入
from x_scanner_commons.infrastructure.vault import VaultClient
```

### 2. 初始化参数错误
```python
# ❌ 错误：使用旧参数名
client = VaultClient(
    address="http://vault:8200",  # 错误参数名
    mount_path="secret",           # 错误参数名
)

# ✅ 正确：使用正确的参数名
client = VaultClient(
    url="http://vault:8200",       # 正确参数名
    mount_point="secret",           # 正确参数名
    kv_version=2,
)
```

### 3. 方法调用错误
```python
# ❌ 错误：使用不存在的方法
await client.write_secret(path, data)
await client.read_secret(path)
await client.check_health()

# ✅ 正确：使用标准接口方法
await client.set_secret(path, data)
await client.get_secret(path)
await client.health()
```

## 性能优化

### 1. 批量操作
```python
# 批量读取多个密钥
async def get_multiple_secrets(paths):
    tasks = [client.get_secret(path) for path in paths]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### 2. 连接池
```python
# 单例模式避免重复创建客户端
class VaultManager:
    _instance = None
    
    @classmethod
    async def get_client(cls):
        if cls._instance is None:
            cls._instance = VaultClient(...)
        return cls._instance
```

## 监控和日志

### 1. 健康检查
```python
async def health_check():
    try:
        health = await client.health()
        if not health.get("healthy"):
            alert("Vault is unhealthy", health)
        return health
    except Exception as e:
        logger.error(f"Vault health check failed: {e}")
        return {"healthy": False, "error": str(e)}
```

### 2. 操作日志
```python
import logging

logger = logging.getLogger(__name__)

async def get_secret_with_logging(path):
    try:
        logger.debug(f"Fetching secret from path: {path}")
        secret = await client.get_secret(path)
        logger.info(f"Successfully retrieved secret from: {path}")
        return secret
    except VaultNotFoundError:
        logger.warning(f"Secret not found at path: {path}")
        raise
    except Exception as e:
        logger.error(f"Failed to get secret from {path}: {e}")
        raise
```

## 总结

遵循这些最佳实践可以确保：
1. **一致性** - 跨项目使用统一的 Vault 接口
2. **可维护性** - 避免重复代码和不必要的抽象
3. **安全性** - 正确处理敏感信息
4. **可靠性** - 适当的错误处理和重试机制
5. **性能** - 合理的缓存和连接管理

记住核心原则：**直接使用 commons vault，禁止二次封装**。