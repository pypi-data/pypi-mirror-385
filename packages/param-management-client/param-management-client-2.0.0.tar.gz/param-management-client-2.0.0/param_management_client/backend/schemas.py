"""
Pydantic模型定义
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
from enum import Enum

class ParameterType(str, Enum):
    """参数类型枚举"""
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    STRING = "string"

class BackupType(str, Enum):
    """备份类型枚举"""
    FULL = "full"
    PROJECT = "project"

# 基础模型
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100, description="项目中文名称")
    name_en: str = Field(..., max_length=100, description="项目英文名称")
    description: Optional[str] = Field(None, description="项目描述")
    time_horizon: int = Field(..., gt=0, description="时间长度")
    start_year: int = Field(..., description="起始年份")
    year_step: int = Field(..., gt=0, description="年份步长")
    end_year: int = Field(..., description="结束年份")
    
    @validator('end_year')
    def validate_end_year(cls, v, values):
        if 'start_year' in values and 'year_step' in values:
            start_year = values['start_year']
            year_step = values['year_step']
            expected_end_year = start_year + (v - start_year) // year_step * year_step
            if v != expected_end_year:
                raise ValueError(f"结束年份 {v} 不符合起始年份 {start_year} 和步长 {year_step} 的计算规则")
        return v
    
    @validator('time_horizon')
    def validate_time_horizon(cls, v, values):
        if 'start_year' in values and 'end_year' in values:
            start_year = values['start_year']
            end_year = values['end_year']
            if 'year_step' in values:
                year_step = values['year_step']
                expected_horizon = (end_year - start_year) // year_step + 1
                if v != expected_horizon:
                    raise ValueError(f"时间长度 {v} 与起始年份 {start_year}、结束年份 {end_year}、步长 {year_step} 不匹配")
        return v

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="项目中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="项目英文名称")
    description: Optional[str] = Field(None, description="项目描述")
    # 不允许修改时间相关字段
    time_horizon: Optional[int] = Field(None, gt=0, description="时间长度（不支持更新）")
    start_year: Optional[int] = Field(None, description="起始年份（不支持更新）")
    year_step: Optional[int] = Field(None, gt=0, description="年份步长（不支持更新）")
    end_year: Optional[int] = Field(None, description="结束年份（不支持更新）")

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectList(BaseModel):
    id: int
    name: str
    name_en: str
    description: Optional[str]
    time_horizon: int
    start_year: int
    year_step: int
    end_year: int
    created_at: datetime
    updated_at: datetime
    category_count: int = 0
    parameter_count: int = 0
    
    class Config:
        from_attributes = True

# 参数分类模型
class ParameterCategoryBase(BaseModel):
    name: str = Field(..., max_length=100, description="分类中文名称")
    name_en: str = Field(..., max_length=100, description="分类英文名称")
    description: Optional[str] = Field(None, description="分类描述")

class ParameterCategoryCreate(ParameterCategoryBase):
    pass

class ParameterCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="分类中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="分类英文名称")
    description: Optional[str] = Field(None, description="分类描述")

class ParameterCategory(ParameterCategoryBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 参数模型
class ParameterBase(BaseModel):
    name: str = Field(..., max_length=100, description="参数中文名称")
    name_en: str = Field(..., max_length=100, description="参数英文名称")
    param_type: ParameterType = Field(..., description="参数类型")
    unit: Optional[str] = Field(None, max_length=50, description="参数单位")
    description: Optional[str] = Field(None, description="参数描述")
    is_list: bool = Field(False, description="是否为列表参数")
    is_year_related: bool = Field(False, description="是否关联年份（仅列表参数有效）")
    # 已删除：default_value, min_value, max_value, is_required, validation_rule
    
    @validator('is_year_related')
    def validate_year_related(cls, v, values):
        if v and not values.get('is_list', False):
            raise ValueError("只有列表参数才能关联年份")
        return v

class ParameterCreate(ParameterBase):
    pass

class ParameterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="参数中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="参数英文名称")
    unit: Optional[str] = Field(None, max_length=50, description="参数单位")
    description: Optional[str] = Field(None, description="参数描述")
    # 不允许修改年份关联字段，防止数据不一致

class Parameter(ParameterBase):
    id: int
    category_id: int
    list_length: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 参数值模型
class ParameterValueBase(BaseModel):
    value: str = Field(..., description="参数值")
    list_index: Optional[int] = Field(None, description="列表索引")

class ParameterValueCreate(ParameterValueBase):
    pass

class ParameterValueUpdate(BaseModel):
    value: str = Field(..., description="参数值")

class ParameterValue(ParameterValueBase):
    id: int
    parameter_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ParameterValueBatch(BaseModel):
    values: List[str] = Field(..., description="批量参数值列表")

# 参数详情模型（包含值）
class ParameterDetail(Parameter):
    values: List[ParameterValue] = []
    current_value: Optional[str] = None
    current_values: Optional[List[str]] = None

# 分类详情模型（包含参数）
class ParameterCategoryDetail(ParameterCategory):
    parameters: List[ParameterDetail] = []

# 项目详情模型（包含分类）
class ProjectDetail(Project):
    categories: List[ParameterCategoryDetail] = []

# API响应模型
class ParameterDict(BaseModel):
    """用于API返回的参数字典格式"""
    data: Dict[str, Any] = Field(..., description="参数字典数据")
    metadata: Dict[str, Any] = Field(..., description="元数据信息")

# 备份模型
class BackupBase(BaseModel):
    backup_type: BackupType = Field(..., description="备份类型")
    description: Optional[str] = Field(None, description="备份描述")
    project_id: Optional[int] = Field(None, description="项目ID")

class BackupCreate(BackupBase):
    pass

class Backup(BackupBase):
    id: int
    file_path: str
    file_size: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class BackupRestore(BaseModel):
    restore_type: BackupType = Field(..., description="恢复类型")

# 通用响应模型
class MessageResponse(BaseModel):
    message: str = Field(..., description="响应消息")
    success: bool = Field(True, description="是否成功")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")
