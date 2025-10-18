from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json

from ...crud import get_project_by_name_en, get_parameter_categories, get_parameters_with_values
from ...io_formats.registry import register_exporter
from ...io_formats.validation import generate_project_checksum


@register_exporter("json")
class JsonExporter:
    def __init__(self):
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)

    def export(self, project_name_en: str, db_session) -> str:
        """导出项目参数为JSON格式"""
        project = get_project_by_name_en(db_session, project_name_en)
        if not project:
            raise ValueError(f"项目 '{project_name_en}' 不存在")
        
        categories = get_parameter_categories(db_session, project.id)
        if not categories:
            raise ValueError(f"项目 '{project_name_en}' 没有参数分类")

        # 生成项目校验哈希
        project_checksum = generate_project_checksum(project.name_en, db_session)

        # 构建导出数据结构
        export_data = {
            "project": {
                "name": project.name,
                "name_en": project.name_en,
                "description": project.description,
                "time_horizon": project.time_horizon,
                "start_year": project.start_year,
                "year_step": project.year_step,
                "end_year": project.end_year,
                "export_time": datetime.now().isoformat(),
                "checksum": project_checksum
            },
            "categories": []
        }

        # 处理每个分类
        for category in categories:
            parameters = get_parameters_with_values(db_session, category.id)
            category_data = {
                "name": category.name,
                "name_en": category.name_en,
                "description": category.description,
                "parameters": []
            }

            # 处理每个参数
            for param in parameters:
                param_data = {
                    "name": param['name'],
                    "name_en": param['name_en'],
                    "param_type": param['param_type'],
                    "unit": param.get('unit'),
                    "description": param.get('description'),
                    "is_list": param['is_list'],
                    "is_year_related": param['is_year_related'],
                    "list_length": param.get('list_length'),
                    "values": []
                }

                # 处理参数值
                if param['is_list']:
                    values = param.get('current_values', [])
                    for idx, value in enumerate(values):
                        param_data["values"].append({
                            "index": idx,
                            "value": str(value) if value is not None else None
                        })
                else:
                    value = param.get('current_value')
                    if value is not None:
                        param_data["values"].append({
                            "index": None,
                            "value": str(value)
                        })

                category_data["parameters"].append(param_data)

            export_data["categories"].append(category_data)

        # 保存JSON文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{project.name_en}_parameters_{timestamp}.json"
        filepath = self.export_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)

    def get_export_formats(self) -> List[Dict[str, str]]:
        return [
            {
                "format": "json", 
                "name": "JSON文件", 
                "extension": ".json", 
                "description": "结构化的JSON格式文件，便于程序处理"
            }
        ]
