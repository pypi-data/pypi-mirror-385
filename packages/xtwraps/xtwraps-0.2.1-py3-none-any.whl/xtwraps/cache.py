# !/usr/bin/env python3
"""
==============================================================
Description  : 缓存装饰器模块 - 提供函数结果缓存功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-01 15:45:00
Github       : https://github.com/sandorn/xtwraps

本模块提供以下核心功能：
- cache_wrapper：函数结果缓存装饰器，基于functools.lru_cache
- clear_cache：清除指定函数的缓存
- CacheManager：缓存管理器类，管理多个函数的缓存

主要特性：
- 基于Python内置的lru_cache实现高效缓存
- 支持配置缓存大小和过期时间
- 支持清除特定函数或所有函数的缓存
- 同时支持同步和异步函数
- 保留原始函数的元数据
- 完整的类型注解支持
==============================================================
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Any

from .strategy import UnifiedWrapper


def cache_wrapper(maxsize: int | None = 128, typed: bool = False, ttl: int | None = None) -> Callable[[Callable], Callable]:
    """缓存装饰器，支持同步/异步函数

    Args:
        maxsize: 缓存最大大小，None表示无限制
        typed: 是否区分参数类型
        ttl: 缓存生存时间（秒），None表示永不过期

    Returns:
        Callable[[Callable], Callable]: 缓存装饰器

    Example:
        >>> @cache_wrapper(maxsize=100)
        >>> def expensive_computation(x: int) -> int:
        >>> # 复杂计算
        >>>     return x * x
        >>>
        >>> @cache_wrapper(ttl=300)  # 5分钟缓存
        >>> async def async_operation(data: str) -> dict:
        >>> # 异步操作
        >>>     return {"result": data.upper()}
    """
    # 直接使用已有的CacheWrapper类实现，降低复杂度
    return CacheWrapper(maxsize=maxsize, typed=typed, ttl=ttl)


def _hashable_repr(obj):
    """将对象转换为可哈希的字符串表示"""
    import json

    try:
        # 尝试直接使用对象（如果它已经是可哈希的）
        hash(obj)
        return obj
    except TypeError:
        # 如果对象不可哈希，使用JSON序列化
        try:
            return json.dumps(obj, sort_keys=True, default=str)
        except (TypeError, ValueError):
            # 如果JSON序列化失败，使用字符串表示
            return str(obj)


def _make_cache_key(args: tuple, kwargs: dict, typed: bool) -> tuple:
    """生成缓存键

    Args:
        args: 位置参数
        kwargs: 关键字参数
        typed: 是否区分参数类型

    Returns:
        tuple: 缓存键
    """
    # 处理位置参数
    key_parts = []
    for arg in args:
        key_parts.append(_hashable_repr(arg))

    # 处理关键字参数
    if kwargs:
        # 对kwargs进行排序以确保一致性
        sorted_kwargs = sorted(kwargs.items())
        for k, v in sorted_kwargs:
            key_parts.append((k, _hashable_repr(v)))

    # 处理类型信息
    if typed:
        for arg in args:
            key_parts.append(type(arg).__name__)
        if kwargs:
            for v in kwargs.values():
                key_parts.append(type(v).__name__)

    return tuple(key_parts)


class CacheWrapper(UnifiedWrapper):
    """缓存装饰器类实现

    基于类的缓存装饰器实现，提供更多配置选项。
    """

    def __init__(self, maxsize: int | None = 128, typed: bool = False, ttl: int | None = None) -> None:
        """初始化缓存装饰器

        Args:
            maxsize: 缓存最大大小
            typed: 是否区分参数类型
            ttl: 缓存生存时间
        """
        super().__init__(maxsize=maxsize, typed=typed, ttl=ttl)
        self.cache = {}

    def _execute_sync(self, func: Callable, args: tuple, kwargs: dict) -> Any:
        """执行同步函数

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数

        Returns:
            Any: 函数执行结果
        """
        import time

        key = _make_cache_key(args, kwargs, self.config.get('typed', False))
        ttl = self.config.get('ttl')

        # 检查缓存
        if key in self.cache:
            cached_result, timestamp = self.cache[key]
            if ttl is None or (time.time() - timestamp) < ttl:
                return cached_result

        # 执行函数
        result = func(*args, **kwargs)

        # 更新缓存
        self.cache[key] = (result, time.time())

        # 清理缓存
        self._clean_cache()

        return result

    async def _execute_async(self, func: Callable, args: tuple, kwargs: dict) -> Any:
        """执行异步函数

        Args:
            func: 被装饰的函数
            args: 位置参数
            kwargs: 关键字参数

        Returns:
            Any: 函数执行结果
        """
        key = _make_cache_key(args, kwargs, self.config.get('typed', False))
        ttl = self.config.get('ttl')

        # 检查缓存
        if key in self.cache:
            cached_result, timestamp = self.cache[key]
            if ttl is None or (asyncio.get_running_loop().time() - timestamp) < ttl:
                return cached_result

        # 执行函数
        result = await func(*args, **kwargs)

        # 更新缓存
        self.cache[key] = (result, asyncio.get_running_loop().time())

        # 清理缓存
        self._clean_cache()

        return result

    def _clean_cache(self) -> None:
        """清理缓存"""
        maxsize = self.config.get('maxsize', 128)
        ttl = self.config.get('ttl')

        # 使用更安全的方式获取当前时间，兼容Python 3.14
        try:
            # 尝试获取事件循环时间（仅在异步上下文中）
            loop = asyncio.get_running_loop()
            current_time = loop.time()
        except RuntimeError:
            # 如果没有运行的事件循环，使用系统时间
            current_time = time.time()

        # 清理过期缓存
        if ttl is not None:
            expired_keys = [k for k, (_, timestamp) in self.cache.items() if current_time - timestamp >= ttl]
            for key in expired_keys:
                self.cache.pop(key, None)

        # 限制缓存大小
        if maxsize is not None and len(self.cache) > maxsize:
            # 移除最旧的缓存项
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            self.cache.pop(oldest_key)


__all__ = ['cache_wrapper']
