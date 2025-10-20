# !/usr/bin/env python3
"""xtlog高级用法示例。

本示例展示了xtlog库的高级用法，包括：
- 自定义日志格式
- 结构化日志输出
- 异常捕获
- 上下文管理

Author: sandorn sandorn@live.cn
Github: http://github.com/sandorn/xtlog
"""

from __future__ import annotations

import time
from contextlib import contextmanager

from xtlog import LogCls, mylog
from xtlog.config import DETAILED_FORMAT, JSON_FORMAT


# 创建一个上下文管理器，用于记录代码块执行时间
@contextmanager
def log_time(operation_name: str):
    """记录代码块执行时间的上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        mylog.info(f'{operation_name} 完成,耗时: {elapsed_time:.4f}秒')


def simulate_error():
    """模拟一个错误，用于演示异常捕获"""
    try:
        # 故意引发一个除零错误
        return 1 / 0
    except Exception as e:
        # 使用xtlog记录异常
        mylog.exception(f'发生异常: {e!s}')
        return None


def demonstrate_structured_logging():
    """演示结构化日志输出"""
    # 重置单例实例，以便创建新的实例
    LogCls.reset_instance()

    # 创建一个使用JSON格式的日志实例
    json_log = LogCls(
        level='INFO',
        log_format=JSON_FORMAT,
        serialize=True,  # 启用序列化
    )

    # 记录结构化日志
    json_log.info('用户登录', extra={'user_id': 12345, 'ip_address': '192.168.1.1', 'login_time': time.strftime('%Y-%m-%d %H:%M:%S'), 'success': True})

    # 记录更复杂的结构化数据
    user_data = {'id': 12345, 'name': '张三', 'roles': ['admin', 'user'], 'settings': {'theme': 'dark', 'notifications': True}}

    json_log.info('用户数据', extra={'user': user_data})


def demonstrate_detailed_logging():
    """演示详细日志格式"""
    # 重置单例实例，以便创建新的实例
    LogCls.reset_instance()

    # 创建一个使用详细格式的日志实例
    detailed_log = LogCls(level='DEBUG', log_format=DETAILED_FORMAT)

    # 记录不同级别的日志
    detailed_log.debug('这是一条详细的调试日志')
    detailed_log.info('这是一条详细的信息日志')
    detailed_log.warning('这是一条详细的警告日志')

    # 记录带有额外信息的日志
    detailed_log.info('用户操作', extra={'operation': '文件上传', 'file_size': '2.5MB', 'file_type': 'image/jpeg'})


def main():
    """主函数，演示xtlog的高级用法"""
    # 1. 使用上下文管理器记录执行时间
    with log_time('耗时操作'):
        # 模拟一个耗时操作
        time.sleep(1.5)

    # 2. 异常捕获示例
    print('\n异常捕获示例...\n')
    simulate_error()

    # 3. 结构化日志输出
    print('\n结构化日志输出示例...\n')
    demonstrate_structured_logging()

    # 4. 详细日志格式
    print('\n详细日志格式示例...\n')
    demonstrate_detailed_logging()


if __name__ == '__main__':
    main()
