from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ...database import Base, Project, ParameterCategory, Parameter, ParameterValue
from ...io_formats.registry import register_importer


@dataclass
class ImportResult:
    project_name_en: str
    output_db_path: str
    categories_count: int
    parameters_count: int
    values_count: int


@register_importer("json")
class JsonImporter:
    def import_project(self, json_path: str, output_db_path: str) -> ImportResult:
        """从JSON文件导入项目到新数据库"""
        json_file = Path(json_path)
        if not json_file.exists():
            raise FileNotFoundError(f"JSON文件不存在: {json_path}")
        
        # 创建新数据库
        db_path = Path(output_db_path)
        if db_path.exists():
            db_path.unlink()
        
        engine = create_engine(f"sqlite:///{db_path}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        db: Session = SessionLocal()
        
        try:
            # 读取JSON数据
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 创建项目
            project_info = data["project"]
            project = Project(
                name=project_info["name"],
                name_en=project_info["name_en"],
                description=project_info.get("description"),
                time_horizon=project_info["time_horizon"],
                start_year=project_info["start_year"],
                year_step=project_info["year_step"],
                end_year=project_info["end_year"],
            )
            db.add(project)
            db.flush()
            
            categories_count = 0
            parameters_count = 0
            values_count = 0
            
            # 处理分类和参数
            for category_data in data["categories"]:
                category = ParameterCategory(
                    project_id=project.id,
                    name=category_data["name"],
                    name_en=category_data["name_en"],
                    description=category_data.get("description"),
                )
                db.add(category)
                db.flush()
                categories_count += 1
                
                # 处理参数
                for param_data in category_data["parameters"]:
                    parameter = Parameter(
                        category_id=category.id,
                        name=param_data["name"],
                        name_en=param_data["name_en"],
                        param_type=param_data["param_type"],
                        unit=param_data.get("unit"),
                        description=param_data.get("description"),
                        is_list=param_data["is_list"],
                        is_year_related=param_data["is_year_related"],
                        list_length=param_data.get("list_length"),
                    )
                    db.add(parameter)
                    db.flush()
                    parameters_count += 1
                    
                    # 处理参数值
                    for value_data in param_data["values"]:
                        if value_data["value"] is not None:
                            param_value = ParameterValue(
                                parameter_id=parameter.id,
                                value=value_data["value"],
                                list_index=value_data["index"]
                            )
                            db.add(param_value)
                            values_count += 1
                
                db.commit()
            
            return ImportResult(
                project_name_en=project.name_en,
                output_db_path=str(db_path),
                categories_count=categories_count,
                parameters_count=parameters_count,
                values_count=values_count,
            )
        finally:
            db.close()

    def import_into_current_db(self, db: Session, json_path: str) -> Project:
        """从JSON文件导入项目到当前数据库"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理项目重名
        project_info = data["project"]
        base_name = project_info["name"]
        base_name_en = project_info["name_en"]
        new_name = base_name
        new_name_en = base_name_en
        
        from ...database import Project as DBProject
        suffix = 0
        while db.query(DBProject).filter(DBProject.name_en == new_name_en).first() is not None:
            suffix += 1
            new_name = f"{base_name} 副本{suffix}"
            new_name_en = f"{base_name_en}_copy{suffix}"
        
        # 创建项目
        project = Project(
            name=new_name,
            name_en=new_name_en,
            description=project_info.get("description"),
            time_horizon=project_info["time_horizon"],
            start_year=project_info["start_year"],
            year_step=project_info["year_step"],
            end_year=project_info["end_year"],
        )
        db.add(project)
        db.flush()
        
        # 处理分类和参数
        for category_data in data["categories"]:
            category = ParameterCategory(
                project_id=project.id,
                name=category_data["name"],
                name_en=category_data["name_en"],
                description=category_data.get("description"),
            )
            db.add(category)
            db.flush()
            
            # 处理参数
            for param_data in category_data["parameters"]:
                parameter = Parameter(
                    category_id=category.id,
                    name=param_data["name"],
                    name_en=param_data["name_en"],
                    param_type=param_data["param_type"],
                    unit=param_data.get("unit"),
                    description=param_data.get("description"),
                    is_list=param_data["is_list"],
                    is_year_related=param_data["is_year_related"],
                    list_length=param_data.get("list_length"),
                )
                db.add(parameter)
                db.flush()
                
                # 处理参数值
                for value_data in param_data["values"]:
                    if value_data["value"] is not None:
                        param_value = ParameterValue(
                            parameter_id=parameter.id,
                            value=value_data["value"],
                            list_index=value_data["index"]
                        )
                        db.add(param_value)
        
        db.commit()
        return project
