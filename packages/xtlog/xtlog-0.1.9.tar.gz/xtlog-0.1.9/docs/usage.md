# xtlog 使用指南

## 简介

xtlog是一个基于loguru的Python日志库，提供了简单易用的接口和丰富的功能。它支持控制台和文件双输出、自定义日志格式、结构化日志输出等功能。

## 安装

```bash
pip install xtlog
```

## 基本用法

### 快速开始

```python
from xtlog import mylog

# 记录不同级别的日志
mylog.debug("这是一条调试日志")
mylog.info("这是一条信息日志")
mylog.warning("这是一条警告日志")
mylog.error("这是一条错误日志")
mylog.critical("这是一条严重错误日志")

# 直接调用日志实例
mylog("这是直接调用的日志")
```

### 设置日志级别

```python
# 设置日志级别为WARNING
mylog.set_level("WARNING")

# 此时只有WARNING及以上级别的日志会被记录
mylog.debug("这条调试日志不会显示")
mylog.info("这条信息日志不会显示")
mylog.warning("这条警告日志会显示")
```

## 高级用法

### 自定义日志实例

```python
from xtlog import LogCls
from xtlog.config import FORMAT_MAP

# 重置单例实例，以便创建新的实例
LogCls.reset_instance()

# 创建自定义日志实例
custom_log = LogCls(
    level="INFO",
    log_format=FORMAT_MAP["simple"],
    log_file_rotation_size="10 MB",
    log_file_retention_days="7 days",
    log_dir="/custom/log/path",
    log_file_name="custom.log"
)

custom_log.info("这是来自自定义日志实例的信息")
```

### 结构化日志输出

```python
from xtlog import LogCls
from xtlog.config import JSON_FORMAT

# 创建一个使用JSON格式的日志实例
json_log = LogCls(
    level="INFO",
    log_format=JSON_FORMAT,
    serialize=True  # 启用序列化
)

# 记录结构化日志
json_log.info("用户登录", extra={
    "user_id": 12345,
    "ip_address": "192.168.1.1",
    "login_time": "2023-01-01 12:00:00",
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

# 创建一个上下文管理器，用于记录代码块执行时间
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
    # 执行耗时操作
    time.sleep(1.5)
```

## 配置选项

### 日志级别

- TRACE: 5
- DEBUG: 10
- INFO: 20
- SUCCESS: 25
- WARNING: 30
- ERROR: 40
- CRITICAL: 50

### 日志格式

xtlog提供了多种预定义的日志格式：

- default: 优化格式，包含时间、级别、路径和消息
- simple: 简洁格式，只包含基本信息
- detailed: 详细格式，包含更多信息如进程ID、线程ID等
- json: JSON格式，用于结构化日志输出

### 环境变量配置

xtlog支持通过环境变量进行配置：

- `ENV`: 环境名称，默认为"dev"
- `LOG_LEVEL`: 日志级别，默认为"DEBUG"
- `LOG_FORMAT`: 日志格式，默认为"default"
- `LOG_FILE`: 日志文件名，默认为自动生成
- `LOG_DIR`: 日志目录，默认为项目根目录下的logs目录
- `LOG_ROTATION_SIZE`: 日志文件轮转大小，默认为"16 MB"
- `LOG_RETENTION_DAYS`: 日志文件保留天数，默认为"30 days"

## 更多示例

更多示例请参考[examples](../examples)目录。