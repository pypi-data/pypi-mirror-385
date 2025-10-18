"""
IO 格式插件包
- 约定：每种格式一个子目录，例如 excel/、excel_rich/
- 子目录内包含 exporter.py 和/或 importer.py，并在模块加载时调用注册函数完成注册
"""

from . import registry  # noqa: F401

__all__ = [
    "registry",
]
