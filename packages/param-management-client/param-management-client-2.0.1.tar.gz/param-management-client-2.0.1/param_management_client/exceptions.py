"""
参数管理系统客户端异常定义
"""


class ParameterClientError(Exception):
    """参数客户端基础异常"""
    pass


class ParameterNotFoundError(ParameterClientError):
    """参数未找到异常"""
    pass


class CategoryNotFoundError(ParameterClientError):
    """分类未找到异常"""
    pass


class ProjectNotFoundError(ParameterClientError):
    """项目未找到异常"""
    pass


class ConnectionError(ParameterClientError):
    """连接错误异常"""
    pass
