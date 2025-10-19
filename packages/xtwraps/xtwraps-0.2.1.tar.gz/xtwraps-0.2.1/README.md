# XTWraps

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://badge.fury.io/py/xtwraps.svg)](https://pypi.org/project/xtwraps/)

## 项目简介

XTWraps 是一个功能强大的 Python 装饰器工具库，提供一系列实用的装饰器和工具函数，用于简化日常开发工作。

## 功能特性

### 核心功能

-   **统一装饰器接口**：简化同步/异步函数的装饰器实现
-   **日志记录装饰器**：提供函数调用的详细日志
-   **函数执行计时器**：监控同步/异步函数的执行时间
-   **自动重试机制**：优化网络请求和不稳定操作的成功率
-   **线程池执行器包装器**：简化异步执行同步函数，函数命名优化为更直观的名称
-   **单例模式实现**：提供多种单例装饰器和混入类
-   **缓存装饰器**：提供函数结果缓存功能
-   **类型检查和验证装饰器**：确保函数参数和返回值类型正确

### 设计特点

-   **统一的 API 设计**：简化装饰器使用体验
-   **自动识别并适配**：同步和异步函数无缝切换
-   **完整的异常捕获和处理机制**：提高代码健壮性
-   **符合现代 Python 类型注解规范**：增强代码可读性和 IDE 支持
-   **支持多种组合使用场景**：灵活应对不同需求
-   **线程安全的单例实现**：确保多线程环境下的安全性
-   **完整的类型提示支持**：提高开发效率和代码质量

## 安装方法

### 从 PyPI 安装（推荐）

```bash
pip install xtwraps
```

### 从源码安装

```bash
git clone https://github.com/sandorn/xtwraps.git
cd xtwraps
pip install -e .
```

### 开发环境安装

```bash
git clone https://github.com/sandorn/xtwraps.git
cd xtwraps
pip install -e ".[test]"
```

## 使用示例

### 1. 日志装饰器

```python
from xtwraps import log_wraps

@log_wraps
def add_numbers(a: int, b: int) -> int:
    return a + b

# 调用函数，会自动记录函数调用信息
result = add_numbers(5, 3)
```

### 2. 计时装饰器

```python
from xtwraps import timer_wraps

@timer_wraps
def slow_function():
    import time
    time.sleep(1)  # 模拟耗时操作
    return "完成"

# 调用函数，会自动记录执行时间
result = slow_function()
```

### 3. 异常处理装饰器

```python
from xtwraps import exc_wraps

@exc_wraps(re_raise=False, default_return=0)
def divide(a: int, b: int) -> float:
    return a / b

# 安全调用，即使除零也不会崩溃
result = divide(10, 0)  # 返回 0
```

### 4. 重试装饰器

```python
from xtwraps import retry_wraps

@retry_wraps(max_retries=3, delay=1)
def unstable_operation():
    # 模拟不稳定操作，可能会失败
    import random
    if random.random() < 0.7:
        raise ConnectionError("连接失败")
    return "操作成功"

# 调用函数，会自动重试失败的操作
result = unstable_operation()
```

### 5. 单例模式

```python
from xtwraps import singleton

@singleton
def get_database_connection():
    # 模拟数据库连接初始化
    print("初始化数据库连接...")
    return {"connection": "active"}

# 多次调用返回相同实例
conn1 = get_database_connection()
conn2 = get_database_connection()
assert conn1 is conn2
```

### 6. 缓存装饰器

```python
from xtwraps import cache_wrapper

@cache_wrapper(ttl=60)  # 缓存60秒
def expensive_computation(x: int, y: int) -> int:
    # 模拟耗时计算
    print(f"执行计算: {x} + {y}")
    return x + y

# 首次调用会执行计算并缓存结果
result1 = expensive_computation(10, 20)
# 再次调用会直接返回缓存结果，不执行计算
result2 = expensive_computation(10, 20)
```

## 更多示例

请查看 [examples](examples/) 目录下的示例文件，了解更多使用方法：

## 功能变化

### 版本 0.2.0 更新内容

-   **异常处理优化**：改进了 retry 模块中异常处理的逻辑，确保异常捕获和处理更加健壮
-   **爬虫专用重试装饰器**：新增了 spider_retry 装饰器，专为爬虫场景设计，支持更灵活的异常处理
-   **代码复用优化**：优化了装饰器实现，减少冗余代码，提高维护性
-   **JSON 响应处理**：修复了 JSON 响应处理中的错误，确保结果处理更加稳定
-   **参数检查增强**：增强了函数参数的类型检查，提高代码健壮性

### 版本 0.1.1 更新内容

-   **枚举类优化**：优化 BaseEnum 和 StrEnum 的使用方式和文档说明
-   **最佳实践更新**：提供异常处理和类型使用的最佳实践指南
-   **代码结构优化**：进一步优化模块组织，提高代码可读性和可维护性
-   **文档完善**：更新功能说明和使用注意事项

### 版本 0.1.0 更新内容

-   **API 稳定性提升**：所有核心 API 已稳定，适合生产环境使用
-   **代码质量优化**：全面通过 ruff 和 basedPyright 检查，代码风格统一
-   **文档完善**：更新使用示例和 API 说明，提高用户体验
-   **性能改进**：优化内部实现，提高装饰器执行效率
-   **依赖管理优化**：更新依赖版本，提高兼容性

### 版本 0.0.9 更新内容

-   **函数命名优化**：重构 executor 模块，将复杂的函数名改为更直观的名称
    -   `executor_wraps` → `async_executor`：异步执行器装饰器，更明确地表达其异步执行功能
    -   `run_executor_wraps` → `syncify`：同步化装饰器，将异步函数转换为同步函数
    -   `future_wraps` → `to_future`：将普通函数返回值包装为 Future 对象
    -   `future_wraps_result` → `await_future_with_timeout`：带超时的 Future 等待函数
-   **代码结构优化**：移除冗余类定义，将功能转换为独立函数，提高代码可读性
-   **文档更新**：完善函数文档和类型注解，符合现代 Python 编码规范

## 版本更新日志

### v0.2.1 (2025-10-19)

**新功能：**

-   整合所有依赖到 `pyproject.toml` 中，简化依赖管理
-   移除 `wrapped.py` 模块，相关功能已整合到其他模块
-   优化类型注解，提升 IDE 支持

**改进：**

-   更新所有示例代码，移除对已删除模块的依赖
-   完善项目文档和安装说明
-   修复 Python 3.14 兼容性问题

**依赖更新：**

-   添加 `aiohttp>=3.10.0` 支持异步 HTTP 请求
-   添加 `tenacity>=8.2.0` 增强重试机制
-   添加 `requests>=2.32.3` 支持同步 HTTP 请求

### v0.2.0 (2025-10-01)

**重大更新：**

-   项目重命名：`nswrapslite` → `xtwraps`
-   更新 GitHub 仓库地址
-   完善所有模块的文档和示例

## 开发要求

-   Python 3.13+
-   依赖项已整合到 `pyproject.toml` 中

## 贡献指南

欢迎提交问题和改进建议！如果您想为项目贡献代码，请遵循以下步骤：

1. Fork 项目仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 作者

**sandorn**

-   GitHub: [@sandorn](https://github.com/sandorn)
-   Email: sandorn@live.cn
