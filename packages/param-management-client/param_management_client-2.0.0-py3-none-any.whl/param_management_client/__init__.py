"""
参数管理系统 Python 客户端
支持类似pandas DataFrame的点号访问方式
"""

from .client import ParameterClient, create_client
from .exceptions import ParameterClientError, ParameterNotFoundError, CategoryNotFoundError
from .backend import run_embedded_server, backend_app

__version__ = "2.0.0"
__author__ = "Liu Jiawei"
__email__ = "liujiawei@anlper.cn"

__all__ = [
    "ParameterClient",
    "create_client", 
    "ParameterClientError",
    "ParameterNotFoundError",
    "CategoryNotFoundError",
    "run_embedded_server",
    "backend_app",
]
