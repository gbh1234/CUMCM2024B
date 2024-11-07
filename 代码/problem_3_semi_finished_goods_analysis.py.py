import itertools
import pandas as pd


def multi_stage_production_decision_process(
    initial_quantity,
    component_params,
    semi_product_params,
    final_product_params,
    max_cycles=3
    ):
    total_revenue = 0
    total_cost = 0
    
    # 零件初始购买成本
    for comp in component_params:
        total_cost += initial_quantity * comp['purchase_cost']

    # 零件检测和初始库存计算
    inventories = []
    for comp in component_params:
        if comp['inspect']:
            inventory = int(initial_quantity * (1 - comp['defect_rate']))
            total_cost += initial_quantity * comp['inspection_cost']
        else:
            inventory = initial_quantity
        inventories.append(inventory)

    # 半成品库存
    semi_product_inventories = [0] * len(semi_product_params)

    for cycle in range(max_cycles):
        # 半成品的装配与检测
        semi_products = []
        for idx, semi_prod in enumerate(semi_product_params):
            assembled = min([inventories[i-1] for i in semi_prod['components']])
            assembled += semi_product_inventories[idx]  # 加上之前的半成品库存
            semi_product_inventories[idx] = 0  # 清空半成品库存
            
            for i in semi_prod['components']:
                inventories[i-1] -= min(assembled, inventories[i-1])
            total_cost += assembled * semi_prod['assembly_cost']

            # 计算半成品的实际合格率
            semi_product_quality = 1.0
            for i in semi_prod['components']:
                if not component_params[i-1]['inspect']:
                    semi_product_quality *= (1 - component_params[i-1]['defect_rate'])
            semi_product_quality *= (1 - semi_prod['defect_rate'])  # 考虑装配过程的次品率

            actual_qualified = int(assembled * semi_product_quality)
            if semi_prod['inspect']:
                qualified = actual_qualified
                defective = assembled - qualified
                total_cost += assembled * semi_prod['inspection_cost']
                if semi_prod['disassemble']:
                    total_cost += defective * semi_prod['disassembly_cost']
                    for i in semi_prod['components']:
                        inventories[i-1] += defective
            else:
                qualified = assembled  # 不检验时，所有产品都进入下一阶段，包括不合格品

            semi_products.append((qualified, actual_qualified))

        # 成品的装配与检测
        final_assembled = min([sp[0] for sp in semi_products])
        total_cost += final_assembled * final_product_params['assembly_cost']
        
        # 计算成品的实际合格率
        final_quality = 1.0

        # 考虑每个半成品的实际合格率，而不是仅考虑是否检测
        for idx, sp in enumerate(semi_products):
            qualified, actual_qualified = sp
            semi_product_quality = actual_qualified / qualified if qualified > 0 else 0
            final_quality *= semi_product_quality

        # 再考虑成品装配过程的次品率
        final_quality *= (1 - final_product_params['defect_rate'])  

        actual_qualified_products = int(final_assembled * final_quality)

        if final_product_params['inspect']:
            qualified_products = actual_qualified_products
            defective_products = final_assembled - qualified_products
            total_cost += final_assembled * final_product_params['inspection_cost']
            returned_products = 0
        else:
            qualified_products = actual_qualified_products
            defective_products = final_assembled - qualified_products
            returned_products = defective_products# 实际不合格品最终会被退回
            total_cost += returned_products * final_product_params['return_loss']
        
        # 销售收入
        total_revenue += qualified_products * final_product_params['market_price']
        
        # 处理不合格品
        total_defective = defective_products
        if total_defective > 0 and final_product_params['disassemble']:
            total_cost += total_defective * final_product_params['disassembly_cost']
            # 将拆解的成品均匀分配到各个半成品库存中
            for i in range(len(semi_product_params)):
                semi_product_inventories[i] += total_defective // len(semi_product_params)

    # 返回总利润
    profit = total_revenue - total_cost
    return profit, total_revenue, total_cost

def optimize_multi_stage_decisions(params):
    decision_data = []

    for decisions in itertools.product([True, False], repeat=16):  # 8个零件 + 3个半成品检测 + 3个半成品拆解 + 1个成品检测 + 1个拆解决策
        for i, decision in enumerate(decisions[:8]):
            params['component_params'][i]['inspect'] = decision
        for i, decision in enumerate(decisions[8:11]):
            params['semi_product_params'][i]['inspect'] = decision
        for i, decision in enumerate(decisions[11:14]):
            params['semi_product_params'][i]['disassemble'] = decision
        params['final_product_params']['inspect'] = decisions[14]
        params['final_product_params']['disassemble'] = decisions[15]
        
        profit, revenue, cost = multi_stage_production_decision_process(**params)
        
        # 保存决策与结果
        decision_data.append({
            'Decisions': decisions,
            'Profit': profit,
            'Revenue': revenue,
            'Cost': cost
        })
    
    return decision_data

def save_decision_data_to_excel(decision_data, file_name):
    # 将决策数据转换为DataFrame
    df = pd.DataFrame(decision_data)
    
    # 将数据保存到Excel文件
    df.to_excel(file_name, index=False)

def main():
    params = {
        'initial_quantity': 1000,
        'component_params': [
            {'defect_rate': 0.10, 'purchase_cost': 2, 'inspection_cost': 1, 'inspect': False},
            {'defect_rate': 0.10, 'purchase_cost': 8, 'inspection_cost': 1, 'inspect': False},
            {'defect_rate': 0.10, 'purchase_cost': 12, 'inspection_cost': 2, 'inspect': False},
            {'defect_rate': 0.10, 'purchase_cost': 2, 'inspection_cost': 1, 'inspect': False},
            {'defect_rate': 0.10, 'purchase_cost': 8, 'inspection_cost': 1, 'inspect': False},
            {'defect_rate': 0.10, 'purchase_cost': 12, 'inspection_cost': 2, 'inspect': False},
            {'defect_rate': 0.10, 'purchase_cost': 8, 'inspection_cost': 1, 'inspect': False},
            {'defect_rate': 0.10, 'purchase_cost': 12, 'inspection_cost': 2, 'inspect': False}
        ],
        'semi_product_params': [
            {'defect_rate': 0.10, 'assembly_cost': 8, 'inspection_cost': 4, 'disassembly_cost': 6, 'components': [1, 2, 3], 'inspect': False, 'disassemble': False},
            {'defect_rate': 0.10, 'assembly_cost': 8, 'inspection_cost': 4, 'disassembly_cost': 6, 'components': [4, 5, 6], 'inspect': False, 'disassemble': False},
            {'defect_rate': 0.10, 'assembly_cost': 8, 'inspection_cost': 4, 'disassembly_cost': 6, 'components': [7, 8], 'inspect': False, 'disassemble': False}
        ],
        'final_product_params': {
            'defect_rate': 0.10, 'assembly_cost': 8, 'inspection_cost': 6, 'market_price': 200,
            'disassembly_cost': 10, 'return_loss': 40, 'inspect': False, 'disassemble': False
        }
    }

    decision_data = optimize_multi_stage_decisions(params)
    
    # 保存到Excel文件
    save_decision_data_to_excel(decision_data, 'multi_stage_production_results.xlsx')
    print("所有决策的利润数据已保存到 multi_stage_production_results.xlsx 文件中。")

    # 找出最佳决策
    best_decision = max(decision_data, key=lambda x: x['Profit'])
    print("\n最佳决策:")
    print(f"决策: {best_decision['Decisions']}")
    print(f"利润: {best_decision['Profit']:.2f}")
    print(f"收入: {best_decision['Revenue']:.2f}")
    print(f"成本: {best_decision['Cost']:.2f}")

if __name__ == "__main__":
    main()