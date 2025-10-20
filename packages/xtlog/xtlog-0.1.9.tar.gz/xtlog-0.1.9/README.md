# xtlog

基于 loguru 的高性能日志库

## 特性

- 🚀 **高性能**: 基于 loguru 的高性能日志记录
- 📝 **双输出**: 文件和控制台双输出支持
- 🔄 **自动轮转**: 自动日志文件轮转和保留
- 🎯 **单例模式**: 确保全局只有一个日志实例
- ⚙️ **动态配置**: 支持动态设置日志级别
- 🎨 **丰富图标**: 支持丰富的日志图标显示
- 📊 **结构化日志**: 支持JSON格式的结构化日志输出
- 🔍 **异常追踪**: 自动捕获和记录异常堆栈
- 🛠️ **灵活配置**: 支持自定义日志格式和输出路径

## 安装

```bash
pip install xtlog
```

## 快速开始

```python
from xtlog import mylog

# 基本使用
mylog.info("这是一条信息日志")
mylog.error("这是一条错误日志")

# 支持直接调用
mylog("第一条日志", "第二条日志")

# 设置日志级别
mylog.set_level("DEBUG")
```

## 高级功能

### 自定义日志配置

```python
from xtlog import LogCls

# 创建自定义日志实例
custom_log = LogCls(
    level=20,  # INFO级别
    log_file_rotation_size="10 MB",
    log_file_retention_days="7 days",
    log_dir="/custom/log/path",  # 自定义日志目录
    log_file_name="custom.log"   # 自定义日志文件名
)

custom_log.info("自定义配置的日志")
```

### 结构化日志输出

```python
from xtlog import LogCls
from xtlog.config import JSON_FORMAT

# 创建JSON格式的日志实例
json_log = LogCls(
    level="INFO",
    log_format=JSON_FORMAT,
    serialize=True  # 启用序列化
)

# 记录结构化日志
json_log.info("用户登录", extra={
    "user_id": 12345,
    "ip_address": "192.168.1.1",
    "success": True
})
```

### 异常捕获

```python
try:
    # 可能引发异常的代码
    result = 1 / 0
except Exception as e:
    # 使用xtlog记录异常
    mylog.exception(f"发生异常: {str(e)}")
```

### 上下文管理

```python
import time
from contextlib import contextmanager

@contextmanager
def log_time(operation_name):
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        mylog.info(f"{operation_name} 完成，耗时: {elapsed_time:.4f}秒")

# 使用上下文管理器
with log_time("耗时操作"):
    time.sleep(1.5)
```

## 日志级别

支持以下日志级别：

- `TRACE` (5)
- `DEBUG` (10)
- `INFO` (20)
- `SUCCESS` (25)
- `WARNING` (30)
- `ERROR` (40)
- `CRITICAL` (50)

## 日志格式

xtlog提供了多种预定义的日志格式：

- `default`: 优化格式，包含时间、级别、路径和消息
- `simple`: 简洁格式，只包含基本信息
- `detailed`: 详细格式，包含更多信息如进程ID、线程ID等
- `json`: JSON格式，用于结构化日志输出

```python
from xtlog import LogCls
from xtlog.config import FORMAT_MAP

# 使用简洁格式
simple_log = LogCls(log_format=FORMAT_MAP["simple"])
```

## 配置

### 环境变量

- `ENV`: 设置环境类型，`dev` 为开发环境（显示控制台日志），其他为生产环境
- `LOG_LEVEL`: 日志级别，默认为"DEBUG"
- `LOG_FORMAT`: 日志格式，默认为"default"
- `LOG_FILE`: 日志文件名，默认为自动生成
- `LOG_DIR`: 日志目录，默认为项目根目录下的logs目录
- `LOG_ROTATION_SIZE`: 日志文件轮转大小，默认为"16 MB"
- `LOG_RETENTION_DAYS`: 日志文件保留天数，默认为"30 days"

### 默认配置

- 日志文件位置: `系统临时目录/logs/xt_YYYYMMDD.log`
- 文件轮转大小: `16 MB`
- 文件保留天数: `30 days`
- 默认日志级别: `DEBUG` (10)

## 版本更新

### v0.1.8

- 优化了日志文件处理器配置，添加 `enqueue=True` 参数，避免多线程环境下的日志写入问题
- 改进了日志文件路径的处理逻辑，确保在各种操作系统环境下的兼容性
- 增强了异常处理和错误恢复机制，提高了日志系统的稳定性

### v0.1.7

- 修复了 `get_function_location` 函数对无 `__name__` 属性对象的处理问题，增强函数的容错性和适用范围

### v0.1.6

- 移除了对 `callfrom` 参数的支持
- 优化了日志文件存储路径，使用系统临时目录

### v0.1.5

- 修复了 [set_level](xtlog/logger.py#L273-L282) 方法对 `callfrom` 参数的影响问题
- 优化了日志级别动态切换时的性能表现

### v0.1.4

- 初始版本发布

## 示例

查看 [examples](./examples) 目录获取更多示例：

- [基本用法](./examples/basic_usage.py)
- [高级用法](./examples/advanced_usage.py)

## 文档

详细文档请参考 [docs](./docs) 目录：

- [使用指南](./docs/usage.md)

## 开发

### 安装开发依赖

```bash
pip install -e .[dev]
```

### 运行测试

```bash
pytest
```

### 代码检查

```bash
ruff check --fix --unsafe-fixes
```

### 类型检查

```bash
mypy .
```

## 贡献

欢迎提交问题和贡献代码！请参阅 [贡献指南](./CONTRIBUTING.md)。

## 许可证

MIT License

## 作者

sandorn <sandorn@live.cn>

GitHub: [http://github.com/sandorn/xtlog](http://github.com/sandorn/xtlog)