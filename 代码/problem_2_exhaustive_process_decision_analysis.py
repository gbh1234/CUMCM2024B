import itertools
import pandas as pd


# 改进的生产决策过程函数
def improved_production_decision_process(
        initial_quantity,
        defect_rate_1, purchase_cost_1, inspection_cost_1,
        defect_rate_2, purchase_cost_2, inspection_cost_2,
        defect_rate_product, assembly_cost, inspection_cost_product,
        market_price, return_loss, disassembly_cost,
        inspect_component_1=True, inspect_component_2=True, inspect_product=True,
        disassemble_defective=True, max_cycles=2
):
    total_revenue = 0
    total_cost = 0

    # 初始购买成本
    total_cost += initial_quantity * (purchase_cost_1 + purchase_cost_2)

    # 初始零件检测 - 只在开始时进行一次
    if inspect_component_1:
        inventory_1 = int(initial_quantity * (1 - defect_rate_1))  # 检测零件1，使用合格品
        total_cost += initial_quantity * inspection_cost_1
    else:
        inventory_1 = initial_quantity  # 不检测，使用全部零件1，包括不合格品

    if inspect_component_2:
        inventory_2 = int(initial_quantity * (1 - defect_rate_2))  # 检测零件2，使用合格品
        total_cost += initial_quantity * inspection_cost_2
    else:
        inventory_2 = initial_quantity  # 不检测，使用全部零件2，包括不合格品

    for cycle in range(max_cycles):
        # 计算当前批次的零件合格率
        part1_quality = 1 - defect_rate_1 if not inspect_component_1 else 1.0
        part2_quality = 1 - defect_rate_2 if not inspect_component_2 else 1.0

        # 检查库存是否足够装配
        if inventory_1 == 0 or inventory_2 == 0:
            break  # 退出循环

        # 组装过程，成品合格率 = 零件1合格率 * 零件2合格率 * (1 - 成品次品率)
        assembled_products = min(inventory_1, inventory_2)

        # 装配成品
        inventory_1 -= assembled_products
        inventory_2 -= assembled_products
        total_cost += assembled_products * assembly_cost

        # 成品合格率的计算
        product_quality = part1_quality * part2_quality * (1 - defect_rate_product)

        # 成品检测
        if inspect_product:
            qualified_products = int(assembled_products * product_quality)
            defective_products = assembled_products - qualified_products
            total_cost += assembled_products * inspection_cost_product
            returned_products = 0  # 无退换
        else:
            qualified_products = int(assembled_products * product_quality)
            defective_products = assembled_products - qualified_products
            returned_products = defective_products
            # 销售的次品导致退货.
            total_cost += returned_products * return_loss  # 调换损失

        # 销售收入
        total_revenue += qualified_products * market_price

        # 处理不合格品
        total_defective = defective_products
        if total_defective > 0:
            if disassemble_defective:
                total_cost += total_defective * disassembly_cost
                inventory_1 += total_defective  # 拆解后的次品重新进入生产流程
                inventory_2 += total_defective
            else:
                # 如果不拆解，次品直接丢弃
                total_defective = 0

    # 返回总利润
    profit = total_revenue - total_cost
    return profit, total_revenue, total_cost


# 优化决策函数，并将结果保存为DataFrame
def optimize_decisions(params):
    decision_profits = []
    best_profit = float('-inf')
    best_decisions = None

    for decisions in itertools.product([True, False], repeat=4):
        inspect_1, inspect_2, inspect_prod, disassemble = decisions
        profit, revenue, cost = improved_production_decision_process(
            inspect_component_1=inspect_1,
            inspect_component_2=inspect_2,
            inspect_product=inspect_prod,
            disassemble_defective=disassemble,
            **params
        )
        decision_profits.append({
            "Inspect Component 1": inspect_1,
            "Inspect Component 2": inspect_2,
            "Inspect Product": inspect_prod,
            "Disassemble Defective": disassemble,
            "Profit": profit,
            "Revenue": revenue,
            "Cost": cost
        })

        # 找到利润最高的决策
        if profit > best_profit:
            best_profit = profit
            best_decisions = decisions

    return pd.DataFrame(decision_profits), best_profit, best_decisions


# 主函数，处理多个案例并将结果保存到Excel
def main():
    # 基础参数
    params = {
        'initial_quantity': 1000,
        'assembly_cost': 6, 'market_price': 56
    }

    # 分析表格中的所有情况
    table_cases = [
        {'defect_rate_1': 0.10, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'defect_rate_2': 0.10, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'defect_rate_product': 0.10, 'return_loss': 6, 'disassembly_cost': 5, 'inspection_cost_product': 3},

        {'defect_rate_1': 0.20, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'defect_rate_2': 0.20, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'defect_rate_product': 0.20, 'return_loss': 6, 'disassembly_cost': 5, 'inspection_cost_product': 3},

        {'defect_rate_1': 0.10, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'defect_rate_2': 0.10, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'defect_rate_product': 0.10, 'return_loss': 30, 'disassembly_cost': 5, 'inspection_cost_product': 3},

        {'defect_rate_1': 0.20, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'defect_rate_2': 0.20, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'defect_rate_product': 0.20, 'return_loss': 30, 'disassembly_cost': 5, 'inspection_cost_product': 2},

        {'defect_rate_1': 0.10, 'purchase_cost_1': 4, 'inspection_cost_1': 8,
         'defect_rate_2': 0.20, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'defect_rate_product': 0.10, 'return_loss': 10, 'disassembly_cost': 5, 'inspection_cost_product': 2},

        {'defect_rate_1': 0.05, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'defect_rate_2': 0.05, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'defect_rate_product': 0.05, 'return_loss': 10, 'disassembly_cost': 40, 'inspection_cost_product': 3}
    ]

    writer = pd.ExcelWriter("decision_results.xlsx", engine='xlsxwriter')

    for i, case in enumerate(table_cases, 1):
        case_params = params.copy()
        case_params.update(case)
        print(f"\nCase {i}:")
        decision_df, best_profit, best_decisions = optimize_decisions(case_params)
        print(f"Best profit: {best_profit:.2f}")
        print(f"Best decisions: Inspect Component 1: {best_decisions[0]}, "
              f"Inspect Component 2: {best_decisions[1]}, "
              f"Inspect Product: {best_decisions[2]}, "
              f"Disassemble Defective: {best_decisions[3]}")

        # 将每个案例的结果保存到Excel中
        decision_df.to_excel(writer, sheet_name=f"Case_{i}")

    writer._save()
    print("Results saved to 'decision_results.xlsx'.")


if __name__ == "__main__":
    main()
