#!/usr/bin/env python3
"""
参数管理系统 Python 客户端测试
"""
import pytest
from unittest.mock import Mock, patch
from param_management_client import ParameterClient, create_client
from param_management_client.exceptions import ParameterClientError, ProjectNotFoundError


class TestParameterClient:
    """ParameterClient测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = ParameterClient(host="localhost", port=8000)
        assert client.host == "localhost"
        assert client.port == 8000
        assert client.project_name is None
        assert client.project is None
    
    def test_client_initialization_with_project(self):
        """测试带项目名称的客户端初始化"""
        with patch.object(ParameterClient, 'load_project') as mock_load:
            client = ParameterClient(host="localhost", port=8000, project_name="test_project")
            assert client.project_name == "test_project"
            mock_load.assert_called_once_with("test_project")
    
    def test_create_client_function(self):
        """测试create_client便捷函数"""
        client = create_client(host="localhost", port=8000, project_name="test_project")
        assert isinstance(client, ParameterClient)
        assert client.host == "localhost"
        assert client.port == 8000
        assert client.project_name == "test_project"


class TestParameterValue:
    """ParameterValue测试类"""
    
    def test_single_value_conversion(self):
        """测试单个值类型转换"""
        from param_management_client.client import ParameterValue
        
        # 测试float类型
        param_data = {
            'value': '0.35',
            'param_type': 'float',
            'is_list': False,
            'name_en': 'test_param'
        }
        param = ParameterValue(param_data)
        assert param.value == 0.35
        assert isinstance(param.value, float)
        
        # 测试integer类型
        param_data['value'] = '100'
        param_data['param_type'] = 'integer'
        param = ParameterValue(param_data)
        assert param.value == 100
        assert isinstance(param.value, int)
        
        # 测试boolean类型
        param_data['value'] = 'true'
        param_data['param_type'] = 'boolean'
        param = ParameterValue(param_data)
        assert param.value is True
        assert isinstance(param.value, bool)
    
    def test_list_value_conversion(self):
        """测试列表值类型转换"""
        from param_management_client.client import ParameterValue
        
        param_data = {
            'value': ['0.1', '0.2', '0.3'],
            'param_type': 'float',
            'is_list': True,
            'name_en': 'test_list_param'
        }
        param = ParameterValue(param_data)
        assert param.value == [0.1, 0.2, 0.3]
        assert all(isinstance(x, float) for x in param.value)
    
    def test_parameter_properties(self):
        """测试参数属性"""
        from param_management_client.client import ParameterValue
        
        param_data = {
            'value': '0.35',
            'param_type': 'float',
            'is_list': False,
            'name_en': 'capital_ratio',
            'name': '资本比例',
            'unit': '比例',
            'description': '资本金比例'
        }
        param = ParameterValue(param_data)
        
        assert param.name == '资本比例'
        assert param.name_en == 'capital_ratio'
        assert param.unit == '比例'
        assert param.description == '资本金比例'
        assert param.param_type == 'float'
        assert param.is_list is False
    
    def test_list_operations(self):
        """测试列表操作"""
        from param_management_client.client import ParameterValue
        
        param_data = {
            'value': [0.1, 0.2, 0.3],
            'param_type': 'float',
            'is_list': True,
            'name_en': 'test_list'
        }
        param = ParameterValue(param_data)
        
        # 测试索引访问
        assert param[0] == 0.1
        assert param[1] == 0.2
        assert param[2] == 0.3
        
        # 测试长度
        assert len(param) == 3
        
        # 测试迭代
        values = list(param)
        assert values == [0.1, 0.2, 0.3]


class TestParameterCategory:
    """ParameterCategory测试类"""
    
    def test_category_creation(self):
        """测试分类创建"""
        from param_management_client.client import ParameterCategory
        
        category_data = {
            'name': '风能参数',
            'name_en': 'wind_params',
            'description': '风电项目参数',
            'parameters': {
                'capital_ratio': {
                    'value': '0.35',
                    'param_type': 'float',
                    'is_list': False,
                    'name_en': 'capital_ratio'
                }
            }
        }
        category = ParameterCategory(category_data)
        
        assert category.name == '风能参数'
        assert category.name_en == 'wind_params'
        assert category.description == '风电项目参数'
        assert 'capital_ratio' in category.list_parameters()
    
    def test_parameter_access(self):
        """测试参数访问"""
        from param_management_client.client import ParameterCategory
        
        category_data = {
            'name': '风能参数',
            'name_en': 'wind_params',
            'parameters': {
                'capital_ratio': {
                    'value': '0.35',
                    'param_type': 'float',
                    'is_list': False,
                    'name_en': 'capital_ratio'
                }
            }
        }
        category = ParameterCategory(category_data)
        
        # 测试点号访问
        capital_ratio = category.capital_ratio
        assert capital_ratio.value == 0.35
        
        # 测试get_parameter方法
        capital_ratio2 = category.get_parameter('capital_ratio')
        assert capital_ratio2.value == 0.35


class TestProject:
    """Project测试类"""
    
    def test_project_creation(self):
        """测试项目创建"""
        from param_management_client.client import Project
        
        project_data = {
            'name': '测试项目',
            'name_en': 'test_project',
            'time_horizon': 10
        }
        
        categories_data = {
            'wind_params': {
                'name': '风能参数',
                'name_en': 'wind_params',
                'parameters': {}
            }
        }
        
        project = Project(project_data, categories_data)
        
        assert project.name == '测试项目'
        assert project.name_en == 'test_project'
        assert project.time_horizon == 10
        assert 'wind_params' in project.categories
    
    def test_category_access(self):
        """测试分类访问"""
        from param_management_client.client import Project
        
        project_data = {'name': '测试项目', 'name_en': 'test_project'}
        categories_data = {
            'wind_params': {
                'name': '风能参数',
                'name_en': 'wind_params',
                'parameters': {}
            }
        }
        
        project = Project(project_data, categories_data)
        
        # 测试点号访问
        wind_params = project.wind_params
        assert wind_params.name == '风能参数'
        
        # 测试get_category方法
        wind_params2 = project.get_category('wind_params')
        assert wind_params2.name == '风能参数'


if __name__ == "__main__":
    pytest.main([__file__])
