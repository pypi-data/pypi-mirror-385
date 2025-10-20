[根目录](../../CLAUDE.md) > [src](../) > **tools**

# Tools 模块 - Redis 操作工具集

## 模块职责

Tools 模块提供完整的 Redis 数据操作工具集，按数据类型分组，每个工具都通过 `@mcp.tool()` 装饰器注册为 MCP 工具，供 AI 智能体调用。

## 入口与启动

### 模块结构
所有工具模块都通过 `src/common/server.py` 的 `load_tools()` 函数自动加载：
```python
for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
    importlib.import_module(f"src.tools.{module_name}")
```

### 工具注册模式
每个工具都使用统一的模式：
```python
@mcp.tool()
async def tool_name(param1: type1, param2: type2) -> return_type:
    """工具描述"""
    try:
        r = RedisConnectionManager.get_connection()
        # Redis 操作
        return "成功消息"
    except RedisError as e:
        return f"错误消息: {str(e)}"
```

## 对外接口

### 字符串操作 (`string.py`)
- `set(key, value, expiration=None)`: 设置字符串值，支持过期时间
- `get(key)`: 获取字符串值
- 支持 str, bytes, int, float, dict 类型

### 哈希操作 (`hash.py`)
- `hset(name, key, value, expire_seconds=None)`: 设置哈希字段
- `hget(name, key)`: 获取哈希字段值
- `hgetall(name)`: 获取整个哈希
- `hdel(name, *keys)`: 删除哈希字段
- 支持向量嵌入存储

### 列表操作 (`list.py`)
- `lpush(key, *values)`: 左侧推入元素
- `rpush(key, *values)`: 右侧推入元素
- `lpop(key)`: 左侧弹出元素
- `rpop(key)`: 右侧弹出元素
- `lrange(key, start, end)`: 获取列表范围

### 集合操作 (`set.py`)
- `sadd(key, *members)`: 添加集合成员
- `smembers(key)`: 获取所有集合成员
- `srem(key, *members)`: 删除集合成员
- `sinter(*keys)`: 集合交集
- `sunion(*keys)`: 集合并集

### 有序集合操作 (`sorted_set.py`)
- `zadd(key, *args)`: 添加有序集合成员
- `zrange(key, start, end, desc=False)`: 获取有序集合范围
- `zrank(key, member)`: 获取成员排名
- `zrem(key, *members)`: 删除有序集合成员

### 流操作 (`stream.py`)
- `xadd(key, fields, id='*', maxlen=None)`: 添加流条目
- `xread(key, id='$', count=None, block=None)`: 读取流条目
- `xgroup_create(key, groupname, id='$')`: 创建消费者组
- `xreadgroup(key, groupname, consumername, count=None)`: 消费者组读取

### JSON 操作 (`json.py`)
- `json_set(key, path, value)`: 设置 JSON 路径值
- `json_get(key, path='.')`: 获取 JSON 路径值
- `json_del(key, path)`: 删除 JSON 路径
- 支持复杂嵌套数据结构

### 发布订阅 (`pub_sub.py`)
- `publish(channel, message)`: 发布消息到频道
- `subscribe(channel, callback)`: 订阅频道
- 支持实时通知和聊天应用

### 向量搜索 (`redis_query_engine.py`)
- `get_indexes()`: 获取所有索引列表
- `get_index_info(index_name)`: 获取索引详细信息
- `create_vector_index(index_name, prefix, vector_dim)`: 创建向量索引
- `search_vectors(index_name, vector, k=10)`: 向量相似性搜索

### 服务器管理 (`server_management.py`)
- `dbsize()`: 获取数据库键数量
- `info(section='default')`: 获取服务器信息
- `client_list()`: 获取连接客户端列表
- `ping()`: 测试连接状态

### 杂项操作 (`misc.py`)
- `del_key(key)`: 删除键
- `exists(key)`: 检查键是否存在
- `expire(key, seconds)`: 设置键过期时间
- `ttl(key)`: 获取键剩余时间

## 关键依赖与配置

### 核心依赖
```python
from src.common.connection import RedisConnectionManager
from src.common.server import mcp
from redis.exceptions import RedisError
import numpy as np  # 用于向量操作
import json  # 用于 JSON 处理
```

### 特殊功能依赖
- **向量搜索**: `redis.commands.search.*`
- **JSON 操作**: RedisJSON 模块
- **流操作**: Redis Streams

## 数据模型

### 统一响应模式
- **成功**: 返回描述性成功消息
- **失败**: 返回包含错误信息的消息
- **数据查询**: 返回结构化数据（JSON、字典、列表）

### 错误处理模型
```python
try:
    r = RedisConnectionManager.get_connection()
    # Redis 操作
    return result
except RedisError as e:
    return f"Error: {str(e)}"
```

## 测试与质量

### 测试策略
- **单元测试**: 每个工具都有对应的测试文件
- **Mock 测试**: 使用 `mock_redis_connection_manager` fixture
- **错误场景**: 测试各种 Redis 错误情况
- **数据类型**: 测试不同数据类型的处理

### 测试覆盖范围
- 功能正确性测试
- 参数验证测试
- 错误处理测试
- 边界条件测试

## 常见问题 (FAQ)

### Q: 如何处理大对象的存储？
A: 对于大型 JSON 或哈希，考虑分片存储或使用 Redis 的压缩功能。

### Q: 向量搜索需要什么特殊配置？
A: 需要 RediSearch 模块支持，使用 `create_vector_index` 创建索引。

### Q: 流操作的消费者组如何管理？
A: 使用 `xgroup_create` 创建组，`xreadgroup` 读取消息，`xack` 确认处理。

### Q: JSON 操作的性能如何？
A: JSON 操作比普通字符串操作稍慢，但提供了更好的数据结构支持。

## 相关文件清单

| 文件 | 数据类型 | 主要工具 |
|------|----------|----------|
| `string.py` | 字符串 | `set()`, `get()` |
| `hash.py` | 哈希 | `hset()`, `hget()`, `hgetall()` |
| `list.py` | 列表 | `lpush()`, `rpop()`, `lrange()` |
| `set.py` | 集合 | `sadd()`, `smembers()`, `sinter()` |
| `sorted_set.py` | 有序集合 | `zadd()`, `zrange()`, `zrank()` |
| `stream.py` | 流 | `xadd()`, `xread()`, `xreadgroup()` |
| `json.py` | JSON | `json_set()`, `json_get()`, `json_del()` |
| `pub_sub.py` | 发布订阅 | `publish()`, `subscribe()` |
| `redis_query_engine.py` | 向量搜索 | `create_vector_index()`, `search_vectors()` |
| `server_management.py` | 服务器管理 | `dbsize()`, `info()`, `client_list()` |
| `misc.py` | 杂项 | `del_key()`, `exists()`, `expire()` |

## 变更记录 (Changelog)

### 2025-10-20 15:14:26 - 初始化工具模块文档
- 创建 tools 模块文档
- 列出所有 Redis 操作工具
- 文档化工具接口和使用模式