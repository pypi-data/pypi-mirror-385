"""
参数导入工具模块（与导出对称）
支持多格式导入（当前实现：Excel），并可创建全新的SQLite数据库文件。
提供内容一致性校验工具（基于逻辑数据对比，而非字节级）。
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from database import Base, Project, ParameterCategory, Parameter, ParameterValue


@dataclass
class ImportResult:
    project_name_en: str
    output_db_path: str
    categories_count: int
    parameters_count: int
    values_count: int


class ImportManager:
    """兼容层：将导入请求转发到已注册的 excel 插件。"""

    def import_project_from_excel_rich(self, excel_path: str, output_db_path: str) -> ImportResult:
        from io_formats.registry import get_importer
        importer = get_importer("excel_rich")
        return importer.import_project(excel_path, output_db_path)

    def import_into_current_db_from_excel_rich(self, db: Session, excel_path: str) -> Project:
        """将富格式Excel中的一个项目导入到当前运行数据库（解决重名冲突）。"""
        from io_formats.registry import get_importer
        importer = get_importer("excel_rich")
        # 复用插件实现，返回 Project
        return importer.import_into_current_db(db, excel_path)

        # 由插件实现
        # 保留兼容签名
        raise NotImplementedError


class ImportFactory:
    """导入格式工厂兼容层：转发到注册中心"""

    @staticmethod
    def create_importer(format_type: str):
        from io_formats.registry import get_importer
        return get_importer(format_type)

    @staticmethod
    def get_supported_formats() -> List[str]:
        from io_formats.registry import supported_import_formats
        return supported_import_formats()


def dump_database_as_dict(db_url: str, project_name_en: Optional[str] = None) -> Dict[str, Any]:
    """将数据库内容导出为规范字典（用于一致性比对）。"""
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        result: Dict[str, Any] = {"projects": []}
        query = db.query(Project)
        if project_name_en:
            query = query.filter(Project.name_en == project_name_en)
        projects = query.all()
        for p in projects:
            proj_dict: Dict[str, Any] = {
                "name": p.name,
                "name_en": p.name_en,
                "description": p.description,
                "time_horizon": p.time_horizon,
                "start_year": p.start_year,
                "year_step": p.year_step,
                "end_year": p.end_year,
                "categories": [],
            }
            categories = db.query(ParameterCategory).filter(ParameterCategory.project_id == p.id).all()
            for c in categories:
                cat_dict: Dict[str, Any] = {
                    "name": c.name,
                    "name_en": c.name_en,
                    "description": c.description,
                    "parameters": [],
                }
                params = db.query(Parameter).filter(Parameter.category_id == c.id).all()
                for prm in params:
                    param_dict: Dict[str, Any] = {
                        "name": prm.name,
                        "name_en": prm.name_en,
                        "param_type": prm.param_type,
                        "unit": prm.unit,
                        "description": prm.description,
                        "is_list": prm.is_list,
                        "is_year_related": prm.is_year_related,
                        "values": [],
                    }
                    vals = db.query(ParameterValue).filter(ParameterValue.parameter_id == prm.id).order_by(ParameterValue.list_index.nullsfirst()).all()
                    for v in vals:
                        param_dict["values"].append({
                            "list_index": v.list_index,
                            "value": v.value,
                        })
                    cat_dict["parameters"].append(param_dict)
                proj_dict["categories"].append(cat_dict)
            result["projects"].append(proj_dict)
        return result
    finally:
        db.close()


def compare_databases(db_url_a: str, db_url_b: str, project_name_en: Optional[str] = None) -> Tuple[bool, List[str]]:
    """比较两个数据库的逻辑内容是否一致。

    返回: (是否一致, 差异列表)
    """
    ia = dump_database_as_dict(db_url_a, project_name_en)
    ib = dump_database_as_dict(db_url_b, project_name_en)

    diffs: List[str] = []

    def sort_canonical(d: Dict[str, Any]) -> Dict[str, Any]:
        # 统一排序：按 name_en 排序，values 按 list_index 排
        for proj in d.get("projects", []):
            proj["categories"].sort(key=lambda x: x["name_en"])
            for cat in proj["categories"]:
                cat["parameters"].sort(key=lambda x: x["name_en"])
                for prm in cat["parameters"]:
                    prm["values"].sort(key=lambda x: (x["list_index"] is None, x["list_index"]))
        return d

    sa = sort_canonical(ia)
    sb = sort_canonical(ib)

    import json
    ja = json.dumps(sa, ensure_ascii=False, sort_keys=True)
    jb = json.dumps(sb, ensure_ascii=False, sort_keys=True)
    if ja == jb:
        return True, []

    # 简单差异提示（可扩展更细粒度）
    diffs.append("内容字典不一致。建议导出两边的json进一步diff。")
    return False, diffs


def compare_projects(project_a: Dict[str, Any], project_b: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """比较两个项目字典是否一致（按名称排序后对比）。
    
    Args:
        project_a: 项目A的字典数据
        project_b: 项目B的字典数据
        
    Returns:
        (是否一致, 差异列表)
    """
    def sort_project_canonical(proj: Dict[str, Any]) -> Dict[str, Any]:
        """对项目数据进行规范化排序"""
        proj["categories"].sort(key=lambda x: x["name_en"])
        for cat in proj["categories"]:
            cat["parameters"].sort(key=lambda x: x["name_en"])
            for prm in cat["parameters"]:
                prm["values"].sort(key=lambda x: (x["list_index"] is None, x["list_index"]))
        return proj
    
    sa = sort_project_canonical(project_a.copy())
    sb = sort_project_canonical(project_b.copy())
    
    import json
    ja = json.dumps(sa, ensure_ascii=False, sort_keys=True)
    jb = json.dumps(sb, ensure_ascii=False, sort_keys=True)
    
    if ja == jb:
        return True, []
    
    # 详细差异分析
    diffs = []
    
    # 项目基本信息对比
    for key in ["name", "name_en", "description", "time_horizon", "start_year", "year_step", "end_year"]:
        if sa.get(key) != sb.get(key):
            diffs.append(f"项目{key}: {sa.get(key)} != {sb.get(key)}")
    
    # 分类对比
    cats_a = {cat["name_en"]: cat for cat in sa["categories"]}
    cats_b = {cat["name_en"]: cat for cat in sb["categories"]}
    
    all_cats = set(cats_a.keys()) | set(cats_b.keys())
    for cat_name in sorted(all_cats):
        if cat_name not in cats_a:
            diffs.append(f"分类缺失: {cat_name} 在项目A中不存在")
        elif cat_name not in cats_b:
            diffs.append(f"分类缺失: {cat_name} 在项目B中不存在")
        else:
            # 参数对比
            params_a = {p["name_en"]: p for p in cats_a[cat_name]["parameters"]}
            params_b = {p["name_en"]: p for p in cats_b[cat_name]["parameters"]}
            
            all_params = set(params_a.keys()) | set(params_b.keys())
            for param_name in sorted(all_params):
                if param_name not in params_a:
                    diffs.append(f"参数缺失: {cat_name}.{param_name} 在项目A中不存在")
                elif param_name not in params_b:
                    diffs.append(f"参数缺失: {cat_name}.{param_name} 在项目B中不存在")
                else:
                    # 参数值对比
                    values_a = [v["value"] for v in params_a[param_name]["values"]]
                    values_b = [v["value"] for v in params_b[param_name]["values"]]
                    if values_a != values_b:
                        diffs.append(f"参数值不同: {cat_name}.{param_name} {values_a} != {values_b}")
    
    return False, diffs