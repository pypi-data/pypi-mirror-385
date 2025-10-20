[根目录](../../CLAUDE.md) > [src](../) > **common**

# Common 模块 - 核心基础设施

## 模块职责

Common 模块提供 Redis MCP Server 的核心基础设施，包括 MCP 服务器初始化、Redis 连接管理、配置解析和日志记录等功能。

## 入口与启动

### 主要组件
- **server.py**: MCP 服务器核心，使用 FastMCP 框架
- **connection.py**: Redis 连接管理器，支持单实例和集群模式
- **config.py**: 配置管理，支持 CLI 参数和环境变量
- **logging_utils.py**: 日志配置和工具

### 启动流程
1. `main.py` 解析命令行参数
2. `config.py` 处理配置（CLI > 环境变量 > 默认值）
3. `server.py` 初始化 FastMCP 服务器
4. 动态加载 `tools/` 目录下的所有工具模块
5. 启动 MCP 服务器监听 stdio 连接

## 对外接口

### FastMCP 服务器 (`server.py`)
```python
# 服务器初始化
mcp = FastMCP("Redis MCP Server", dependencies=["redis", "dotenv", "numpy"])

# 动态工具加载
def load_tools():
    for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
        importlib.import_module(f"src.tools.{module_name}")
```

### Redis 连接管理 (`connection.py`)
```python
class RedisConnectionManager:
    @classmethod
    def get_connection(cls, decode_responses=True) -> Redis:
        # 单例模式，支持 SSL/TLS 和集群
```

### 配置管理 (`config.py`)
```python
# Redis URI 解析
def parse_redis_uri(uri: str) -> dict

# CLI 参数覆盖配置
def set_redis_config_from_cli(config: dict)
```

## 关键依赖与配置

### Redis 连接配置
```python
REDIS_CFG = {
    "host": os.getenv("REDIS_HOST", "127.0.0.1"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "username": os.getenv("REDIS_USERNAME", None),
    "password": os.getenv("REDIS_PWD", ""),
    "ssl": os.getenv("REDIS_SSL", False),
    "ssl_ca_path": os.getenv("REDIS_SSL_CA_PATH", None),
    "cluster_mode": os.getenv("REDIS_CLUSTER_MODE", False),
    "db": int(os.getenv("REDIS_DB", 0)),
}
```

### 支持的连接方式
1. **Redis URI**: `redis://user:pass@host:port/db`
2. **Redis SSL URI**: `rediss://user:pass@host:port/db?ssl_cert_reqs=required`
3. **命令行参数**: `--host`, `--port`, `--password`, `--ssl`
4. **环境变量**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PWD`

## 数据模型

### 连接管理模型
- **单例模式**: 确保整个应用只有一个 Redis 连接实例
- **连接池**: 自动管理连接池，最大连接数 10
- **错误处理**: 完整的 Redis 异常处理机制

### 配置层次模型
1. 默认配置值
2. 环境变量配置
3. 命令行参数配置（最高优先级）

## 测试与质量

### 测试覆盖
- **单元测试**: 测试配置解析、连接管理
- **Mock 测试**: 模拟 Redis 连接和错误场景
- **集成测试**: 测试实际的 Redis 连接

### 质量保证
- **类型注解**: 完整的类型提示
- **错误处理**: 全面的异常捕获和处理
- **日志记录**: 结构化的日志输出

## 常见问题 (FAQ)

### Q: 如何连接到 Redis 集群？
A: 设置 `cluster_mode=true` 或使用环境变量 `REDIS_CLUSTER_MODE=true`，连接管理器会自动使用 `RedisCluster` 类。

### Q: SSL 连接如何配置？
A: 使用 `rediss://` URI 或设置 SSL 相关参数：`ssl_ca_path`, `ssl_certfile`, `ssl_keyfile`。

### Q: 连接池大小是多少？
A: 默认最大连接数为 10，可在 `connection.py` 中调整 `max_connections` 参数。

### Q: 如何处理连接失败？
A: 连接管理器会捕获所有 Redis 异常并重新抛出，调用方需要处理这些异常。

## 相关文件清单

| 文件 | 职责 | 主要类/函数 |
|------|------|-------------|
| `server.py` | MCP 服务器核心 | `FastMCP`, `load_tools()` |
| `connection.py` | Redis 连接管理 | `RedisConnectionManager` |
| `config.py` | 配置管理 | `parse_redis_uri()`, `REDIS_CFG` |
| `logging_utils.py` | 日志工具 | `configure_logging()` |
| `__init__.py` | 包初始化 | - |

## 变更记录 (Changelog)

### 2025-10-20 15:14:26 - 初始化模块文档
- 创建 common 模块文档
- 分析核心组件和接口
- 文档化配置管理和连接机制