from __future__ import annotations

import os
import sys
import tempfile
from collections.abc import Callable
from datetime import datetime
from threading import RLock
from typing import Any, Self
from weakref import WeakValueDictionary

from loguru import logger

from .config import LOG_LEVELS, OPTIMIZED_FORMAT

# 是否为开发环境
IS_DEV: bool = os.getenv('ENV', 'dev').lower() == 'dev'


class SingletonMixin:
    """线程安全的单例混入类实现"""

    _instance_lock: RLock = RLock()
    _instances: WeakValueDictionary[type, Self] = WeakValueDictionary()

    def __new__(cls: type[Self], *args: Any, **kwargs: Any) -> Self:
        """实例化处理（带错误日志和双重检查锁）"""
        # 第一次检查（无锁）
        if cls in cls._instances:
            instance = cls._instances[cls]
            # 如果提供了新参数，可能需要重新初始化
            if args or kwargs:
                instance._reinit_if_needed(*args, **kwargs)
            return instance

        # 获取锁
        with cls._instance_lock:
            # 第二次检查（有锁）
            if cls in cls._instances:
                instance = cls._instances[cls]
                if args or kwargs:
                    instance._reinit_if_needed(*args, **kwargs)
                return instance

            try:
                # 创建实例
                instance = super().__new__(cls)
                # 存储实例引用
                cls._instances[cls] = instance
                # 调用初始化
                instance.__init__(*args, **kwargs)
                return instance
            except Exception as e:
                # 清理失败的实例
                if cls in cls._instances:
                    del cls._instances[cls]
                raise RuntimeError(f'SingletonMixin {cls.__name__} __new__ failed: {e}') from e

    def _reinit_if_needed(self, *args: Any, **kwargs: Any) -> None:
        """检查是否需要重新初始化"""
        # 子类可以重写这个方法来实现参数变化的重新初始化
        pass

    @classmethod
    def reset_instance(cls: type[Self]) -> None:
        """重置单例实例"""
        with cls._instance_lock:
            _ = cls._instances.pop(cls, None)

    @classmethod
    def has_instance(cls: type[Self]) -> bool:
        """检查是否存在单例实例"""
        return cls in cls._instances

    @classmethod
    def get_instance(cls: type[Self]) -> Self | None:
        """获取当前单例实例（不创建新实例）"""
        return cls._instances.get(cls)


class LogCls(SingletonMixin):
    """增强的日志管理类

    特性：
    - 线程安全的单例模式
    - 支持动态配置更新
    - 自动处理日志轮换和清理
    - 开发环境与控制台输出，生产环境仅文件输出
    - 支持直接调用和属性访问
    """

    # 默认日志级别
    DEFAULT_LOG_LEVEL: int = 10  # DEBUG级别

    def __init__(
        self,
        level: int | str = 10,
        serialize: bool = False,
        log_file_rotation_size: str = '16 MB',
        log_file_retention_days: str = '30 days',
        log_format: str = OPTIMIZED_FORMAT,
        log_dir: str | None = None,
        log_file_name: str | None = None,
        enable_file_logging: bool = True,
        enable_console_logging: bool | None = None,
    ) -> None:
        # 保存配置参数
        self._config = {
            'level': level,
            'serialize': serialize,
            'log_file_rotation_size': log_file_rotation_size,
            'log_file_retention_days': log_file_retention_days,
            'log_format': log_format,
            'log_dir': log_dir,
            'log_file_name': log_file_name,
            'enable_file_logging': enable_file_logging,
            'enable_console_logging': enable_console_logging or IS_DEV,
        }

        # 初始化内部状态
        self._file_handler_id: int | None = None
        self._console_handler_id: int | None = None
        self._initialized: bool = False

        # 执行初始化
        self._initialize_logger()

    def _reinit_if_needed(self, *args: Any, **kwargs: Any) -> None:
        """检查是否需要重新初始化配置"""
        if args or kwargs:
            # 创建新的配置字典
            new_config = self._config.copy()

            # 更新配置参数
            config_keys = ['level', 'serialize', 'log_file_rotation_size', 'log_file_retention_days', 'log_format', 'log_dir', 'log_file_name', 'enable_file_logging', 'enable_console_logging']

            # 处理位置参数
            for i, key in enumerate(config_keys):
                if i < len(args):
                    new_config[key] = args[i]

            # 处理关键字参数
            for key, value in kwargs.items():
                if key in config_keys:
                    new_config[key] = value

            # 如果配置有变化，重新初始化
            if new_config != self._config:
                self._config = new_config
                self._reinitialize_logger()

    def _initialize_logger(self) -> None:
        """初始化日志配置"""
        if self._initialized:
            return

        # 配置基础logger
        self.logger = logger
        self.logger.remove()

        # 转换字符串级别为整数
        level = self._config['level']
        if isinstance(level, str):
            level = LOG_LEVELS.get(level.upper(), self.DEFAULT_LOG_LEVEL)
        self._config['level'] = level

        # 设置日志目录和文件
        if self._config['enable_file_logging']:
            self._setup_file_logging()

        # 设置控制台日志
        if self._config['enable_console_logging']:
            self._setup_console_logging()

        self._initialized = True

    def _reinitialize_logger(self) -> None:
        """重新初始化日志配置"""
        self.logger.remove()
        self._file_handler_id = None
        self._console_handler_id = None
        self._initialized = False
        self._initialize_logger()

    def _setup_file_logging(self) -> None:
        """设置文件日志"""
        log_dir = self._config['log_dir']
        log_file_name = self._config['log_file_name']

        # 确定日志目录
        logs_dir = os.path.join(tempfile.gettempdir(), 'logs') if log_dir is None else os.path.abspath(log_dir)

        os.makedirs(logs_dir, exist_ok=True)

        # 确定日志文件名
        if log_file_name is None:
            log_file_name = f'xt_{datetime.now().strftime("%Y%m%d")}.log'

        log_file = os.path.join(logs_dir, log_file_name)

        # 添加文件处理器
        try:
            self._file_handler_id = self.logger.add(
                log_file,
                rotation=self._config['log_file_rotation_size'],
                retention=self._config['log_file_retention_days'],
                level=self._config['level'],
                encoding='utf-8',
                format=self._config['log_format'],
                serialize=self._config['serialize'],
                backtrace=True,
                diagnose=True,
                catch=True,
                enqueue=True,  # 添加队列支持，避免多线程问题
            )
        except Exception as e:
            # 文件日志失败时，fallback到控制台
            print(f'文件日志初始化失败: {e}，将使用控制台日志')
            self._config['enable_file_logging'] = False
            if not self._config['enable_console_logging']:
                self._config['enable_console_logging'] = True
                self._setup_console_logging()

    def _setup_console_logging(self) -> None:
        """设置控制台日志"""
        try:
            self._console_handler_id = self.logger.add(
                sys.stderr,
                level=self._config['level'],
                format=self._config['log_format'],
                serialize=self._config['serialize'],
                backtrace=True,
                diagnose=True,
                catch=True,
                # colorize=True,  # 启用颜色
            )
        except Exception as e:
            print(f'控制台日志初始化失败: {e}')

    def __call__(self, *args: Any, **kwargs: Any) -> list[None]:
        """
        支持实例直接调用，将多个参数作为多条日志记录

        Args:
            *args: 要记录的参数
            **kwargs: 传递给loguru的额外参数

        Returns:
            list[None]: 每条日志的记录结果列表
        """
        return [self.logger.info(str(arg), **kwargs) for arg in args]

    def __getitem__(self, attr: str) -> Callable[..., Any]:
        """通过索引访问日志方法"""
        return getattr(self.logger, attr)

    def __getattr__(self, attr: str) -> Callable[..., Any]:
        """动态获取方法并包装"""
        original_method = getattr(self.logger, attr)

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """包装函数，处理多个参数"""
            if len(args) > 1:
                # 如果有多个参数，分别记录
                return [original_method(str(arg), **kwargs) for arg in args]
            # 单个参数，直接调用原始方法
            return original_method(*args, **kwargs)

        return wrapper

    def set_level(self, level: int | str) -> None:
        """动态设置日志级别"""
        if isinstance(level, str):
            level = LOG_LEVELS.get(level.upper(), self.DEFAULT_LOG_LEVEL)

        if level != self._config['level']:
            self._config['level'] = level
            self._reinitialize_logger()

    def update_config(self, **kwargs: Any) -> None:
        """更新日志配置"""
        config_changed = False
        for key, value in kwargs.items():
            if key in self._config and self._config[key] != value:
                self._config[key] = value
                config_changed = True

        if config_changed:
            self._reinitialize_logger()

    def get_config(self) -> dict[str, Any]:
        """获取当前配置"""
        return self._config.copy()

    def disable_file_logging(self) -> None:
        """禁用文件日志"""
        if self._config['enable_file_logging']:
            self._config['enable_file_logging'] = False
            self._reinitialize_logger()

    def enable_file_logging(self) -> None:
        """启用文件日志"""
        if not self._config['enable_file_logging']:
            self._config['enable_file_logging'] = True
            self._reinitialize_logger()

    def get_logger(self) -> logger:
        """获取原始的loguru logger实例"""
        return self.logger

    @property
    def log_file(self) -> str | None:
        """获取当前日志文件路径"""
        if not self._config['enable_file_logging']:
            return None

        log_dir = self._config['log_dir']
        log_file_name = self._config['log_file_name']

        if log_dir is None:
            logs_dir = os.path.join(tempfile.gettempdir(), 'logs')
        else:
            logs_dir = os.path.abspath(log_dir)

        if log_file_name is None:
            log_file_name = f'xt_{datetime.now().strftime("%Y%m%d")}.log'

        return os.path.join(logs_dir, log_file_name)
