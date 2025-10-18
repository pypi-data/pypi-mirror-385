#!/usr/bin/env python3
"""
参数管理系统 Python 客户端与Pyomo集成示例
"""
from param_management_client import ParameterClient

try:
    import pyomo.environ as pyo
    PYOMO_AVAILABLE = True
except ImportError:
    PYOMO_AVAILABLE = False
    print("Pyomo未安装，跳过集成示例")


def pyomo_optimization_example():
    """Pyomo优化建模示例"""
    if not PYOMO_AVAILABLE:
        return
    
    print("=== Pyomo集成示例 ===")
    
    # 创建客户端
    client = ParameterClient(
        host="localhost",
        port=8000,
        project_name="energy_optimization_params"
    )
    project = client.get_project()
    
    # 创建Pyomo模型
    model = pyo.ConcreteModel()
    
    # 定义时间集合
    model.T = pyo.Set(initialize=range(project.time_horizon))
    
    # 从参数系统获取数据（自动类型转换）
    wind_capital_ratio = project.wind_params.capital_ratio
    wind_unit_cost = project.wind_params.unit_investment_cost
    wind_electricity_price = project.wind_params.electricity_price
    
    print(f"风能资本比例: {wind_capital_ratio}")
    print(f"风能单位成本: {wind_unit_cost} {project.wind_params.unit_investment_cost.unit}")
    print(f"电价数据: {len(wind_electricity_price)} 年")
    
    # 定义Pyomo参数
    model.wind_capital_ratio = pyo.Param(initialize=wind_capital_ratio)
    model.wind_unit_cost = pyo.Param(initialize=wind_unit_cost)
    model.electricity_price = pyo.Param(
        model.T, 
        initialize=lambda m, t: wind_electricity_price[t] if t < len(wind_electricity_price) else 0
    )
    
    # 定义决策变量
    model.wind_capacity = pyo.Var(model.T, domain=pyo.NonNegativeReals)
    
    # 定义目标函数
    def objective_rule(model):
        return sum(
            model.wind_unit_cost * model.wind_capacity[t] * model.wind_capital_ratio
            for t in model.T
        )
    
    model.objective = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
    
    # 定义约束
    def demand_constraint_rule(model, t):
        return model.wind_capacity[t] >= 100  # 最小容量约束
    
    model.demand_constraint = pyo.Constraint(model.T, rule=demand_constraint_rule)
    
    print("Pyomo模型创建成功！")
    print(f"时间步数: {len(model.T)}")
    print(f"决策变量数: {len(model.wind_capacity)}")
    print(f"约束数: {len(model.demand_constraint)}")
    
    # 尝试不同的求解器
    solvers_to_try = ['pulp', 'cbc', 'glpk', 'cplex', 'gurobi']
    solver = None
    results = None
    
    for solver_name in solvers_to_try:
        try:
            solver = pyo.SolverFactory(solver_name)
            if solver.available():
                print(f"使用求解器: {solver_name}")
                results = solver.solve(model, tee=False)
                break
            else:
                print(f"求解器 {solver_name} 不可用")
        except Exception as e:
            print(f"求解器 {solver_name} 初始化失败: {e}")
            continue
    
    if results is None:
        print("警告: 没有可用的求解器，模型已创建但无法求解")
        print("请安装以下求解器之一:")
        print("- PuLP: pip install pulp")
        print("- CBC: 下载并安装 CBC 求解器")
        print("- GLPK: 下载并安装 GLPK 求解器")
        return
    
    # 检查求解结果
    if results.solver.termination_condition == pyo.TerminationCondition.optimal:
        print("优化求解成功！")
        print(f"目标函数值: {pyo.value(model.objective):.2f}")
        
        # 显示部分决策变量值
        print("前5个时间步的风电容量:")
        for t in list(model.T)[:5]:
            print(f"  时间 {t}: {model.wind_capacity[t].value:.2f} kW")
    else:
        print(f"求解失败: {results.solver.termination_condition}")


def main():
    """主函数"""
    print("参数管理系统 Python 客户端 Pyomo集成示例")
    print("=" * 50)
    
    if PYOMO_AVAILABLE:
        pyomo_optimization_example()
    else:
        print("请安装Pyomo以运行此示例:")
        print("pip install pyomo")


if __name__ == "__main__":
    main()
