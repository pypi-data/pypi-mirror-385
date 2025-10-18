"""
数据库操作函数
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from .database import Project, ParameterCategory, Parameter, ParameterValue, Backup
from .schemas import (
    ProjectCreate, ProjectUpdate, 
    ParameterCategoryCreate, ParameterCategoryUpdate,
    ParameterCreate, ParameterUpdate,
    ParameterValueCreate, ParameterValueUpdate, ParameterValueBatch
)
import json

# 项目管理
def create_project(db: Session, project: ProjectCreate) -> Project:
    """创建项目"""
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int) -> Optional[Project]:
    """根据ID获取项目"""
    return db.query(Project).filter(Project.id == project_id).first()

def get_project_by_name_en(db: Session, name_en: str) -> Optional[Project]:
    """根据英文名称获取项目"""
    return db.query(Project).filter(Project.name_en == name_en).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """获取项目列表"""
    return db.query(Project).offset(skip).limit(limit).all()

def get_projects_with_counts(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """获取项目列表（包含统计信息）"""
    projects = db.query(Project).offset(skip).limit(limit).all()
    result = []
    for project in projects:
        category_count = db.query(ParameterCategory).filter(ParameterCategory.project_id == project.id).count()
        parameter_count = db.query(Parameter).join(ParameterCategory).filter(ParameterCategory.project_id == project.id).count()
        result.append({
            "id": project.id,
            "name": project.name,
            "name_en": project.name_en,
            "description": project.description,
            "time_horizon": project.time_horizon,
            "start_year": project.start_year,
            "year_step": project.year_step,
            "end_year": project.end_year,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "category_count": category_count,
            "parameter_count": parameter_count
        })
    return result

def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
    """更新项目"""
    db_project = get_project(db, project_id)
    if db_project:
        update_data = project_update.dict(exclude_unset=True)
        # 禁止修改时间相关字段
        time_fields = ['time_horizon', 'start_year', 'year_step', 'end_year']
        for field in time_fields:
            if field in update_data:
                update_data.pop(field, None)
        # 允许修改英文名，需要保证唯一
        if 'name_en' in update_data:
            exists = db.query(Project).filter(Project.name_en == update_data['name_en'], Project.id != project_id).first()
            if exists:
                # 冲突则忽略该字段（也可抛错，这里保持兼容）
                update_data.pop('name_en', None)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int) -> bool:
    """删除项目"""
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

# 参数分类管理
def create_parameter_category(db: Session, category: ParameterCategoryCreate, project_id: int) -> ParameterCategory:
    """创建参数分类"""
    db_category = ParameterCategory(**category.dict(), project_id=project_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_parameter_category(db: Session, category_id: int) -> Optional[ParameterCategory]:
    """根据ID获取参数分类"""
    return db.query(ParameterCategory).filter(ParameterCategory.id == category_id).first()

def get_parameter_category_by_name_en(db: Session, project_id: int, name_en: str) -> Optional[ParameterCategory]:
    """根据英文名称获取参数分类"""
    return db.query(ParameterCategory).filter(
        and_(ParameterCategory.project_id == project_id, ParameterCategory.name_en == name_en)
    ).first()

def get_parameter_categories(db: Session, project_id: int) -> List[ParameterCategory]:
    """获取项目的参数分类列表"""
    return db.query(ParameterCategory).filter(ParameterCategory.project_id == project_id).order_by(ParameterCategory.created_at).all()

def get_parameter_categories_with_counts(db: Session, project_id: int) -> List[Dict[str, Any]]:
    """获取项目的参数分类列表（包含统计信息）"""
    categories = db.query(ParameterCategory).filter(ParameterCategory.project_id == project_id).order_by(ParameterCategory.created_at).all()
    result = []
    for category in categories:
        parameter_count = db.query(Parameter).filter(Parameter.category_id == category.id).count()
        result.append({
            "id": category.id,
            "name": category.name,
            "name_en": category.name_en,
            "description": category.description,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "parameter_count": parameter_count
        })
    return result

def update_parameter_category(db: Session, category_id: int, category_update: ParameterCategoryUpdate) -> Optional[ParameterCategory]:
    """更新参数分类"""
    db_category = get_parameter_category(db, category_id)
    if db_category:
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_parameter_category(db: Session, category_id: int) -> bool:
    """删除参数分类"""
    db_category = get_parameter_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False

# 参数管理
def create_parameter(db: Session, parameter: ParameterCreate, category_id: int, project_time_horizon: int) -> Parameter:
    """创建参数"""
    db_parameter = Parameter(**parameter.dict(), category_id=category_id)
    
    # 如果是列表参数，根据是否关联年份设置列表长度
    if db_parameter.is_list:
        if db_parameter.is_year_related:
            # 关联年份的列表参数，长度设为项目时间长度
            db_parameter.list_length = project_time_horizon
        else:
            # 不关联年份的列表参数，初始长度为0（还没有添加数据）
            db_parameter.list_length = 0
    
    # 如果关联年份，确保是列表参数
    if db_parameter.is_year_related and not db_parameter.is_list:
        raise ValueError("只有列表参数才能关联年份")
    
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter

def get_parameter(db: Session, parameter_id: int) -> Optional[Parameter]:
    """根据ID获取参数"""
    return db.query(Parameter).filter(Parameter.id == parameter_id).first()

def get_parameter_by_name_en(db: Session, category_id: int, name_en: str) -> Optional[Parameter]:
    """根据英文名称获取参数"""
    return db.query(Parameter).filter(
        and_(Parameter.category_id == category_id, Parameter.name_en == name_en)
    ).first()

def get_parameters(db: Session, category_id: int) -> List[Parameter]:
    """获取分类下的参数列表"""
    return db.query(Parameter).filter(Parameter.category_id == category_id).all()

def get_parameters_simple(db: Session, category_id: int) -> List[Parameter]:
    """获取分类下的参数列表（简单版本，用于API）"""
    return db.query(Parameter).filter(Parameter.category_id == category_id).all()

def get_parameters_with_values(db: Session, category_id: int) -> List[Dict[str, Any]]:
    """获取分类下的参数列表（包含值）"""
    parameters = db.query(Parameter).filter(Parameter.category_id == category_id).all()
    result = []
    for param in parameters:
        values = db.query(ParameterValue).filter(ParameterValue.parameter_id == param.id).order_by(ParameterValue.list_index).all()
        
        param_dict = {
            "id": param.id,
            "name": param.name,
            "name_en": param.name_en,
            "param_type": param.param_type,
            "unit": param.unit,
            "description": param.description,
            "is_list": param.is_list,
            "is_year_related": param.is_year_related,
            "list_length": param.list_length,
            # 以下字段已废弃，不再返回
            "created_at": param.created_at,
            "updated_at": param.updated_at,
            "values": [{"id": v.id, "value": v.value, "list_index": v.list_index, "created_at": v.created_at, "updated_at": v.updated_at} for v in values]
        }
        
        # 设置当前值
        if param.is_list:
            param_dict["current_values"] = [v.value for v in sorted(values, key=lambda x: x.list_index or 0)]
        else:
            param_dict["current_value"] = values[0].value if values else None
        
        result.append(param_dict)
    return result

def update_parameter(db: Session, parameter_id: int, parameter_update: ParameterUpdate) -> Optional[Parameter]:
    """更新参数"""
    db_parameter = get_parameter(db, parameter_id)
    if db_parameter:
        update_data = parameter_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_parameter, field, value)
        db.commit()
        db.refresh(db_parameter)
    return db_parameter

def delete_parameter(db: Session, parameter_id: int) -> bool:
    """删除参数"""
    db_parameter = get_parameter(db, parameter_id)
    if db_parameter:
        db.delete(db_parameter)
        db.commit()
        return True
    return False

# 参数值管理
def set_parameter_value(db: Session, parameter_id: int, value: str, list_index: Optional[int] = None) -> ParameterValue:
    """设置参数值"""
    # 检查是否已存在相同的值记录
    existing_value = db.query(ParameterValue).filter(
        and_(ParameterValue.parameter_id == parameter_id, ParameterValue.list_index == list_index)
    ).first()
    
    if existing_value:
        existing_value.value = value
        db.commit()
        db.refresh(existing_value)
        result = existing_value
    else:
        db_value = ParameterValue(parameter_id=parameter_id, value=value, list_index=list_index)
        db.add(db_value)
        db.commit()
        db.refresh(db_value)
        result = db_value
    
    # 更新参数的列表长度
    update_parameter_list_length(db, parameter_id)
    
    return result

def set_parameter_values_batch(db: Session, parameter_id: int, values: List[str]) -> List[ParameterValue]:
    """批量设置列表参数值"""
    # 删除现有值
    db.query(ParameterValue).filter(ParameterValue.parameter_id == parameter_id).delete()
    
    # 添加新值
    result = []
    for i, value in enumerate(values):
        db_value = ParameterValue(parameter_id=parameter_id, value=value, list_index=i)
        db.add(db_value)
        result.append(db_value)
    
    db.commit()
    for value in result:
        db.refresh(value)
    
    # 更新参数的列表长度
    update_parameter_list_length(db, parameter_id)
    
    return result

def get_parameter_values(db: Session, parameter_id: int) -> List[ParameterValue]:
    """获取参数的所有值"""
    return db.query(ParameterValue).filter(ParameterValue.parameter_id == parameter_id).order_by(ParameterValue.list_index).all()

def delete_parameter_value(db: Session, parameter_id: int, value_id: int) -> bool:
    """删除参数值"""
    value = db.query(ParameterValue).filter(
        and_(ParameterValue.id == value_id, ParameterValue.parameter_id == parameter_id)
    ).first()
    
    if value:
        db.delete(value)
        db.commit()
        
        # 更新参数的列表长度
        update_parameter_list_length(db, parameter_id)
        
        return True
    return False

def update_parameter_list_length(db: Session, parameter_id: int) -> None:
    """更新参数的列表长度（基于实际参数值数量）"""
    parameter = db.query(Parameter).filter(Parameter.id == parameter_id).first()
    if not parameter or not parameter.is_list:
        return
    
    # 如果参数关联年份，列表长度应该保持为项目时间长度
    if parameter.is_year_related:
        return
    
    # 对于不关联年份的列表参数，根据实际参数值数量更新长度
    actual_count = db.query(ParameterValue).filter(ParameterValue.parameter_id == parameter_id).count()
    parameter.list_length = actual_count
    db.commit()

def get_project_parameters_dict(db: Session, project_name_en: str) -> Dict[str, Any]:
    """获取项目的参数字典（用于API）"""
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        return {}
    
    categories = get_parameter_categories(db, project.id)
    result = {}
    
    for category in categories:
        parameters = get_parameters_with_values(db, category.id)
        category_dict = {}
        
        for param in parameters:
            if param["is_list"]:
                # 列表参数
                values = param["current_values"] or []
                if param["param_type"] in ["integer", "float"]:
                    try:
                        casted = [float(v) for v in values]
                        if param["param_type"] == "integer":
                            casted = [int(float(v)) for v in values]
                        category_dict[param["name_en"]] = casted
                    except ValueError:
                        category_dict[param["name_en"]] = values
                elif param["param_type"] == "boolean":
                    category_dict[param["name_en"]] = [v.lower() in ['true', '1', 'yes'] for v in values]
                else:
                    category_dict[param["name_en"]] = values
            else:
                # 单个参数
                value = param["current_value"]
                if param["param_type"] in ["integer", "float"]:
                    try:
                        if value is None:
                            category_dict[param["name_en"]] = None
                        else:
                            num = float(value)
                            category_dict[param["name_en"]] = int(num) if param["param_type"] == "integer" else num
                    except (ValueError, TypeError):
                        category_dict[param["name_en"]] = value
                elif param["param_type"] == "boolean":
                    category_dict[param["name_en"]] = str(value).lower() in ['true', '1', 'yes']
                else:
                    category_dict[param["name_en"]] = value
        
        result[category.name_en] = category_dict
    
    return result

# 备份管理
def create_backup(db: Session, backup: dict) -> Backup:
    """创建备份记录"""
    db_backup = Backup(**backup)
    db.add(db_backup)
    db.commit()
    db.refresh(db_backup)
    return db_backup

def get_backups(db: Session, skip: int = 0, limit: int = 100) -> List[Backup]:
    """获取备份列表"""
    return db.query(Backup).order_by(Backup.created_at.desc()).offset(skip).limit(limit).all()

def get_backup(db: Session, backup_id: int) -> Optional[Backup]:
    """根据ID获取备份"""
    return db.query(Backup).filter(Backup.id == backup_id).first()
