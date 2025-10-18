"""
项目一致性校验模块
用于生成项目的哈希值，确保导入导出的一致性
"""
import hashlib
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..database import Project, ParameterCategory, Parameter, ParameterValue


class ProjectConsistencyValidator:
    """项目一致性校验器"""
    
    @staticmethod
    def generate_project_hash(project: Project, db_session: Session) -> str:
        """
        生成项目的哈希值，用于一致性校验
        
        Args:
            project: 项目对象
            db_session: 数据库会话
            
        Returns:
            str: 项目的SHA256哈希值
        """
        # 构建项目的核心数据结构（不包含时间戳等元数据）
        project_data = ProjectConsistencyValidator._build_project_data(project, db_session)
        
        # 将数据转换为JSON字符串（确保顺序一致）
        json_str = json.dumps(project_data, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        
        # 生成SHA256哈希
        hash_obj = hashlib.sha256()
        hash_obj.update(json_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def _build_project_data(project: Project, db_session: Session) -> Dict[str, Any]:
        """
        构建项目的核心数据结构
        
        Args:
            project: 项目对象
            db_session: 数据库会话
            
        Returns:
            Dict[str, Any]: 项目的核心数据
        """
        # 项目基本信息（不包含id、created_at、updated_at、name、name_en）
        # 对于导入导出一致性校验，项目名称可能不同，所以不包含在哈希中
        project_info = {
            "description": project.description,
            "time_horizon": project.time_horizon,
            "start_year": project.start_year,
            "year_step": project.year_step,
            "end_year": project.end_year
        }
        
        # 获取所有分类（按name_en排序确保顺序一致）
        categories = db_session.query(ParameterCategory).filter(
            ParameterCategory.project_id == project.id
        ).order_by(ParameterCategory.name_en).all()
        
        categories_data = []
        for category in categories:
            category_info = {
                "name": category.name,
                "name_en": category.name_en,
                "description": category.description,
                "parameters": []
            }
            
            # 获取分类下的所有参数（按name_en排序确保顺序一致）
            parameters = db_session.query(Parameter).filter(
                Parameter.category_id == category.id
            ).order_by(Parameter.name_en).all()
            
            for parameter in parameters:
                parameter_info = {
                    "name": parameter.name,
                    "name_en": parameter.name_en,
                    "param_type": parameter.param_type,
                    "unit": parameter.unit,
                    "description": parameter.description,
                    "is_list": parameter.is_list,
                    "is_year_related": parameter.is_year_related,
                    "list_length": parameter.list_length,
                    "values": []
                }
                
                # 获取参数的所有值（按list_index排序确保顺序一致）
                values = db_session.query(ParameterValue).filter(
                    ParameterValue.parameter_id == parameter.id
                ).order_by(ParameterValue.list_index.asc().nullsfirst()).all()
                
                for value in values:
                    value_info = {
                        "value": value.value,
                        "list_index": value.list_index
                    }
                    parameter_info["values"].append(value_info)
                
                category_info["parameters"].append(parameter_info)
            
            categories_data.append(category_info)
        
        return {
            "project": project_info,
            "categories": categories_data
        }
    
    @staticmethod
    def compare_project_hashes(hash1: str, hash2: str) -> bool:
        """
        比较两个项目的哈希值是否一致
        
        Args:
            hash1: 第一个项目的哈希值
            hash2: 第二个项目的哈希值
            
        Returns:
            bool: 是否一致
        """
        return hash1 == hash2
    
    @staticmethod
    def validate_project_consistency(original_project: Project, 
                                   imported_project: Project, 
                                   db_session: Session) -> Dict[str, Any]:
        """
        验证两个项目的一致性
        
        Args:
            original_project: 原始项目
            imported_project: 导入的项目
            db_session: 数据库会话
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        original_hash = ProjectConsistencyValidator.generate_project_hash(original_project, db_session)
        imported_hash = ProjectConsistencyValidator.generate_project_hash(imported_project, db_session)
        
        is_consistent = ProjectConsistencyValidator.compare_project_hashes(original_hash, imported_hash)
        
        return {
            "is_consistent": is_consistent,
            "original_hash": original_hash,
            "imported_hash": imported_hash,
            "original_project_name": original_project.name,
            "imported_project_name": imported_project.name
        }


def generate_project_checksum(project_name_en: str, db_session: Session) -> str:
    """
    为指定项目生成校验和
    
    Args:
        project_name_en: 项目英文名称
        db_session: 数据库会话
        
    Returns:
        str: 项目的校验和
        
    Raises:
        ValueError: 如果项目不存在
    """
    project = db_session.query(Project).filter(Project.name_en == project_name_en).first()
    if not project:
        raise ValueError(f"项目 '{project_name_en}' 不存在")
    
    return ProjectConsistencyValidator.generate_project_hash(project, db_session)


def validate_import_consistency(original_project_name_en: str, 
                               imported_project_name_en: str, 
                               db_session: Session) -> Dict[str, Any]:
    """
    验证导入项目与原始项目的一致性
    
    Args:
        original_project_name_en: 原始项目英文名称
        imported_project_name_en: 导入项目英文名称
        db_session: 数据库会话
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    original_project = db_session.query(Project).filter(Project.name_en == original_project_name_en).first()
    if not original_project:
        raise ValueError(f"原始项目 '{original_project_name_en}' 不存在")
    
    imported_project = db_session.query(Project).filter(Project.name_en == imported_project_name_en).first()
    if not imported_project:
        raise ValueError(f"导入项目 '{imported_project_name_en}' 不存在")
    
    return ProjectConsistencyValidator.validate_project_consistency(
        original_project, imported_project, db_session
    )
