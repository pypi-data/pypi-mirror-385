"""
参数管理系统 - FastAPI主应用
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
import json
from datetime import datetime
from pathlib import Path

from .database import get_db, create_tables 
from .schemas import (
    Project, ProjectCreate, ProjectUpdate, ProjectList,
    ParameterCategory, ParameterCategoryCreate, ParameterCategoryUpdate,
    Parameter, ParameterCreate, ParameterUpdate, ParameterDetail,
    ParameterValue, ParameterValueCreate, ParameterValueUpdate, ParameterValueBatch,
    ParameterDict, Backup, BackupCreate, BackupRestore,
    MessageResponse, ErrorResponse
)
from pydantic import BaseModel

class ConsistencyValidationRequest(BaseModel):
    original_project_name_en: str
    imported_project_name_en: str
from .crud import (
    # 项目管理
    create_project, get_project, get_project_by_name_en, get_projects_with_counts, update_project, delete_project,
    # 参数分类管理
    create_parameter_category, get_parameter_category, get_parameter_category_by_name_en, 
    get_parameter_categories, get_parameter_categories_with_counts, update_parameter_category, delete_parameter_category,
    # 参数管理
    create_parameter, get_parameter, get_parameter_by_name_en, get_parameters, get_parameters_simple, get_parameters_with_values,
    update_parameter, delete_parameter,
    # 参数值管理
    set_parameter_value, set_parameter_values_batch, get_parameter_values, delete_parameter_value,
    get_project_parameters_dict
)
from .io_formats.validation import generate_project_checksum, validate_import_consistency
from .io_formats.registry import (
    get_exporter,
    get_importer,
    supported_export_formats,
    supported_import_formats,
    collect_export_format_descriptors,
)
# 触发插件注册（导入子包以执行注册装饰器）
from .io_formats import registry as _io_registry  # noqa: F401
from .io_formats.excel_rich import exporter as _excel_rich_exporter  # noqa: F401
from .io_formats.excel_rich import importer as _excel_rich_importer  # noqa: F401
from .io_formats.json import exporter as _json_exporter  # noqa: F401
from .io_formats.json import importer as _json_importer  # noqa: F401
from .io_formats.text import exporter as _text_exporter  # noqa: F401
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

# 创建FastAPI应用
app = FastAPI(
    title="参数管理系统",
    description="优化建模项目参数管理平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 启用CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 创建数据库表
create_tables()
@app.get("/", response_model=MessageResponse)
async def root():
    return MessageResponse(message="参数管理系统API", success=True)

# ==================== 项目管理接口 ====================

@app.post("/api/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(project: ProjectCreate, db: Session = Depends(get_db)):
    """创建项目"""
    # 检查项目英文名称是否已存在
    existing_project = get_project_by_name_en(db, project.name_en)
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"项目英文名称 '{project.name_en}' 已存在"
        )
    
    return create_project(db, project)

@app.get("/api/projects", response_model=List[ProjectList])
async def get_projects_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取项目列表"""
    projects = get_projects_with_counts(db, skip=skip, limit=limit)
    return projects

@app.get("/api/projects/{project_name_en}", response_model=Project)
async def get_project_endpoint(project_name_en: str, db: Session = Depends(get_db)):
    """获取项目详情"""
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    return project

@app.put("/api/projects/{project_name_en}", response_model=Project)
async def update_project_endpoint(
    project_name_en: str, 
    project_update: ProjectUpdate, 
    db: Session = Depends(get_db)
):
    """更新项目"""
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    updated_project = update_project(db, project.id, project_update)
    return updated_project

@app.delete("/api/projects/{project_name_en}", response_model=MessageResponse)
async def delete_project_endpoint(project_name_en: str, db: Session = Depends(get_db)):
    """删除项目"""
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    success = delete_project(db, project.id)
    if success:
        return MessageResponse(message=f"项目 '{project_name_en}' 删除成功")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除项目失败"
        )

# ==================== 参数分类管理接口 ====================

@app.post("/api/projects/{project_name_en}/categories", response_model=ParameterCategory, status_code=status.HTTP_201_CREATED)
async def create_parameter_category_endpoint(
    project_name_en: str,
    category: ParameterCategoryCreate,
    db: Session = Depends(get_db)
):
    """创建参数分类"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类英文名称是否已存在
    existing_category = get_parameter_category_by_name_en(db, project.id, category.name_en)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分类英文名称 '{category.name_en}' 已存在"
        )
    
    return create_parameter_category(db, category, project.id)

@app.get("/api/projects/{project_name_en}/categories")
async def get_parameter_categories_endpoint(project_name_en: str, db: Session = Depends(get_db)):
    """获取参数分类列表"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    categories = get_parameter_categories(db, project.id)
    # 手动转换为字典
    result = []
    for cat in categories:
        result.append({
            "id": cat.id,
            "name": cat.name,
            "name_en": cat.name_en,
            "description": cat.description,
            "project_id": cat.project_id,
            "created_at": cat.created_at.isoformat() if cat.created_at else None,
            "updated_at": cat.updated_at.isoformat() if cat.updated_at else None
        })
    return result

@app.put("/api/projects/{project_name_en}/categories/{category_name_en}", response_model=ParameterCategory)
async def update_parameter_category_endpoint(
    project_name_en: str,
    category_name_en: str,
    category_update: ParameterCategoryUpdate,
    db: Session = Depends(get_db)
):
    """更新参数分类"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    updated_category = update_parameter_category(db, category.id, category_update)
    return updated_category

@app.delete("/api/projects/{project_name_en}/categories/{category_name_en}", response_model=MessageResponse)
async def delete_parameter_category_endpoint(
    project_name_en: str,
    category_name_en: str,
    db: Session = Depends(get_db)
):
    """删除参数分类"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    success = delete_parameter_category(db, category.id)
    if success:
        return MessageResponse(message=f"分类 '{category_name_en}' 删除成功")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除分类失败"
        )

# ==================== 参数管理接口 ====================

@app.post("/api/projects/{project_name_en}/categories/{category_name_en}/parameters", response_model=Parameter, status_code=status.HTTP_201_CREATED)
async def create_parameter_endpoint(
    project_name_en: str,
    category_name_en: str,
    parameter: ParameterCreate,
    db: Session = Depends(get_db)
):
    """创建参数"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    # 检查参数英文名称是否已存在
    existing_parameter = get_parameter_by_name_en(db, category.id, parameter.name_en)
    if existing_parameter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数英文名称 '{parameter.name_en}' 已存在"
        )
    
    return create_parameter(db, parameter, category.id, project.time_horizon)

@app.get("/api/projects/{project_name_en}/categories/{category_name_en}/parameters")
async def get_parameters_endpoint(
    project_name_en: str,
    category_name_en: str,
    db: Session = Depends(get_db)
):
    """获取参数列表"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    parameters = get_parameters_simple(db, category.id)
    # 手动转换为字典
    result = []
    for param in parameters:
        result.append({
            "id": param.id,
            "name": param.name,
            "name_en": param.name_en,
            "param_type": param.param_type,
            "unit": param.unit,
            "description": param.description,
            "is_list": param.is_list,
            "is_year_related": getattr(param, "is_year_related", False),
            "list_length": param.list_length,
            "category_id": param.category_id,
            "created_at": param.created_at.isoformat() if param.created_at else None,
            "updated_at": param.updated_at.isoformat() if param.updated_at else None
        })
    return result

@app.put("/api/projects/{project_name_en}/categories/{category_name_en}/parameters/{param_name_en}", response_model=Parameter)
async def update_parameter_endpoint(
    project_name_en: str,
    category_name_en: str,
    param_name_en: str,
    parameter_update: ParameterUpdate,
    db: Session = Depends(get_db)
):
    """更新参数"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    # 检查参数是否存在
    parameter = get_parameter_by_name_en(db, category.id, param_name_en)
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"参数 '{param_name_en}' 不存在"
        )
    
    updated_parameter = update_parameter(db, parameter.id, parameter_update)
    return updated_parameter

@app.delete("/api/projects/{project_name_en}/categories/{category_name_en}/parameters/{param_name_en}", response_model=MessageResponse)
async def delete_parameter_endpoint(
    project_name_en: str,
    category_name_en: str,
    param_name_en: str,
    db: Session = Depends(get_db)
):
    """删除参数"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    # 检查参数是否存在
    parameter = get_parameter_by_name_en(db, category.id, param_name_en)
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"参数 '{param_name_en}' 不存在"
        )
    
    success = delete_parameter(db, parameter.id)
    if success:
        return MessageResponse(message=f"参数 '{param_name_en}' 删除成功")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除参数失败"
        )

# ==================== 参数值管理接口 ====================

@app.post("/api/projects/{project_name_en}/categories/{category_name_en}/parameters/{param_name_en}/values", response_model=ParameterValue)
async def set_parameter_value_endpoint(
    project_name_en: str,
    category_name_en: str,
    param_name_en: str,
    value_data: ParameterValueCreate,
    db: Session = Depends(get_db)
):
    """设置参数值"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    # 检查参数是否存在
    parameter = get_parameter_by_name_en(db, category.id, param_name_en)
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"参数 '{param_name_en}' 不存在"
        )
    
    return set_parameter_value(db, parameter.id, value_data.value, value_data.list_index)

@app.post("/api/projects/{project_name_en}/categories/{category_name_en}/parameters/{param_name_en}/values/batch", response_model=List[ParameterValue])
async def set_parameter_values_batch_endpoint(
    project_name_en: str,
    category_name_en: str,
    param_name_en: str,
    values_data: ParameterValueBatch,
    db: Session = Depends(get_db)
):
    """批量设置列表参数值"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    # 检查参数是否存在
    parameter = get_parameter_by_name_en(db, category.id, param_name_en)
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"参数 '{param_name_en}' 不存在"
        )
    
    if not parameter.is_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有列表参数支持批量设置值"
        )
    
    return set_parameter_values_batch(db, parameter.id, values_data.values)

@app.get("/api/projects/{project_name_en}/categories/{category_name_en}/parameters/{param_name_en}/values", response_model=List[ParameterValue])
async def get_parameter_values_endpoint(
    project_name_en: str,
    category_name_en: str,
    param_name_en: str,
    db: Session = Depends(get_db)
):
    """获取参数值列表"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    # 检查参数是否存在
    parameter = get_parameter_by_name_en(db, category.id, param_name_en)
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"参数 '{param_name_en}' 不存在"
        )
    
    return get_parameter_values(db, parameter.id)

@app.delete("/api/projects/{project_name_en}/categories/{category_name_en}/parameters/{param_name_en}/values/{value_id}", response_model=MessageResponse)
async def delete_parameter_value_endpoint(
    project_name_en: str,
    category_name_en: str,
    param_name_en: str,
    value_id: int,
    db: Session = Depends(get_db)
):
    """删除参数值"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查分类是否存在
    category = get_parameter_category_by_name_en(db, project.id, category_name_en)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类 '{category_name_en}' 不存在"
        )
    
    # 检查参数是否存在
    parameter = get_parameter_by_name_en(db, category.id, param_name_en)
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"参数 '{param_name_en}' 不存在"
        )
    
    success = delete_parameter_value(db, parameter.id, value_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="参数值不存在"
        )
    
    return MessageResponse(message="参数值删除成功")

# ==================== 导出接口 ====================

@app.get("/api/projects/{project_name_en}/parameters", response_model=ParameterDict)
async def get_project_parameters_endpoint(project_name_en: str, db: Session = Depends(get_db)):
    """获取项目的完整参数字典（用于API调用）"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    parameters_dict = get_project_parameters_dict(db, project_name_en)
    
    # 添加元数据
    metadata = {
        "project_name": project.name,
        "project_name_en": project.name_en,
        "time_horizon": project.time_horizon,
        "start_year": project.start_year,
        "year_step": project.year_step,
        "end_year": project.end_year,
        "export_time": datetime.utcnow().isoformat(),
        "data_types": {}
    }
    
    # 添加数据类型信息
    for category_name, category_data in parameters_dict.items():
        metadata["data_types"][category_name] = {}
        for param_name, param_value in category_data.items():
            if isinstance(param_value, list):
                if param_value and isinstance(param_value[0], (int, float)):
                    metadata["data_types"][category_name][param_name] = {
                        "type": "list",
                        "element_type": "number" if isinstance(param_value[0], float) else "integer"
                    }
                else:
                    metadata["data_types"][category_name][param_name] = {
                        "type": "list",
                        "element_type": "string"
                    }
            elif isinstance(param_value, (int, float)):
                metadata["data_types"][category_name][param_name] = {
                    "type": "number" if isinstance(param_value, float) else "integer"
                }
            elif isinstance(param_value, bool):
                metadata["data_types"][category_name][param_name] = {
                    "type": "boolean"
                }
            else:
                metadata["data_types"][category_name][param_name] = {
                    "type": "string"
                }
    
    return ParameterDict(data=parameters_dict, metadata=metadata)

@app.get("/api/projects/{project_name_en}/parameters/detailed")
async def get_project_parameters_detailed_endpoint(project_name_en: str, db: Session = Depends(get_db)):
    """获取项目的详细参数信息（包含元数据）"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 获取项目信息
    project_info = {
        "id": project.id,
        "name": project.name,
        "name_en": project.name_en,
        "description": project.description,
        "time_horizon": project.time_horizon,
        "start_year": project.start_year,
        "year_step": project.year_step,
        "end_year": project.end_year,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None
    }
    
    # 获取分类和参数信息
    categories = get_parameter_categories(db, project.id)
    categories_data = {}
    
    for category in categories:
        parameters = get_parameters_with_values(db, category.id)
        category_params = {}
        
        for param in parameters:
            param_info = {
                "id": param["id"],
                "name": param["name"],
                "name_en": param["name_en"],
                "param_type": param["param_type"],
                "unit": param.get("unit"),
                "description": param.get("description"),
                "is_list": param["is_list"],
                "is_year_related": param["is_year_related"],
                "list_length": param.get("list_length"),
                "created_at": param["created_at"].isoformat() if param["created_at"] else None,
                "updated_at": param["updated_at"].isoformat() if param["updated_at"] else None
            }
            
            # 添加参数值
            if param["is_list"]:
                param_info["value"] = param["current_values"] or []
            else:
                param_info["value"] = param["current_value"]
            
            category_params[param["name_en"]] = param_info
        
        categories_data[category.name_en] = {
            "id": category.id,
            "name": category.name,
            "name_en": category.name_en,
            "description": category.description,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None,
            "parameters": category_params
        }
    
    return {
        "project": project_info,
        "categories": categories_data,
        "export_time": datetime.utcnow().isoformat()
    }

@app.get("/api/export/formats")
async def get_export_formats():
    """获取支持的导出格式列表"""
    return {"formats": collect_export_format_descriptors()}

@app.get("/api/import/formats")
async def get_import_formats():
    """获取支持的导入格式列表"""
    formats = []
    for format_type in supported_import_formats():
        # 根据格式类型返回对应的文件扩展名
        if format_type == "excel_rich":
            formats.append({
                "format": format_type,
                "name": "富格式Excel文件",
                "extensions": [".xlsx"],
                "description": "多sheet、超链接、富格式的Excel文件"
            })
        elif format_type == "json":
            formats.append({
                "format": format_type,
                "name": "JSON文件", 
                "extensions": [".json"],
                "description": "JSON数据格式文件"
            })
    return {"formats": formats}

@app.post("/api/projects/{project_name_en}/export/{format_type}")
async def export_project_parameters(
    project_name_en: str, 
    format_type: str, 
    db: Session = Depends(get_db)
):
    """导出项目参数"""
    # 检查项目是否存在
    project = get_project_by_name_en(db, project_name_en)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 '{project_name_en}' 不存在"
        )
    
    # 检查导出格式是否支持
    if format_type not in supported_export_formats():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的导出格式: {format_type}"
        )
    
    try:
        exporter = get_exporter(format_type)
        if not exporter:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建导出器失败"
            )
        file_path = exporter.export(project_name_en, db)
        
        # 检查文件是否存在
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="导出文件生成失败"
            )
        
        # 返回文件
        filename = Path(file_path).name
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


# ==================== 导入接口 ====================

@app.post("/api/import/{format_type}", response_model=MessageResponse)
async def import_project_parameters(
    format_type: str,
    excel_path: str,
):
    """从指定格式文件导入项目参数（支持excel和json）。

    注意：excel_path 为服务器可访问的文件路径。
    """
    if format_type not in supported_import_formats():
        raise HTTPException(status_code=400, detail=f"不支持的导入格式: {format_type}")
    importer = get_importer(format_type)
    try:
        # 输出数据库路径（临时命名）
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_db = f"imported_{ts}.db"
        result = importer.import_project(excel_path, output_db)
        return MessageResponse(message=f"导入完成，输出数据库: {result.output_db_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.post("/api/import/upload/{format_type}", response_model=MessageResponse)
async def import_by_upload(
    format_type: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """上传文件导入（支持excel和json）。根据后缀校验类型，不支持则拒绝。若重名，自动追加副本序号。"""
    raw = await request.body()
    filename = request.headers.get('X-Filename')
    if not raw or not filename:
        raise HTTPException(status_code=400, detail="未提供文件或文件名")

    allowed = {"excel": [".xlsx"], "excel_rich": [".xlsx"], "json": [".json"]}
    if format_type not in allowed:
        raise HTTPException(status_code=400, detail=f"不支持的导入格式: {format_type}")
    import os
    _, ext = os.path.splitext(filename)
    if ext.lower() not in allowed[format_type]:
        raise HTTPException(status_code=400, detail="文件类型不被支持或后缀不正确")

    # 保存到临时目录
    import tempfile
    tmp_dir = tempfile.mkdtemp()
    save_path = os.path.join(tmp_dir, filename)
    with open(save_path, "wb") as f:
        f.write(raw)

    try:
        importer = get_importer(format_type)
        if not importer:
            raise HTTPException(status_code=400, detail=f"不支持的导入格式: {format_type}")
        project = importer.import_into_current_db(db, save_path)
        return MessageResponse(message=f"导入完成：{project.name} ({project.name_en})")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"导入失败：{str(e)}")

# ==================== 项目一致性校验接口 ====================

@app.get("/api/projects/{project_name_en}/checksum")
async def get_project_checksum(project_name_en: str, db: Session = Depends(get_db)):
    """获取项目的校验哈希"""
    try:
        checksum = generate_project_checksum(project_name_en, db)
        return {"project_name_en": project_name_en, "checksum": checksum}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成校验哈希失败: {str(e)}")

@app.post("/api/projects/validate-consistency")
async def validate_project_consistency(
    request: ConsistencyValidationRequest,
    db: Session = Depends(get_db)
):
    """验证两个项目的一致性"""
    try:
        result = validate_import_consistency(request.original_project_name_en, request.imported_project_name_en, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证一致性失败: {str(e)}")

# ==================== 健康检查 ====================

@app.get("/health", response_model=MessageResponse)
async def health_check():
    """健康检查接口"""
    return MessageResponse(message="系统运行正常", success=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
