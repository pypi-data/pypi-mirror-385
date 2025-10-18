"""
参数管理系统 Python 客户端
支持类似pandas DataFrame的点号访问方式
"""
import requests
import json
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urljoin
import logging
import os
import tempfile

from .exceptions import ParameterClientError, ParameterNotFoundError, CategoryNotFoundError, ProjectNotFoundError, ConnectionError

# 配置日志
logger = logging.getLogger(__name__)


class ParameterValue:
    """参数值对象，支持属性访问"""
    
    def __init__(self, param_data: Dict[str, Any]):
        self._data = param_data
        self._raw_value = param_data.get('value')
        self._param_type = param_data.get('param_type', 'string')
        self._is_list = param_data.get('is_list', False)
        
        # 根据参数类型转换值
        self._value = self._convert_value(self._raw_value)
    
    def _convert_value(self, raw_value):
        """根据参数类型转换值"""
        if raw_value is None:
            return None
        
        if self._is_list:
            # 列表参数
            if not isinstance(raw_value, list):
                return raw_value
            
            converted_list = []
            for item in raw_value:
                converted_item = self._convert_single_value(item)
                converted_list.append(converted_item)
            return converted_list
        else:
            # 单个参数
            return self._convert_single_value(raw_value)
    
    def _convert_single_value(self, value):
        """转换单个值"""
        if value is None:
            return None
        
        try:
            if self._param_type == 'integer':
                return int(float(value))  # 先转float再转int，处理"1.0"这种情况
            elif self._param_type == 'float':
                return float(value)
            elif self._param_type == 'boolean':
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ['true', '1', 'yes', 'on']
            else:  # string 或其他类型
                return str(value)
        except (ValueError, TypeError):
            # 转换失败时返回原始值
            return value
    
    @property
    def value(self):
        """参数值"""
        return self._value
    
    @property
    def unit(self):
        """参数单位"""
        return self._data.get('unit')
    
    @property
    def description(self):
        """参数描述"""
        return self._data.get('description')
    
    @property
    def name(self):
        """参数中文名称"""
        return self._data.get('name')
    
    @property
    def name_en(self):
        """参数英文名称"""
        return self._data.get('name_en')
    
    @property
    def param_type(self):
        """参数类型"""
        return self._param_type
    
    @property
    def is_list(self):
        """是否为列表参数"""
        return self._is_list
    
    @property
    def is_year_related(self):
        """是否关联年份"""
        return self._data.get('is_year_related', False)
    
    @property
    def list_length(self):
        """列表长度"""
        return self._data.get('list_length')
    
    def __str__(self):
        return str(self._value)
    
    def __repr__(self):
        return f"ParameterValue(name='{self.name_en}', value={self._value}, type='{self._param_type}')"
    
    def __getitem__(self, index):
        """支持列表索引访问"""
        if not self._is_list or not isinstance(self._value, list):
            raise TypeError(f"参数 '{self.name_en}' 不是列表类型")
        return self._value[index]
    
    def __len__(self):
        """支持len()函数"""
        if not self._is_list or not isinstance(self._value, list):
            return 1
        return len(self._value)
    
    def __iter__(self):
        """支持迭代"""
        if not self._is_list or not isinstance(self._value, list):
            return iter([self._value])
        return iter(self._value)
    
    # 算术运算符重载
    def __add__(self, other):
        """加法运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return other
        return self._value + other
    
    def __radd__(self, other):
        """右加法运算"""
        return self.__add__(other)
    
    def __sub__(self, other):
        """减法运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return -other if other is not None else None
        return self._value - other
    
    def __rsub__(self, other):
        """右减法运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return other
        return other - self._value
    
    def __mul__(self, other):
        """乘法运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 0
        return self._value * other
    
    def __rmul__(self, other):
        """右乘法运算"""
        return self.__mul__(other)
    
    def __truediv__(self, other):
        """除法运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 0
        if other == 0:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 除以零")
        return self._value / other
    
    def __rtruediv__(self, other):
        """右除法运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 的值为 None，无法作为除数")
        if self._value == 0:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 为零，无法作为除数")
        return other / self._value
    
    def __floordiv__(self, other):
        """整除运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 0
        if other == 0:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 除以零")
        return self._value // other
    
    def __rfloordiv__(self, other):
        """右整除运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 的值为 None，无法作为除数")
        if self._value == 0:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 为零，无法作为除数")
        return other // self._value
    
    def __mod__(self, other):
        """取模运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 0
        if other == 0:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 除以零")
        return self._value % other
    
    def __rmod__(self, other):
        """右取模运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 的值为 None，无法作为除数")
        if self._value == 0:
            raise ZeroDivisionError(f"参数 '{self.name_en}' 为零，无法作为除数")
        return other % self._value
    
    def __pow__(self, other):
        """幂运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 0
        return self._value ** other
    
    def __rpow__(self, other):
        """右幂运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 1
        return other ** self._value
    
    def __neg__(self):
        """负号运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 0
        return -self._value
    
    def __pos__(self):
        """正号运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 0
        return +self._value
    
    def __abs__(self):
        """绝对值运算"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持算术运算")
        if self._value is None:
            return 0
        return abs(self._value)
    
    # 比较运算符重载
    def __eq__(self, other):
        """等于比较"""
        if self._is_list:
            return False  # 列表参数不支持比较
        return self._value == other
    
    def __ne__(self, other):
        """不等于比较"""
        return not self.__eq__(other)
    
    def __lt__(self, other):
        """小于比较"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持比较运算")
        if self._value is None:
            return True  # None 小于任何值
        return self._value < other
    
    def __le__(self, other):
        """小于等于比较"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持比较运算")
        if self._value is None:
            return True  # None 小于等于任何值
        return self._value <= other
    
    def __gt__(self, other):
        """大于比较"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持比较运算")
        if self._value is None:
            return False  # None 不大于任何值
        return self._value > other
    
    def __ge__(self, other):
        """大于等于比较"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 不支持比较运算")
        if self._value is None:
            return False  # None 不大于等于任何值
        return self._value >= other
    
    # 数值类型转换
    def __int__(self):
        """转换为整数"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法转换为整数")
        if self._value is None:
            return 0
        return int(self._value)
    
    def __float__(self):
        """转换为浮点数"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法转换为浮点数")
        if self._value is None:
            return 0.0
        return float(self._value)
    
    def __bool__(self):
        """转换为布尔值"""
        if self._is_list:
            return len(self._value) > 0 if isinstance(self._value, list) else False
        if self._value is None:
            return False
        return bool(self._value)
    
    # 新增数值转换方法
    def __complex__(self):
        """转换为复数，供Pyomo使用"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法转换为复数")
        if self._value is None:
            return 0j
        return complex(self._value)
    
    # 让ParameterValue对象可以直接作为数值使用
    def __index__(self):
        """支持作为索引使用"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法作为索引")
        if self._value is None:
            return 0
        return int(self._value)
    
    # 支持与数值类型的比较和运算
    def __round__(self, n=None):
        """支持round()函数"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法四舍五入")
        if self._value is None:
            return 0
        return round(self._value, n)
    
    def __trunc__(self):
        """支持math.trunc()函数"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法截断")
        if self._value is None:
            return 0
        return int(self._value)
    
    def __floor__(self):
        """支持math.floor()函数"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法向下取整")
        if self._value is None:
            return 0
        import math
        return math.floor(self._value)
    
    def __ceil__(self):
        """支持math.ceil()函数"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法向上取整")
        if self._value is None:
            return 0
        import math
        return math.ceil(self._value)
    
    # 支持Pyomo约束中的数值转换
    def __pyomo_value__(self):
        """为Pyomo提供数值转换"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法转换为数值")
        if self._value is None:
            return 0.0
        return float(self._value)
    
    def __pyomo_float__(self):
        """为Pyomo提供浮点数转换"""
        return self.__pyomo_value__()
    
    def __pyomo_int__(self):
        """为Pyomo提供整数转换"""
        if self._is_list:
            raise TypeError(f"列表参数 '{self.name_en}' 无法转换为整数")
        if self._value is None:
            return 0
        return int(self._value)
    
    # 让ParameterValue在需要时自动转换为数值
    def __call__(self):
        """当对象被调用时返回数值"""
        return self.__pyomo_value__()
    
    def __getattr__(self, name):
        """当访问不存在的属性时，尝试返回数值"""
        if name in ['value', 'val', 'numeric']:
            return self.__pyomo_value__()
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __hash__(self):
        """支持哈希操作，让对象可以作为字典的键"""
        if self._is_list:
            return hash(tuple(self._value) if isinstance(self._value, list) else ())
        if self._value is None:
            return hash(0)
        return hash(self._value)

class ParameterCategory:
    """参数分类对象，支持点号访问参数"""
    
    def __init__(self, category_data: Dict[str, Any]):
        self._data = category_data
        self._parameters = {}
        
        # 创建参数对象
        for param_name, param_data in category_data.get('parameters', {}).items():
            self._parameters[param_name] = ParameterValue(param_data)
    
    @property
    def name(self):
        """分类中文名称"""
        return self._data.get('name')
    
    @property
    def name_en(self):
        """分类英文名称"""
        return self._data.get('name_en')
    
    @property
    def description(self):
        """分类描述"""
        return self._data.get('description')
    
    @property
    def id(self):
        """分类ID"""
        return self._data.get('id')
    
    @property
    def created_at(self):
        """创建时间"""
        return self._data.get('created_at')
    
    @property
    def updated_at(self):
        """更新时间"""
        return self._data.get('updated_at')
    
    def __getattr__(self, name):
        """支持点号访问参数"""
        if name in self._parameters:
            return self._parameters[name]
        raise AttributeError(f"分类 '{self.name_en}' 中没有参数 '{name}'")
    
    def __dir__(self):
        """支持dir()函数，显示可用属性"""
        return list(self._parameters.keys()) + ['name', 'name_en', 'description', 'id', 'created_at', 'updated_at']
    
    def __str__(self):
        return f"ParameterCategory(name='{self.name_en}', parameters={list(self._parameters.keys())})"
    
    def __repr__(self):
        return self.__str__()
    
    def list_parameters(self):
        """列出所有参数名称"""
        return list(self._parameters.keys())
    
    def get_parameter(self, name: str) -> ParameterValue:
        """获取指定参数"""
        if name not in self._parameters:
            raise KeyError(f"参数 '{name}' 不存在")
        return self._parameters[name]
    
    def __iter__(self):
        """支持迭代，返回所有参数名称"""
        return iter(self._parameters.keys())
    
    def __getitem__(self, param_name: str) -> ParameterValue:
        """支持中括号访问参数对象"""
        if param_name not in self._parameters:
            raise KeyError(f"参数 '{param_name}' 不存在")
        return self._parameters[param_name]


class Project:
    """项目对象，支持点号访问分类和项目属性"""
    
    def __init__(self, project_data: Dict[str, Any], categories_data: Dict[str, Any]):
        self._data = project_data
        self._categories = {}
        
        # 创建分类对象
        for category_name, category_data in categories_data.items():
            self._categories[category_name] = ParameterCategory(category_data)
    
    @property
    def name(self):
        """项目中文名称"""
        return self._data.get('name')
    
    @property
    def name_en(self):
        """项目英文名称"""
        return self._data.get('name_en')
    
    @property
    def description(self):
        """项目描述"""
        return self._data.get('description')
    
    @property
    def id(self):
        """项目ID"""
        return self._data.get('id')
    
    @property
    def time_horizon(self):
        """时间长度"""
        return self._data.get('time_horizon')
    
    @property
    def start_year(self):
        """起始年份"""
        return self._data.get('start_year')
    
    @property
    def year_step(self):
        """年份步长"""
        return self._data.get('year_step')
    
    @property
    def end_year(self):
        """结束年份"""
        return self._data.get('end_year')
    
    @property
    def created_at(self):
        """创建时间"""
        return self._data.get('created_at')
    
    @property
    def updated_at(self):
        """更新时间"""
        return self._data.get('updated_at')
    
    @property
    def categories(self):
        """参数分类列表"""
        return list(self._categories.keys())
    
    def __getattr__(self, name):
        """支持点号访问分类"""
        if name in self._categories:
            return self._categories[name]
        raise AttributeError(f"项目 '{self.name_en}' 中没有分类 '{name}'")
    
    def __dir__(self):
        """支持dir()函数，显示可用属性"""
        return list(self._categories.keys()) + [
            'name', 'name_en', 'description', 'id', 'time_horizon', 
            'start_year', 'year_step', 'end_year', 'created_at', 'updated_at', 'categories'
        ]
    
    def __str__(self):
        return f"Project(name='{self.name_en}', categories={list(self._categories.keys())})"
    
    def __repr__(self):
        return self.__str__()
    
    def get_category(self, name: str) -> ParameterCategory:
        """获取指定分类"""
        if name not in self._categories:
            raise KeyError(f"分类 '{name}' 不存在")
        return self._categories[name]
    
    def list_categories(self):
        """列出所有分类名称"""
        return list(self._categories.keys())
    
    def __iter__(self):
        """支持迭代，返回所有分类名称"""
        return iter(self._categories.keys())
    
    def __getitem__(self, category_name: str) -> ParameterCategory:
        """支持中括号访问分类对象"""
        if category_name not in self._categories:
            raise KeyError(f"分类 '{category_name}' 不存在")
        return self._categories[category_name]


class ParameterClient:
    """
    参数管理系统客户端
    支持类似pandas DataFrame的点号访问方式
    """
    
    def __init__(self, host: str = "localhost", port: int = 8000, project_name: str = None, *, local_format: Optional[str] = None, local_file: Optional[str] = None):
        """
        初始化参数客户端
        
        Args:
            host: 服务器地址，可以是IP地址或域名
            port: 服务器端口，默认8000
            project_name: 项目英文名称，如果提供则在初始化时自动加载参数
            local_format: 本地导入格式（如 "excel_rich"、"json"）。提供后优先使用本地导入
            local_file: 本地文件路径。与 local_format 同时提供时，初始化优先从本地导入
        """
        self.host = host
        self.port = port
        self.project_name = project_name
        self.base_url = f"http://{host}:{port}/api"
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # 存储项目对象
        self.project = None
        
        # 如果提供了本地导入信息，则优先从本地导入
        if local_format and local_file:
            self.load_project_from_file(local_format, local_file)
        else:
            # 如果提供了项目名称，自动从服务器加载参数
            if project_name:
                self.load_project(project_name)

    # ==================== 本地导入能力 ====================
    def supported_local_import_formats(self) -> List[str]:
        """返回客户端可用的本地导入格式（由已复制的后端注册表提供）。"""
        try:
            # 触发注册（导入子包以执行注册装饰器）
            from .backend.io_formats import registry as _io_registry  # noqa: F401
            from .backend.io_formats.excel_rich import importer as _excel_rich_importer  # noqa: F401
            from .backend.io_formats.json import importer as _json_importer  # noqa: F401
            from .backend.io_formats.registry import supported_import_formats
            return supported_import_formats()
        except Exception as e:
            logger.error(f"获取本地导入格式失败: {e}")
            return []

    def load_project_from_file(self, format_type: str, input_path: str) -> "Project":
        """
        从本地文件导入项目数据并在客户端内存中构建 Project 对象。

        Args:
            format_type: 导入格式，例如 "excel_rich" 或 "json"
            input_path: 本地文件路径

        Returns:
            Project 对象
        """
        # 延迟导入，避免在未使用本地模式时引入依赖
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, Session

        # 触发导入器注册
        from .backend.io_formats import registry as _io_registry  # noqa: F401
        from .backend.io_formats.excel_rich import importer as _excel_rich_importer  # noqa: F401
        from .backend.io_formats.json import importer as _json_importer  # noqa: F401
        from .backend.io_formats.registry import get_importer, supported_import_formats
        from .backend.database import Base, Project as DBProject, ParameterCategory as DBParameterCategory
        from .backend.crud import (
            get_project_by_name_en as crud_get_project_by_name_en,
            get_parameter_categories as crud_get_parameter_categories,
            get_parameters_with_values as crud_get_parameters_with_values,
        )

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"文件不存在: {input_path}")

        if format_type not in supported_import_formats():
            raise ValueError(f"不支持的导入格式: {format_type}")

        importer = get_importer(format_type)
        if not importer:
            raise ValueError(f"导入器创建失败: {format_type}")

        # 创建临时数据库文件承载导入结果
        fd, tmp_db_path = tempfile.mkstemp(suffix=".db", prefix="client_import_")
        os.close(fd)
        try:
            # 连接到临时数据库
            engine = create_engine(f"sqlite:///{tmp_db_path}")
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base.metadata.create_all(bind=engine)
            db: Session = SessionLocal()
            try:
                # 使用 import_into_current_db 方法，这个方法有完整的值解析逻辑
                project = importer.import_into_current_db(db, input_path)
                if not project:
                    raise ProjectNotFoundError(f"导入失败")

                # 项目信息
                project_info: Dict[str, Any] = {
                    "id": project.id,
                    "name": project.name,
                    "name_en": project.name_en,
                    "description": project.description,
                    "time_horizon": project.time_horizon,
                    "start_year": project.start_year,
                    "year_step": project.year_step,
                    "end_year": project.end_year,
                    "created_at": project.created_at.isoformat() if getattr(project, "created_at", None) else None,
                    "updated_at": project.updated_at.isoformat() if getattr(project, "updated_at", None) else None,
                }

                # 分类与参数
                categories = crud_get_parameter_categories(db, project.id)
                categories_data: Dict[str, Any] = {}
                for category in categories:
                    params = crud_get_parameters_with_values(db, category.id)
                    category_params: Dict[str, Any] = {}
                    for param in params:
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
                            "created_at": param["created_at"].isoformat() if param.get("created_at") else None,
                            "updated_at": param["updated_at"].isoformat() if param.get("updated_at") else None,
                        }
                        # 值
                        if param["is_list"]:
                            param_info["value"] = param.get("current_values") or []
                        else:
                            param_info["value"] = param.get("current_value")
                        category_params[param["name_en"]] = param_info

                    categories_data[category.name_en] = {
                        "id": category.id,
                        "name": category.name,
                        "name_en": category.name_en,
                        "description": category.description,
                        "created_at": category.created_at.isoformat() if getattr(category, "created_at", None) else None,
                        "updated_at": category.updated_at.isoformat() if getattr(category, "updated_at", None) else None,
                        "parameters": category_params,
                    }

                # 使用与远端相同的数据结构构造客户端 Project
                self.project = Project(project_info, categories_data)
                self.project_name = project_info["name_en"]
                logger.info(f"本地导入项目成功: {self.project_name}")
                return self.project
            finally:
                db.close()
        finally:
            try:
                os.remove(tmp_db_path)
            except Exception:
                # 允许临时文件清理失败静默
                pass
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点
            **kwargs: 请求参数
            
        Returns:
            响应数据字典
            
        Raises:
            requests.RequestException: 请求失败时抛出
        """
        # 确保endpoint不以/开头，避免urljoin替换掉base_url的路径
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = urljoin(self.base_url + '/', endpoint)
        
        try:
            logger.info(f"发送请求: {method} {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接失败: {method} {url}, 错误: {str(e)}")
            hint = (
                f"无法连接到服务器 {self.host}:{self.port}。\n"
                "请检查：\n"
                "- 服务器是否已启动并正常运行\n"
                "- 地址与端口是否填写正确\n"
                "- 当前网络是否可用/有代理拦截\n"
                "若无需远程服务器，可在本地使用内置后端：run_embedded_server(host, port)"
            )
            raise ConnectionError(hint) from e
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, 'status_code', None)
            reason = getattr(e.response, 'reason', '')
            text = ''
            try:
                text = e.response.text[:200] if e.response is not None else ''
            except Exception:
                text = ''
            if status == 404:
                raise ProjectNotFoundError("未找到资源：请确认项目英文名是否正确，或先在服务器创建该项目。") from e
            if isinstance(status, int) and 500 <= status < 600:
                msg = (
                    f"服务器异常({status} {reason})：{url}\n"
                    "请确认服务器已正常启动并健康运行，可尝试重启服务或稍后重试。"
                )
                logger.error(msg)
                raise ConnectionError(msg) from e
            msg = f"请求失败({status} {reason})：{url}"
            if text:
                msg += f" - {text}"
            msg += "\n如问题持续，请检查网络/服务状态，或联系管理员。"
            logger.error(msg)
            raise ParameterClientError(msg) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {method} {url}, 错误: {str(e)}")
            raise ParameterClientError(f"请求失败: {e}") from e
    
    def load_project(self, project_name: str = None) -> Project:
        """
        加载项目数据
        
        Args:
            project_name: 项目英文名称，如果为None则使用初始化时的项目名称
            
        Returns:
            Project对象
        """
        project_name = project_name or self.project_name
        if not project_name:
            raise ValueError("必须提供项目名称")
        
        try:
            logger.info(f"正在加载项目详细数据: {project_name}")
            
            # 获取项目详细参数数据
            response = self._make_request('GET', f'/projects/{project_name}/parameters/detailed')
            
            # 创建项目对象
            self.project = Project(response['project'], response['categories'])
            self.project_name = project_name
            
            logger.info(f"成功加载项目: {project_name}")
            logger.info(f"项目分类: {self.project.categories}")
            
            return self.project
            
        except Exception as e:
            logger.error(f"加载项目失败: {str(e)}")
            raise
    
    def get_project(self) -> Project:
        """
        获取项目对象
        
        Returns:
            Project对象
            
        Raises:
            ValueError: 项目未加载时抛出
        """
        if not self.project:
            raise ValueError("项目未加载，请先调用 load_project()")
        return self.project
    
    def refresh_project(self) -> Project:
        """
        刷新项目数据（重新从服务器加载）
        
        Returns:
            更新后的Project对象
        """
        if not self.project_name:
            raise ValueError("未设置项目名称，无法刷新项目")
        
        logger.info("正在刷新项目数据...")
        return self.load_project()
    
    def __str__(self) -> str:
        """返回客户端状态字符串"""
        status = f"ParameterClient(host={self.host}, port={self.port}, project={self.project_name})"
        if self.project:
            status += f" - 已加载项目 '{self.project.name_en}'"
        else:
            status += " - 项目未加载"
        return status
    
    def __repr__(self) -> str:
        """返回客户端详细表示"""
        return self.__str__()


def create_client(host: str = "localhost", port: int = 8000, project_name: str = None) -> ParameterClient:
    """
    创建参数客户端的便捷函数
    
    Args:
        host: 服务器地址
        port: 服务器端口
        project_name: 项目英文名称
        
    Returns:
        ParameterClient实例
    """
    return ParameterClient(host, port, project_name)
