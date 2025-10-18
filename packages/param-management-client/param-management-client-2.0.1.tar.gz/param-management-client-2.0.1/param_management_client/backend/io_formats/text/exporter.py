"""
文本格式导出器实现
生成AI友好的Markdown格式参数文档
"""
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from ...crud import get_project_by_name_en, get_parameter_categories, get_parameters_with_values
from ...io_formats.registry import register_exporter
from ...io_formats.validation import generate_project_checksum


@register_exporter("text")
class TextExporter:
    """文本格式导出器，生成AI友好的参数文档"""
    
    def __init__(self):
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)

    def export(self, project_name_en: str, db_session) -> str:
        """导出项目参数为Markdown格式"""
        project = get_project_by_name_en(db_session, project_name_en)
        if not project:
            raise ValueError(f"项目 '{project_name_en}' 不存在")
        
        categories = get_parameter_categories(db_session, project.id)
        if not categories:
            raise ValueError(f"项目 '{project_name_en}' 没有参数分类")

        # 生成项目校验哈希
        project_checksum = generate_project_checksum(project.name_en, db_session)

        # 构建Markdown内容
        md_content = self._build_markdown_content(project, categories, db_session, project_checksum)

        # 保存Markdown文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{project.name_en}_parameters_{timestamp}.md"
        filepath = self.export_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(filepath)

    def _build_markdown_content(self, project, categories, db_session, project_checksum) -> str:
        """构建Markdown内容"""
        lines = []
        
        # 标题
        lines.append(f"# {project.name} 参数文档")
        lines.append("")
        
        # 使用说明
        lines.append("## 使用说明")
        lines.append("")
        lines.append("### Python客户端使用方式")
        lines.append("")
        lines.append("```python")
        lines.append("from param_management_client import ParameterClient")
        lines.append("")
        lines.append("# 创建客户端")
        lines.append("client = ParameterClient(")
        lines.append("    host='api.anlper.cn',")
        lines.append("    port=80,")
        lines.append(f"    project_name='{project.name_en}'")
        lines.append(")")
        lines.append("")
        lines.append("# 获取项目对象")
        lines.append("project = client.get_project()")
        lines.append("")
        lines.append("# 访问参数示例")
        lines.append("# project.<分类名>.<参数名>")
        lines.append("```")
        lines.append("")
        
        # 基本数据获取说明
        lines.append("### 获取项目基本信息")
        lines.append("")
        lines.append("| 属性名称 | 访问方式 | 说明 |")
        lines.append("|---------|-----------|------|")
        lines.append("| 项目名称 | `project.name` | 项目中文名称 |")
        lines.append("| 项目英文名 | `project.name_en` | 项目英文标识 |")
        lines.append("| 项目描述 | `project.description` | 项目详细描述 |")
        lines.append("| 时间范围 | `project.time_horizon` | 项目时间长度（年） |")
        lines.append("| 起始年份 | `project.start_year` | 项目开始年份 |")
        lines.append("| 年份步长 | `project.year_step` | 年份间隔 |")
        lines.append("| 结束年份 | `project.end_year` | 项目结束年份 |")
        lines.append("| 参数分类 | `project.categories` | 所有分类名称列表 |")
        lines.append("")
        
        # 灵活操作说明
        lines.append("### 灵活操作")
        lines.append("")
        lines.append("| 操作 | 访问方式 | 说明 |")
        lines.append("|------|----------|------|")
        lines.append("| 获取所有分类 | `project.list_categories()` | 返回所有分类名称列表 |")
        lines.append("| 获取指定分类 | `project['分类名']` 或 `project.分类名` | 获取指定分类对象 |")
        lines.append("| 获取分类下所有参数 | `project.分类名.list_parameters()` | 返回该分类下所有参数名称 |")
        lines.append("| 获取指定参数 | `project['分类名']['参数名']` 或 `project.分类名.参数名` | 获取指定参数对象 |")
        lines.append("| 遍历所有分类 | `for category_name in project:` | 遍历所有分类名称 |")
        lines.append("| 遍历分类下所有参数 | `for param_name in project[category_name]:` | 遍历该分类下所有参数名称 |")
        lines.append("")
        
        # 分类基本信息获取说明
        lines.append("### 获取分类基本信息")
        lines.append("")
        lines.append("| 属性名称 | 访问方式 | 说明 |")
        lines.append("|---------|-----------|------|")
        lines.append("| 分类名称 | `category.name` | 分类中文名称 |")
        lines.append("| 分类英文名 | `category.name_en` | 分类英文标识 |")
        lines.append("| 分类描述 | `category.description` | 分类详细描述 |")
        lines.append("")
        
        # 参数基本信息获取说明
        lines.append("### 获取参数基本信息")
        lines.append("")
        lines.append("| 属性名称 | 访问方式 | 说明 |")
        lines.append("|---------|-----------|------|")
        lines.append("| 参数名称 | `param.name` | 参数中文名称 |")
        lines.append("| 参数英文名 | `param.name_en` | 参数英文标识 |")
        lines.append("| 参数值 | `param.value` | 参数当前值 |")
        lines.append("| 参数单位 | `param.unit` | 参数单位 |")
        lines.append("| 参数描述 | `param.description` | 参数详细描述 |")
        lines.append("| 参数类型 | `param.param_type` | 参数数据类型 |")
        lines.append("| 是否列表 | `param.is_list` | 是否为列表类型参数 |")
        lines.append("| 是否关联年份 | `param.is_year_related` | 是否与年份关联 |")
        lines.append("| 列表长度 | `param.list_length` | 列表参数的长度 |")
        lines.append("")
        
        # 参数分类和参数
        lines.append("## 参数分类")
        lines.append("")
        
        for category in categories:
            parameters = get_parameters_with_values(db_session, category.id)
            
            # 分类标题
            lines.append(f"### {category.name} ({category.name_en})")
            lines.append("")
            if category.description:
                lines.append(f"**描述**: {category.description}")
                lines.append("")
            
            # 参数列表
            if parameters:
                lines.append("| 参数名称 | 参数英文名 | 类型 | 是否列表 | 是否关联年份 | 列表长度 | 代码访问方式 |")
                lines.append("|---------|-----------|------|----------|-------------|----------|-------------|")
                
                for param in parameters:
                    # 构建代码访问方式
                    code_access = f"project.{category.name_en}.{param['name_en']}"
                    
                    # 处理参数值显示
                    param_type = param['param_type']
                    is_list = "是" if param['is_list'] else "否"
                    is_year_related = "是" if param['is_year_related'] else "否"
                    list_length = param.get('list_length') or len(param.get('current_values', [])) if param['is_list'] else "-"
                    
                    lines.append(f"| {param['name']} | {param['name_en']} | {param_type} | {is_list} | {is_year_related} | {list_length} | `{code_access}` |")
                
                lines.append("")
            else:
                lines.append("*该分类暂无参数*")
                lines.append("")
        
        
        
        lines.append("---")
        lines.append(f"*文档生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(lines)

    def get_export_formats(self) -> List[Dict[str, str]]:
        """返回支持的导出格式信息"""
        return [
            {
                "format": "text", 
                "name": "Markdown文档", 
                "extension": ".md", 
                "description": "AI友好的Markdown格式参数文档，包含使用说明和代码示例"
            }
        ]

