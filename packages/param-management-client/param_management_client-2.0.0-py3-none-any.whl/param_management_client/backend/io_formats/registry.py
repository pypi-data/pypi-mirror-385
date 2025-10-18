"""
导入/导出格式注册中心。
- 通过 register_exporter(format_type)(cls) 与 register_importer(format_type)(cls) 装饰器注册
- 统一接口：
  Exporter 必须实现：
    - export(project_name_en: str, db_session) -> str
    - get_export_formats() -> List[Dict[str, str]]
  Importer 必须实现：
    - import_project(input_path: str, output_db_path: str)
    - import_into_current_db(db_session, input_path: str)
"""
from typing import Dict, Type, List, Any, Callable

_exporters: Dict[str, Type] = {}
_importers: Dict[str, Type] = {}


def register_exporter(format_type: str) -> Callable[[Type], Type]:
    def _decorator(cls: Type) -> Type:
        _exporters[format_type] = cls
        return cls
    return _decorator


def register_importer(format_type: str) -> Callable[[Type], Type]:
    def _decorator(cls: Type) -> Type:
        _importers[format_type] = cls
        return cls
    return _decorator


def get_exporter(format_type: str):
    cls = _exporters.get(format_type)
    return cls() if cls else None


def get_importer(format_type: str):
    cls = _importers.get(format_type)
    return cls() if cls else None


def supported_export_formats() -> List[str]:
    return list(_exporters.keys())


def supported_import_formats() -> List[str]:
    return list(_importers.keys())


def collect_export_format_descriptors() -> List[Dict[str, Any]]:
    descriptors: List[Dict[str, Any]] = []
    for _, cls in _exporters.items():
        try:
            inst = cls()
            if hasattr(inst, "get_export_formats"):
                descriptors.extend(inst.get_export_formats())
        except Exception:
            pass
    return descriptors
