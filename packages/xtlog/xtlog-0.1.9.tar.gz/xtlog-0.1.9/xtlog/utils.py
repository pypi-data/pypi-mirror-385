# !/usr/bin/env python3
"""日志工具函数模块。

本模块提供以下核心功能:
- 函数位置信息获取

Author: sandorn sandorn@live.cn
Github: http://github.com/sandorn/xtlog
"""

from __future__ import annotations

import contextlib
import inspect
from collections.abc import Callable
from typing import Any


def get_function_location(func: Callable[..., Any] | None) -> str:
    """
    获取函数的位置信息(文件、行号、函数名)

    Args:
        func: 要获取位置信息的函数

    Returns:
        str: 格式为 "文件路径:行号@函数名 | " 的字符串，用于日志记录
    """
    # 基础检查
    if not callable(func) or func is None:
        return 'unknown:0@unknown | '

    # 获取原始函数(处理装饰器情况)
    original_func: Callable[..., object] = func
    with contextlib.suppress(Exception):
        original_func = inspect.unwrap(func)

    # 尝试使用__code__属性获取位置信息(最可靠的方法)
    if hasattr(original_func, "__code__"):
        code = original_func.__code__
        func_name = getattr(original_func, '__name__', 'unknown')
        return f'{code.co_filename}:{code.co_firstlineno}@{func_name} | '

    # 回退方案：使用inspect.getfile
    try:
        file_path = inspect.getfile(original_func)
        _source_lines, line_no = inspect.getsourcelines(original_func)
        func_name = getattr(original_func, '__name__', 'unknown')
        return f'{file_path}:{line_no}@{func_name} | '
    except Exception:
        # 最后的回退方案
        module_name = getattr(original_func, '__module__', 'unknown') or 'unknown'
        func_name = getattr(original_func, '__name__', 'unknown') or 'unknown'
        return f'{module_name}:0@{func_name} | '