import itertools
import pandas as pd
import random
from collections import Counter


def sample_inspection(population_size, sample_size, true_defect_rate):
    if sample_size == 0:
        return 0
    defects = sum(random.random() < true_defect_rate for _ in range(sample_size))
    return defects / sample_size


def multi_stage_production_decision_process(
    initial_quantity,
    component_params,
    semi_product_params,
    final_product_params,
    max_cycles=2
):
    total_revenue = 0
    total_cost = 0
    
    for comp in component_params:
        total_cost += initial_quantity * comp['purchase_cost']

    inventories = []
    for comp in component_params:
        if comp['inspect']:
            estimated_defect_rate = sample_inspection(initial_quantity, min(100, initial_quantity), comp['true_defect_rate'])
            inventory = int(initial_quantity * (1 - estimated_defect_rate))
            total_cost += initial_quantity * comp['inspection_cost']
        else:
            inventory = initial_quantity
        inventories.append(inventory)

    semi_product_inventories = [0] * len(semi_product_params)

    for cycle in range(max_cycles):
        semi_products = []
        for idx, semi_prod in enumerate(semi_product_params):
            assembled = min([inventories[i-1] for i in semi_prod['components']])
            assembled += semi_product_inventories[idx]
            semi_product_inventories[idx] = 0
            
            for i in semi_prod['components']:
                inventories[i-1] -= min(assembled, inventories[i-1])
            total_cost += assembled * semi_prod['assembly_cost']

            semi_product_quality = 1.0
            for i in semi_prod['components']:
                if not component_params[i-1]['inspect']:
                    semi_product_quality *= (1 - component_params[i-1]['true_defect_rate'])
            semi_product_quality *= (1 - semi_prod['true_defect_rate'])

            actual_qualified = int(assembled * semi_product_quality)
            if semi_prod['inspect'] and assembled > 0:
                estimated_defect_rate = sample_inspection(assembled, min(100, assembled), 1 - semi_product_quality)
                qualified = int(assembled * (1 - estimated_defect_rate))
                defective = assembled - qualified
                total_cost += assembled * semi_prod['inspection_cost']
                if semi_prod['disassemble']:
                    total_cost += defective * semi_prod['disassembly_cost']
                    for i in semi_prod['components']:
                        inventories[i-1] += defective
            else:
                qualified = assembled

            semi_products.append((qualified, actual_qualified))

        final_assembled = min([sp[0] for sp in semi_products])
        total_cost += final_assembled * final_product_params['assembly_cost']
        
        final_quality = 1.0
        for idx, sp in enumerate(semi_products):
            qualified, actual_qualified = sp
            semi_product_quality = actual_qualified / qualified if qualified > 0 else 0
            final_quality *= semi_product_quality
        final_quality *= (1 - final_product_params['true_defect_rate'])  

        actual_qualified_products = int(final_assembled * final_quality)

        if final_product_params['inspect'] and final_assembled > 0:
            estimated_defect_rate = sample_inspection(final_assembled, min(100, final_assembled), 1 - final_quality)
            qualified_products = int(final_assembled * (1 - estimated_defect_rate))
            defective_products = final_assembled - qualified_products
            total_cost += final_assembled * final_product_params['inspection_cost']
            returned_products = 0
        else:
            qualified_products = actual_qualified_products
            defective_products = final_assembled - qualified_products
            returned_products = defective_products
            total_cost += returned_products * final_product_params['return_loss']
        
        total_revenue += qualified_products * final_product_params['market_price']
        
        total_defective = defective_products
        if total_defective > 0 and final_product_params['disassemble']:
            total_cost += total_defective * final_product_params['disassembly_cost']
            for i in range(len(semi_product_params)):
                semi_product_inventories[i] += total_defective // len(semi_product_params)

    profit = total_revenue - total_cost
    return profit, total_revenue, total_cost

def optimize_multi_stage_decisions(params, decision_combinations):
    best_profit = float('-inf')
    best_decision = None

    for decisions in decision_combinations:
        for i, decision in enumerate(decisions[:8]):
            params['component_params'][i]['inspect'] = decision
        for i, decision in enumerate(decisions[8:11]):
            params['semi_product_params'][i]['inspect'] = decision
        for i, decision in enumerate(decisions[11:14]):
            params['semi_product_params'][i]['disassemble'] = decision
        params['final_product_params']['inspect'] = decisions[14]
        params['final_product_params']['disassemble'] = decisions[15]
        
        profit, revenue, cost = multi_stage_production_decision_process(**params)
        
        if profit > best_profit:
            best_profit = profit
            best_decision = decisions
    
    return best_decision, best_profit


def run_multiple_simulations(params, decision_combinations, num_simulations=1000):
    best_decisions = []
    for _ in range(num_simulations):
        best_decision, best_profit = optimize_multi_stage_decisions(params, decision_combinations)
        best_decisions.append(best_decision)
    
    decision_counts = Counter(tuple(decision) for decision in best_decisions)
    return decision_counts


def main():
    params = {
        'initial_quantity': 1000,
        'component_params': [
            {'true_defect_rate': 0.10, 'purchase_cost': 2, 'inspection_cost': 1, 'inspect': False},
            {'true_defect_rate': 0.10, 'purchase_cost': 8, 'inspection_cost': 1, 'inspect': False},
            {'true_defect_rate': 0.10, 'purchase_cost': 12, 'inspection_cost': 2, 'inspect': False},
            {'true_defect_rate': 0.10, 'purchase_cost': 2, 'inspection_cost': 1, 'inspect': False},
            {'true_defect_rate': 0.10, 'purchase_cost': 8, 'inspection_cost': 1, 'inspect': False},
            {'true_defect_rate': 0.10, 'purchase_cost': 12, 'inspection_cost': 2, 'inspect': False},
            {'true_defect_rate': 0.10, 'purchase_cost': 8, 'inspection_cost': 1, 'inspect': False},
            {'true_defect_rate': 0.10, 'purchase_cost': 12, 'inspection_cost': 2, 'inspect': False}
        ],
        'semi_product_params': [
            {'true_defect_rate': 0.10, 'assembly_cost': 8, 'inspection_cost': 4, 'disassembly_cost': 6, 'components': [1, 2, 3], 'inspect': False, 'disassemble': False},
            {'true_defect_rate': 0.10, 'assembly_cost': 8, 'inspection_cost': 4, 'disassembly_cost': 6, 'components': [4, 5, 6], 'inspect': False, 'disassemble': False},
            {'true_defect_rate': 0.10, 'assembly_cost': 8, 'inspection_cost': 4, 'disassembly_cost': 6, 'components': [7, 8], 'inspect': False, 'disassemble': False}
        ],
        'final_product_params': {
            'true_defect_rate': 0.10, 'assembly_cost': 8, 'inspection_cost': 6, 'market_price': 200,
            'disassembly_cost': 10, 'return_loss': 40, 'inspect': False, 'disassemble': False
        }
    }

    # 从文件中读取决策组合
    with open('decision_combinations.txt', 'r') as f:
        decision_combinations = [eval(line.strip()) for line in f]

    decision_counts = run_multiple_simulations(params, decision_combinations)
    
    print("最优策略统计结果:")
    for decision, count in decision_counts.most_common():
        print(f"策略: {decision}, 出现次数: {count}")

    df = pd.DataFrame([
        {"Strategy": str(decision), "Count": count}
        for decision, count in decision_counts.items()
    ])
    df.to_excel("optimal_strategies_distribution.xlsx", index=False)
    print("结果已保存到 optimal_strategies_distribution.xlsx 文件中。")


if __name__ == "__main__":
    main()