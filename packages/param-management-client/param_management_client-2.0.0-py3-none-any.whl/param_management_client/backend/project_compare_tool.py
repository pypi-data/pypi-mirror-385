#!/usr/bin/env python3
"""
项目比较工具
用于比较两个项目的详细差异
"""

import sys
import argparse
from database import SessionLocal
from database import Project, ParameterCategory, Parameter, ParameterValue
from io_formats.validation import ProjectConsistencyValidator, validate_import_consistency

class ProjectComparator:
    """项目比较器"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def compare_projects(self, project1_name, project2_name, show_details=True):
        """比较两个项目"""
        print(f"🔍 比较项目: {project1_name} vs {project2_name}")
        print("=" * 80)
        
        try:
            # 首先进行快速一致性检查
            result = validate_import_consistency(project1_name, project2_name, self.db)
            
            print(f"📊 快速检查结果:")
            print(f"  项目1: {result['original_project_name']}")
            print(f"  项目2: {result['imported_project_name']}")
            print(f"  是否一致: {'✅ 是' if result['is_consistent'] else '❌ 否'}")
            print(f"  项目1哈希: {result['original_hash'][:16]}...")
            print(f"  项目2哈希: {result['imported_hash'][:16]}...")
            
            if result['is_consistent']:
                print("\n🎉 两个项目完全一致！")
                return True
            
            if not show_details:
                print("\n⚠️  项目不一致，使用 --details 参数查看详细差异")
                return False
            
            print("\n" + "=" * 80)
            print("📋 详细差异分析:")
            
            # 获取详细数据进行比较
            data1 = self._get_project_data(project1_name)
            data2 = self._get_project_data(project2_name)
            
            # 比较项目基本信息
            self._compare_project_info(data1['project'], data2['project'])
            
            # 比较分类和参数
            self._compare_categories(data1['categories'], data2['categories'])
            
            # 统计信息
            self._print_statistics(data1, data2)
            
            return False
            
        except ValueError as e:
            print(f"❌ 错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 比较过程中出现错误: {e}")
            return False
    
    def _get_project_data(self, project_name_en):
        """获取项目详细数据"""
        project = self.db.query(Project).filter(Project.name_en == project_name_en).first()
        if not project:
            raise ValueError(f"项目 '{project_name_en}' 不存在")
        
        return ProjectConsistencyValidator._build_project_data(project, self.db)
    
    def _compare_project_info(self, info1, info2):
        """比较项目基本信息"""
        print("\n📋 项目基本信息:")
        differences = []
        
        for key in info1:
            if info1[key] != info2[key]:
                differences.append(f"  ❌ {key}: '{info1[key]}' vs '{info2[key]}'")
            else:
                print(f"  ✅ {key}: 一致")
        
        for diff in differences:
            print(diff)
        
        if not differences:
            print("  ✅ 项目基本信息完全一致")
    
    def _compare_categories(self, categories1, categories2):
        """比较分类信息"""
        print("\n📂 分类和参数比较:")
        
        cats1 = {cat['name_en']: cat for cat in categories1}
        cats2 = {cat['name_en']: cat for cat in categories2}
        all_categories = set(cats1.keys()) | set(cats2.keys())
        
        for cat_name in sorted(all_categories):
            print(f"\n  📁 分类: {cat_name}")
            
            if cat_name not in cats1:
                print(f"    ❌ 只在项目2中存在")
                continue
            elif cat_name not in cats2:
                print(f"    ❌ 只在项目1中存在")
                continue
            
            cat1 = cats1[cat_name]
            cat2 = cats2[cat_name]
            
            # 比较分类基本信息
            cat_diffs = []
            for key in ['name', 'description']:
                if cat1[key] != cat2[key]:
                    cat_diffs.append(f"    ❌ {key}: '{cat1[key]}' vs '{cat2[key]}'")
            
            if cat_diffs:
                for diff in cat_diffs:
                    print(diff)
            else:
                print(f"    ✅ 分类信息一致")
            
            # 比较参数
            self._compare_parameters(cat1['parameters'], cat2['parameters'], cat_name)
    
    def _compare_parameters(self, params1, params2, category_name):
        """比较参数"""
        params1_dict = {param['name_en']: param for param in params1}
        params2_dict = {param['name_en']: param for param in params2}
        all_params = set(params1_dict.keys()) | set(params2_dict.keys())
        
        for param_name in sorted(all_params):
            if param_name not in params1_dict:
                print(f"    ❌ 参数 '{param_name}': 只在项目2中存在")
                continue
            elif param_name not in params2_dict:
                print(f"    ❌ 参数 '{param_name}': 只在项目1中存在")
                continue
            
            param1 = params1_dict[param_name]
            param2 = params2_dict[param_name]
            
            # 比较参数基本信息
            param_diffs = []
            for key in ['name', 'param_type', 'unit', 'description', 'is_list', 'is_year_related', 'list_length']:
                if param1[key] != param2[key]:
                    param_diffs.append(f"      ❌ {key}: '{param1[key]}' vs '{param2[key]}'")
            
            # 比较参数值
            values1 = {v['list_index']: v['value'] for v in param1['values']}
            values2 = {v['list_index']: v['value'] for v in param2['values']}
            all_indices = set(values1.keys()) | set(values2.keys())
            
            value_diffs = []
            for idx in sorted(all_indices):
                if idx not in values1:
                    value_diffs.append(f"      ❌ 值[{idx}]: 只在项目2中存在 '{values2[idx]}'")
                elif idx not in values2:
                    value_diffs.append(f"      ❌ 值[{idx}]: 只在项目1中存在 '{values1[idx]}'")
                elif values1[idx] != values2[idx]:
                    value_diffs.append(f"      ❌ 值[{idx}]: '{values1[idx]}' vs '{values2[idx]}'")
            
            if param_diffs or value_diffs:
                print(f"    ❌ 参数 '{param_name}': 存在差异")
                for diff in param_diffs + value_diffs:
                    print(diff)
            else:
                print(f"    ✅ 参数 '{param_name}': 完全一致")
    
    def _print_statistics(self, data1, data2):
        """打印统计信息"""
        print("\n" + "=" * 80)
        print("📊 统计信息:")
        
        cats1_count = len(data1['categories'])
        cats2_count = len(data2['categories'])
        params1_count = sum(len(cat['parameters']) for cat in data1['categories'])
        params2_count = sum(len(cat['parameters']) for cat in data2['categories'])
        
        print(f"  项目1: {cats1_count} 个分类, {params1_count} 个参数")
        print(f"  项目2: {cats2_count} 个分类, {params2_count} 个参数")
        
        if cats1_count != cats2_count:
            print(f"  ⚠️  分类数量不同: {cats1_count} vs {cats2_count}")
        if params1_count != params2_count:
            print(f"  ⚠️  参数数量不同: {params1_count} vs {params2_count}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='项目比较工具')
    parser.add_argument('project1', help='第一个项目名称（英文）')
    parser.add_argument('project2', help='第二个项目名称（英文）')
    parser.add_argument('--details', '-d', action='store_true', 
                       help='显示详细差异信息（默认：仅显示是否一致）')
    parser.add_argument('--quiet', '-q', action='store_true', 
                       help='静默模式，只返回退出码')
    
    args = parser.parse_args()
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        comparator = ProjectComparator(db)
        is_consistent = comparator.compare_projects(
            args.project1, 
            args.project2, 
            show_details=args.details
        )
        
        if args.quiet:
            # 静默模式，只返回退出码
            return 0 if is_consistent else 1
        else:
            return 0 if is_consistent else 1
            
    except Exception as e:
        if not args.quiet:
            print(f"❌ 错误: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
