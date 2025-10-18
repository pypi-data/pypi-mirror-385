#!/usr/bin/env python3
"""
参数管理系统 Python 客户端基本使用示例
"""
from param_management_client import ParameterClient


def main():
    """基本使用示例"""
    print("=== 参数管理系统 Python 客户端基本使用示例 ===")

    # 方式一：连接服务器读取
    # client = ParameterClient(host="api.anlper.cn", port=80, project_name="oil")
    # project = client.get_project()
    
    # print(f"项目: {project.name} ({project.name_en})")
    # print(f"描述: {project.description}")
    # print(f"时间范围: {project.time_horizon} 年 ({project.start_year}-{project.end_year})")
    # print(f"参数分类: {project.categories}")

    # 方式二：从本地文件导入（无需服务器）
    # 示例：excel_rich 或 json
    local_client = ParameterClient(
        # host="api.anlper.cn", port=80,
        # project_name="oil",
        local_format="excel_rich",
        local_file="/Users/liujiawei/Downloads/oil_parameters_2025-10-15T15-08-45-846Z.xlsx"
    )
    project2 = local_client.get_project()
    # or
    # project2 = local_client.load_project_from_file(format_type="json", input_path="./path/to/your.json")
    print("本地导入成功: ", project2.name_en, project2.categories)
    print(f"项目: {project2.name} ({project2.name_en})")
    print(f"描述: {project2.description}")
    print(f"时间范围: {project2.time_horizon} 年 ({project2.start_year}-{project2.end_year})")
    print(f"参数分类: {project2.categories}")
    print(f"创建时间: {project2.created_at}")
    print(f"更新时间: {project2.updated_at}")
    
    for category_name in project2:
        print(category_name)
        print("参数类别：", project2[category_name])
        for param_name in project2[category_name]:
            print(param_name)
            print("参数值：", project2[category_name][param_name])
    
    print(local_client.supported_local_import_formats())


if __name__ == "__main__":
    main()
