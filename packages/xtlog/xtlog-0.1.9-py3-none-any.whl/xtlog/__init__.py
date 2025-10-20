# !/usr/bin/env python3
"""基于loguru的高性能日志库。

本模块提供以下核心功能:
- 基于loguru的高性能日志记录
- 文件和控制台双输出
- 自动日志文件轮转和保留

主要特性:
- 单例模式，确保全局只有一个日志实例
- 自动识别调用位置信息
- 支持动态设置日志级别

Example:
    >>> from xtlog import mylog
    >>> mylog.info('这是一条信息日志')
    >>> mylog.error('这是一条错误日志')

Author: sandorn sandorn@live.cn
Github: http://github.com/sandorn/xtlog
"""

from __future__ import annotations

from .logger import LogCls
from .utils import get_function_location

# 创建全局日志实例
mylog: LogCls = LogCls()


__all__ = ['LogCls', '__version__', 'get_function_location', 'mylog']
