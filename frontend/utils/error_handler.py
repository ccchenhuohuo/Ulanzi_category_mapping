"""
错误处理和日志模块
提供统一的错误处理和日志记录功能
"""
import logging
import os
from datetime import datetime
from functools import wraps
from typing import Optional, Callable
import streamlit as st


class ExecutionLogger:
    """执行日志记录器"""

    def __init__(self, log_file: str = None):
        """
        初始化日志记录器

        Args:
            log_file: 日志文件路径，默认为项目目录下的 log.txt
        """
        if log_file is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            log_file = os.path.join(current_dir, 'log.txt')

        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self):
        """配置日志记录器"""
        # 创建日志目录
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        # 配置日志格式
        self.logger = logging.getLogger('UlanziClassifier')
        self.logger.setLevel(logging.DEBUG)

        # 清除现有处理器
        self.logger.handlers.clear()

        # 文件处理器 - 写入日志文件
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # 控制台处理器 - 实时显示
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log(self, level: str, message: str, **kwargs):
        """
        记录日志

        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: 日志消息
            **kwargs: 额外的上下文信息
        """
        # 构建完整消息
        if kwargs:
            context = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} [{context}]"
        else:
            full_message = message

        # 根据级别记录日志
        level_upper = level.upper()
        if level_upper == 'DEBUG':
            self.logger.debug(full_message)
        elif level_upper == 'INFO':
            self.logger.info(full_message)
        elif level_upper == 'WARNING':
            self.logger.warning(full_message)
        elif level_upper == 'ERROR':
            self.logger.error(full_message)
        elif level_upper == 'CRITICAL':
            self.logger.critical(full_message)
        else:
            self.logger.info(full_message)

    def debug(self, message: str, **kwargs):
        """记录 DEBUG 级别日志"""
        self.log('DEBUG', message, **kwargs)

    def info(self, message: str, **kwargs):
        """记录 INFO 级别日志"""
        self.log('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """记录 WARNING 级别日志"""
        self.log('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """记录 ERROR 级别日志"""
        self.log('ERROR', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """记录 CRITICAL 级别日志"""
        self.log('CRITICAL', message, **kwargs)

    def log_operation(self, operation: str, status: str, **kwargs):
        """记录操作日志"""
        self.log('INFO', f"[{operation}] {status}", **kwargs)

    def log_classification(self, title: str, predicted: str, score: float, reason: str):
        """记录分类操作日志"""
        self.log('INFO', f"[分类] {title[:50]}... -> {predicted} (得分: {score:.1f}, 原因: {reason})")

    def log_rule_change(self, rule_type: str, field: str, old_value: str, new_value: str):
        """记录规则变更日志"""
        self.log('WARNING', f"[规则变更] {rule_type}.{field}: {old_value} -> {new_value}")

    def log_audit(self, sku_id: str, action: str, old_category: str, new_category: str):
        """记录审核日志"""
        self.log('INFO', f"[审核] {sku_id}: {action} ({old_category} -> {new_category})")

    def get_log_stats(self) -> dict:
        """获取日志统计信息"""
        stats = {
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'DEBUG': 0
        }

        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        for level in stats.keys():
                            if f'[{level}]' in line:
                                stats[level] += 1
                                break
        except Exception:
            pass

        return stats


def handle_errors(default_return=None, show_message: bool = True, reraise: bool = False):
    """
    错误处理装饰器

    Args:
        default_return: 发生错误时返回的默认值
        show_message: 是否显示错误消息
        reraise: 是否重新抛出异常

    Returns:
        装饰器函数
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"[{func.__name__}] {str(e)}"

                # 记录错误日志
                if 'execution_logger' in globals():
                    globals()['execution_logger'].error(error_msg)

                # 显示错误消息
                if show_message:
                    st.error(f"操作失败: {str(e)}")

                # 重新抛出异常（可选）
                if reraise:
                    raise

                return default_return

        return wrapper
    return decorator


def safe_execute(func: Callable, default_return=None, error_msg: str = "操作失败"):
    """
    安全执行函数

    Args:
        func: 要执行的函数
        default_return: 失败时返回的默认值
        error_msg: 错误消息

    Returns:
        函数执行结果或默认值
    """
    try:
        return func()
    except Exception as e:
        error_message = f"{error_msg}: {str(e)}"

        if 'execution_logger' in globals():
            globals()['execution_logger'].error(error_message)

        st.error(error_message)
        return default_return


# 全局日志实例
execution_logger = ExecutionLogger()
