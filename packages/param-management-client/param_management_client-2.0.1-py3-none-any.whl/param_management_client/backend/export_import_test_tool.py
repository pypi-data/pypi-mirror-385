#!/usr/bin/env python3
"""
导出导入一致性测试工具
自动测试指定格式的导出导入流程是否一致
"""

import sys
import os
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.database import SessionLocal, Project, ParameterCategory, Parameter, ParameterValue, create_engine, sessionmaker
from backend.io_formats.registry import get_exporter, get_importer, supported_export_formats, supported_import_formats
from backend.io_formats.validation import validate_import_consistency


class ExportImportTester:
    """导出导入一致性测试器"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.temp_dir = None
    
    def test_format_consistency(self, format_type: str, project_name_en: str, 
                               cleanup: bool = True) -> dict:
        """
        测试指定格式的导出导入一致性
        
        Args:
            format_type: 格式类型 (json, excel_rich, text)
            project_name_en: 项目英文名称
            cleanup: 是否清理临时文件
            
        Returns:
            dict: 测试结果
        """
        print(f"🧪 测试格式 '{format_type}' 的导出导入一致性")
        print(f"📋 测试项目: {project_name_en}")
        print("=" * 80)
        
        try:
            # 检查项目是否存在
            project = self.db.query(Project).filter(Project.name_en == project_name_en).first()
            if not project:
                raise ValueError(f"项目 '{project_name_en}' 不存在")
            
            # 检查格式是否支持
            if format_type not in supported_export_formats():
                raise ValueError(f"不支持的导出格式: {format_type}")
            
            if format_type not in supported_import_formats():
                raise ValueError(f"不支持的导入格式: {format_type}")
            
            # 创建临时目录
            self.temp_dir = tempfile.mkdtemp(prefix=f"export_import_test_{format_type}_")
            temp_dir_path = Path(self.temp_dir)
            
            
            # 步骤1: 导出项目
            print("\n📤 步骤1: 导出项目...")
            exporter = get_exporter(format_type)
            if not exporter:
                raise ValueError(f"无法获取 {format_type} 导出器")
            
            # 修改导出器的工作目录到临时目录
            exporter.export_dir = temp_dir_path
            
            export_file = exporter.export(project_name_en, self.db)
            print(f"✅ 导出完成")
            
            # 步骤2: 导入到新数据库
            print("\n📥 步骤2: 导入到新数据库...")
            importer = get_importer(format_type)
            if not importer:
                raise ValueError(f"无法获取 {format_type} 导入器")
            
            # 创建临时数据库
            temp_db_path = temp_dir_path / "test_import.db"
            
            # 确保临时数据库文件不存在
            if temp_db_path.exists():
                temp_db_path.unlink()
            
            import_result = importer.import_project(export_file, str(temp_db_path))
            print(f"✅ 导入完成: {import_result.project_name_en}")
            print(f"   📊 统计: {import_result.categories_count} 分类, "
                  f"{import_result.parameters_count} 参数, "
                  f"{import_result.values_count} 值")
            
            # 步骤3: 比较一致性
            print("\n🔍 步骤3: 比较一致性...")
            
            # 创建临时数据库的会话
            temp_engine = create_engine(f"sqlite:///{temp_db_path}")
            TempSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)
            temp_db = TempSessionLocal()
            
            try:
                # 跨数据库比较项目一致性
                from backend.io_formats.validation import ProjectConsistencyValidator
                
                # 生成原始项目的哈希
                original_project = self.db.query(Project).filter(Project.name_en == project_name_en).first()
                if not original_project:
                    raise ValueError(f"原始项目 '{project_name_en}' 不存在")
                original_hash = ProjectConsistencyValidator.generate_project_hash(original_project, self.db)
                
                # 生成导入项目的哈希
                imported_project = temp_db.query(Project).filter(Project.name_en == import_result.project_name_en).first()
                if not imported_project:
                    raise ValueError(f"导入项目 '{import_result.project_name_en}' 不存在")
                imported_hash = ProjectConsistencyValidator.generate_project_hash(imported_project, temp_db)
                
                # 比较哈希
                is_consistent = original_hash == imported_hash
                
                comparison_result = {
                    "is_consistent": is_consistent,
                    "original_hash": original_hash,
                    "imported_hash": imported_hash,
                    "original_project_name": original_project.name,
                    "imported_project_name": imported_project.name
                }
                
                print(f"📊 比较结果:")
                print(f"  原始项目: {comparison_result['original_project_name']}")
                print(f"  导入项目: {comparison_result['imported_project_name']}")
                print(f"  是否一致: {'✅ 是' if comparison_result['is_consistent'] else '❌ 否'}")
                print(f"  原始哈希: {comparison_result['original_hash'][:16]}...")
                print(f"  导入哈希: {comparison_result['imported_hash'][:16]}...")
                
                # 返回测试结果
                result = {
                    "success": True,
                    "format_type": format_type,
                    "project_name_en": project_name_en,
                    "is_consistent": comparison_result['is_consistent'],
                    "export_file": export_file,
                    "import_result": import_result,
                    "comparison_result": comparison_result,
                    "temp_dir": str(temp_dir_path)
                }
                
                if comparison_result['is_consistent']:
                    print("\n🎉 测试通过！导出导入完全一致！")
                else:
                    print("\n⚠️  测试失败！导出导入存在差异！")
                    # 显示详细差异信息
                    self._show_detailed_differences(original_project, imported_project, self.db, temp_db)
                
                return result
                
            finally:
                temp_db.close()
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            return {
                "success": False,
                "format_type": format_type,
                "project_name_en": project_name_en,
                "error": str(e),
                "temp_dir": str(self.temp_dir) if self.temp_dir else None
            }
        
        finally:
            # 清理临时文件
            if cleanup and self.temp_dir and Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
    
    def _show_detailed_differences(self, original_project, imported_project, original_db, imported_db):
        """显示详细的差异信息"""
        print("\n" + "=" * 80)
        print("📋 详细差异分析:")
        
        # 比较项目基本信息
        self._compare_project_info(original_project, imported_project)
        
        # 比较分类和参数
        original_categories = original_db.query(ParameterCategory).filter(
            ParameterCategory.project_id == original_project.id
        ).order_by(ParameterCategory.name_en).all()
        
        imported_categories = imported_db.query(ParameterCategory).filter(
            ParameterCategory.project_id == imported_project.id
        ).order_by(ParameterCategory.name_en).all()
        
        self._compare_categories_detailed(original_categories, imported_categories, original_db, imported_db)
        
        # 统计信息
        self._print_statistics_detailed(original_categories, imported_categories, original_db, imported_db)
    
    def _compare_project_info(self, original_project, imported_project):
        """比较项目基本信息"""
        print("\n📋 项目基本信息:")
        differences = []
        
        fields = ['name', 'name_en', 'description', 'time_horizon', 'start_year', 'year_step', 'end_year']
        for field in fields:
            original_val = getattr(original_project, field)
            imported_val = getattr(imported_project, field)
            if original_val != imported_val:
                differences.append(f"  ❌ {field}: '{original_val}' vs '{imported_val}'")
            else:
                print(f"  ✅ {field}: 一致")
        
        for diff in differences:
            print(diff)
        
        if not differences:
            print("  ✅ 项目基本信息完全一致")
    
    def _compare_categories_detailed(self, original_categories, imported_categories, original_db, imported_db):
        """比较分类信息"""
        print("\n📂 分类和参数比较:")
        
        original_cats = {cat.name_en: cat for cat in original_categories}
        imported_cats = {cat.name_en: cat for cat in imported_categories}
        all_categories = set(original_cats.keys()) | set(imported_cats.keys())
        
        for cat_name in sorted(all_categories):
            print(f"\n  📁 分类: {cat_name}")
            
            if cat_name not in original_cats:
                print(f"    ❌ 只在导入项目中存在")
                continue
            elif cat_name not in imported_cats:
                print(f"    ❌ 只在原始项目中存在")
                continue
            
            original_cat = original_cats[cat_name]
            imported_cat = imported_cats[cat_name]
            
            # 比较分类基本信息
            cat_diffs = []
            for field in ['name', 'description']:
                original_val = getattr(original_cat, field)
                imported_val = getattr(imported_cat, field)
                if original_val != imported_val:
                    cat_diffs.append(f"    ❌ {field}: '{original_val}' vs '{imported_val}'")
            
            if cat_diffs:
                for diff in cat_diffs:
                    print(diff)
            else:
                print(f"    ✅ 分类信息一致")
            
            # 比较参数
            self._compare_parameters_detailed(original_cat, imported_cat, original_db, imported_db)
    
    def _compare_parameters_detailed(self, original_cat, imported_cat, original_db, imported_db):
        """比较参数"""
        original_params = original_db.query(Parameter).filter(
            Parameter.category_id == original_cat.id
        ).order_by(Parameter.name_en).all()
        
        imported_params = imported_db.query(Parameter).filter(
            Parameter.category_id == imported_cat.id
        ).order_by(Parameter.name_en).all()
        
        original_params_dict = {param.name_en: param for param in original_params}
        imported_params_dict = {param.name_en: param for param in imported_params}
        all_params = set(original_params_dict.keys()) | set(imported_params_dict.keys())
        
        for param_name in sorted(all_params):
            if param_name not in original_params_dict:
                print(f"    ❌ 参数 '{param_name}': 只在导入项目中存在")
                continue
            elif param_name not in imported_params_dict:
                print(f"    ❌ 参数 '{param_name}': 只在原始项目中存在")
                continue
            
            original_param = original_params_dict[param_name]
            imported_param = imported_params_dict[param_name]
            
            # 比较参数基本信息
            param_diffs = []
            fields = ['name', 'param_type', 'unit', 'description', 'is_list', 'is_year_related', 'list_length']
            for field in fields:
                original_val = getattr(original_param, field)
                imported_val = getattr(imported_param, field)
                if original_val != imported_val:
                    param_diffs.append(f"      ❌ {field}: '{original_val}' vs '{imported_val}'")
            
            # 比较参数值
            original_values = original_db.query(ParameterValue).filter(
                ParameterValue.parameter_id == original_param.id
            ).order_by(ParameterValue.list_index.asc().nullsfirst()).all()
            
            imported_values = imported_db.query(ParameterValue).filter(
                ParameterValue.parameter_id == imported_param.id
            ).order_by(ParameterValue.list_index.asc().nullsfirst()).all()
            
            original_values_dict = {v.list_index: v.value for v in original_values}
            imported_values_dict = {v.list_index: v.value for v in imported_values}
            all_indices = set(original_values_dict.keys()) | set(imported_values_dict.keys())
            
            value_diffs = []
            for idx in sorted(all_indices):
                if idx not in original_values_dict:
                    value_diffs.append(f"      ❌ 值[{idx}]: 只在导入项目中存在 '{imported_values_dict[idx]}'")
                elif idx not in imported_values_dict:
                    value_diffs.append(f"      ❌ 值[{idx}]: 只在原始项目中存在 '{original_values_dict[idx]}'")
                elif original_values_dict[idx] != imported_values_dict[idx]:
                    value_diffs.append(f"      ❌ 值[{idx}]: '{original_values_dict[idx]}' vs '{imported_values_dict[idx]}'")
            
            if param_diffs or value_diffs:
                print(f"    ❌ 参数 '{param_name}': 存在差异")
                for diff in param_diffs + value_diffs:
                    print(diff)
            else:
                print(f"    ✅ 参数 '{param_name}': 完全一致")
    
    def _print_statistics_detailed(self, original_categories, imported_categories, original_db, imported_db):
        """打印统计信息"""
        print("\n" + "=" * 80)
        print("📊 统计信息:")
        
        original_params_count = sum(
            original_db.query(Parameter).filter(Parameter.category_id == cat.id).count()
            for cat in original_categories
        )
        imported_params_count = sum(
            imported_db.query(Parameter).filter(Parameter.category_id == cat.id).count()
            for cat in imported_categories
        )
        
        original_values_count = sum(
            original_db.query(ParameterValue).join(Parameter).filter(Parameter.category_id == cat.id).count()
            for cat in original_categories
        )
        imported_values_count = sum(
            imported_db.query(ParameterValue).join(Parameter).filter(Parameter.category_id == cat.id).count()
            for cat in imported_categories
        )
        
        print(f"  原始项目: {len(original_categories)} 个分类, {original_params_count} 个参数, {original_values_count} 个值")
        print(f"  导入项目: {len(imported_categories)} 个分类, {imported_params_count} 个参数, {imported_values_count} 个值")
        
        if len(original_categories) != len(imported_categories):
            print(f"  ⚠️  分类数量不同: {len(original_categories)} vs {len(imported_categories)}")
        if original_params_count != imported_params_count:
            print(f"  ⚠️  参数数量不同: {original_params_count} vs {imported_params_count}")
        if original_values_count != imported_values_count:
            print(f"  ⚠️  值数量不同: {original_values_count} vs {imported_values_count}")
    
    def test_all_formats(self, project_name_en: str) -> dict:
        """
        测试所有支持格式的一致性
        
        Args:
            project_name_en: 项目英文名称
            
        Returns:
            dict: 所有格式的测试结果
        """
        print(f"🧪 测试所有格式的导出导入一致性")
        print(f"📋 测试项目: {project_name_en}")
        print("=" * 80)
        
        # 获取所有支持的格式
        export_formats = supported_export_formats()
        import_formats = supported_import_formats()
        common_formats = set(export_formats) & set(import_formats)
        
        if not common_formats:
            print("❌ 没有找到同时支持导出和导入的格式")
            return {"success": False, "error": "没有支持的格式"}
        
        print(f"📋 支持的格式: {', '.join(sorted(common_formats))}")
        
        results = {}
        all_passed = True
        
        for format_type in sorted(common_formats):
            print(f"\n{'='*20} 测试格式: {format_type} {'='*20}")
            result = self.test_format_consistency(format_type, project_name_en, cleanup=False)
            results[format_type] = result
            
            if not result["success"] or not result.get("is_consistent", False):
                all_passed = False
        
        # 最终清理
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        
        print(f"\n{'='*80}")
        print(f"📊 测试总结:")
        for format_type, result in results.items():
            status = "✅ 通过" if result.get("success") and result.get("is_consistent") else "❌ 失败"
            print(f"  {format_type}: {status}")
        
        print(f"\n🎯 总体结果: {'✅ 全部通过' if all_passed else '❌ 存在失败'}")
        
        return {
            "success": all_passed,
            "project_name_en": project_name_en,
            "results": results
        }


def list_available_projects(db_session):
    """列出所有可用的项目"""
    projects = db_session.query(Project).all()
    if not projects:
        print("❌ 数据库中没有找到任何项目")
        return []
    
    print("📋 可用的项目:")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project.name_en} ({project.name})")
    
    return projects


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='导出导入一致性测试工具')
    parser.add_argument('project', nargs='?', help='项目名称（英文）')
    parser.add_argument('--format', '-f', type=str, 
                       help='指定测试格式 (json, excel_rich, text)，不指定则测试所有格式')
    parser.add_argument('--database', '-db', type=str, 
                       help='数据库文件路径（默认：./param_management.db）')
    parser.add_argument('--list-projects', '-l', action='store_true',
                       help='列出所有可用项目')
    parser.add_argument('--keep-temp', action='store_true',
                       help='保留临时文件（用于调试）')
    
    args = parser.parse_args()
    
    # 检查参数
    if args.list_projects:
        # 列出项目模式，不需要项目参数
        pass
    elif not args.project:
        parser.error("需要指定项目名称，或使用 --list-projects 列出可用项目")
    
    # 设置数据库路径并创建会话
    if args.database:
        # 使用自定义数据库路径
        database_url = f'sqlite:///{args.database}'
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        CustomSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = CustomSessionLocal()
    else:
        # 使用默认数据库
        db = SessionLocal()
    
    try:
        # 列出项目
        if args.list_projects:
            list_available_projects(db)
            return 0
        
        # 创建测试器
        tester = ExportImportTester(db)
        
        # 执行测试
        if args.format:
            # 测试指定格式
            result = tester.test_format_consistency(
                args.format, 
                args.project, 
                cleanup=not args.keep_temp
            )
            return 0 if result["success"] and result.get("is_consistent", False) else 1
        else:
            # 测试所有格式
            result = tester.test_all_formats(args.project)
            return 0 if result["success"] else 1
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
