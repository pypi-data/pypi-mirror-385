"""
数据库配置和模型定义
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, UTC
import os

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./param_management.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Project(Base):
    """项目表"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="项目中文名称")
    name_en = Column(String(100), nullable=False, unique=True, index=True, comment="项目英文名称")
    description = Column(Text, comment="项目描述")
    time_horizon = Column(Integer, nullable=False, comment="时间长度")
    start_year = Column(Integer, nullable=False, comment="起始年份")
    year_step = Column(Integer, nullable=False, comment="年份步长")
    end_year = Column(Integer, nullable=False, comment="结束年份")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), comment="创建时间")
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), comment="更新时间")
    
    # 关系
    categories = relationship("ParameterCategory", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', name_en='{self.name_en}')>"

class ParameterCategory(Base):
    """参数分类表"""
    __tablename__ = "parameter_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, comment="分类中文名称")
    name_en = Column(String(100), nullable=False, comment="分类英文名称")
    description = Column(Text, comment="分类描述")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), comment="创建时间")
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="categories")
    parameters = relationship("Parameter", back_populates="category", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        UniqueConstraint('project_id', 'name_en', name='uq_project_category_name_en'),
    )
    
    def __repr__(self):
        return f"<ParameterCategory(id={self.id}, name='{self.name}', name_en='{self.name_en}')>"

class Parameter(Base):
    """参数表"""
    __tablename__ = "parameters"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("parameter_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, comment="参数中文名称")
    name_en = Column(String(100), nullable=False, comment="参数英文名称")
    param_type = Column(String(20), nullable=False, comment="参数类型: integer, float, boolean, string")
    unit = Column(String(50), comment="参数单位")
    description = Column(Text, comment="参数描述")
    is_list = Column(Boolean, default=False, comment="是否为列表参数")
    is_year_related = Column(Boolean, default=False, comment="是否关联年份（仅列表参数有效）")
    list_length = Column(Integer, comment="列表长度")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), comment="创建时间")
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), comment="更新时间")
    
    # 关系
    category = relationship("ParameterCategory", back_populates="parameters")
    values = relationship("ParameterValue", back_populates="parameter", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        UniqueConstraint('category_id', 'name_en', name='uq_category_parameter_name_en'),
        Index('idx_parameter_type', 'param_type'),
        Index('idx_parameter_list', 'is_list'),
        Index('idx_parameter_year_related', 'is_year_related'),
    )
    
    def __repr__(self):
        return f"<Parameter(id={self.id}, name='{self.name}', name_en='{self.name_en}', type='{self.param_type}')>"

class ParameterValue(Base):
    """参数值表 - 优化设计，支持单个值和列表值"""
    __tablename__ = "parameter_values"
    
    id = Column(Integer, primary_key=True, index=True)
    parameter_id = Column(Integer, ForeignKey("parameters.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(Text, nullable=False, comment="参数值")
    list_index = Column(Integer, comment="列表索引（列表参数使用，null表示单个值）")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), comment="创建时间")
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), comment="更新时间")
    
    # 关系
    parameter = relationship("Parameter", back_populates="values")
    
    # 约束
    __table_args__ = (
        Index('idx_parameter_value_list', 'parameter_id', 'list_index'),
    )
    
    def __repr__(self):
        return f"<ParameterValue(id={self.id}, parameter_id={self.parameter_id}, value='{self.value}', list_index={self.list_index})>"

class Backup(Base):
    """备份记录表"""
    __tablename__ = "backups"
    
    id = Column(Integer, primary_key=True, index=True)
    backup_type = Column(String(20), nullable=False, comment="备份类型: full, project")
    file_path = Column(String(255), nullable=False, comment="备份文件路径")
    file_size = Column(Integer, comment="文件大小")
    description = Column(Text, comment="备份描述")
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, comment="项目ID（项目备份时使用）")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), comment="创建时间")
    
    # 关系
    project = relationship("Project")
    
    def __repr__(self):
        return f"<Backup(id={self.id}, type='{self.backup_type}', file_path='{self.file_path}')>"

def create_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建表
if __name__ == "__main__":
    create_tables()
    print("数据库表创建完成！")
