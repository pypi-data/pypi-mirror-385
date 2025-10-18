"""
导出工具兼容层：转发到 io_formats 插件框架。
"""
from typing import List


class ExportFactory:
    @staticmethod
    def create_exporter(format_type: str):
        from io_formats.registry import get_exporter
        return get_exporter(format_type)

    @staticmethod
    def get_supported_formats() -> List[str]:
        from io_formats.registry import supported_export_formats
        return supported_export_formats()
