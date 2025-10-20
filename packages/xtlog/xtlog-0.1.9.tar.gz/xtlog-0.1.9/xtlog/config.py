# !/usr/bin/env python3
"""日志配置模块。

本模块提供以下核心功能:
- 日志级别映射定义
- 日志图标配置
- 日志格式设置

主要特性:
- 统一的日志级别管理
- 丰富的日志图标支持
- 多种日志格式模板
- 支持JSON格式日志
- 支持环境变量配置

Author: sandorn sandorn@live.cn
Github: http://github.com/sandorn/xtlog
"""

from __future__ import annotations

import os

# 日志级别映射
LOG_LEVELS: dict[str, int] = {"TRACE": 5, "DEBUG": 10, "INFO": 20, "SUCCESS": 25, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


# 日志图标
LOG_ICONS: dict[str, str] = {
    "TRACE": "\u270f\ufe0f",  # ✏️ - 跟踪日志
    "START": "\u25b6\ufe0f",  # ▶️ - 开始执行
    "STOP": "\u23f9\ufe0f",  # ⏹️ - 停止执行
    "DEBUG": "\U0001f41e",  # 🐞 - 调试信息
    "INFO": "\u2139\ufe0f",  # ℹ️ - 普通信息
    "SUCCESS": "\u2705\ufe0f",  # ✅ - 成功信息
    "WARNING": "\u26a0\ufe0f",  # ⚠️ - 警告信息
    "ERROR": "\u274c\ufe0f",  # ❌ - 错误信息
    "CRITICAL": "\u2620\ufe0f",  # ☠️ - 严重错误
    "DENIED": "\u26d4\ufe0f",  # ⛔ - 拒绝操作
}


# 标准日志格式（默认）
OPTIMIZED_FORMAT: str = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> <level>{level.icon}</level> | <magenta>{process: >6}</magenta>:<yellow>{thread: <6}</yellow> | <level>{message}</level>'
)

# 简洁日志格式
SIMPLE_FORMAT: str = '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>'

# 详细日志格式
DETAILED_FORMAT: str = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> <level>{level.icon}</level> | '
    '<magenta>P:{process}</magenta> : <yellow>T:{thread}</yellow> | '
    '<blue>{name}</blue>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
    '<level>{message}</level>\n'
    '{exception}'
)

# JSON格式（用于结构化日志）
JSON_FORMAT: str = '{{"time": "{time:YYYY-MM-DD HH:mm:ss.SSS}", "level": "{level.name}", "message": "{message}", "process": {process}, "thread": {thread}}}'

# 环境变量配置
ENV_CONFIG: dict[str, int | str | None] = {
    # 是否为开发环境
    "IS_DEV": os.getenv("ENV", "dev").lower() == "dev",
    # 默认日志级别
    "DEFAULT_LOG_LEVEL": os.getenv("LOG_LEVEL", "DEBUG"),
    # 日志目录
    "LOG_DIR": os.getenv("LOG_DIR", None),
    # 日志文件名模板
    "LOG_FILE_TEMPLATE": os.getenv("LOG_FILE_TEMPLATE", "xt_{date}.log"),
    # 日志文件轮转大小
    "LOG_ROTATION_SIZE": os.getenv("LOG_ROTATION_SIZE", "16 MB"),
    # 日志文件保留天数
    "LOG_RETENTION_DAYS": os.getenv("LOG_RETENTION_DAYS", "30 days"),
}

# 格式映射
FORMAT_MAP: dict[str, str] = {
    "default": OPTIMIZED_FORMAT,
    "simple": SIMPLE_FORMAT,
    "detailed": DETAILED_FORMAT,
    "json": JSON_FORMAT,
}


def get_format(format_name: str) -> str:
    """
    获取指定名称的日志格式

    Args:
        format_name: 格式名称，可选值：default, simple, detailed, json

    Returns:
        str: 对应的日志格式字符串
    """
    return FORMAT_MAP.get(format_name.lower(), OPTIMIZED_FORMAT)
