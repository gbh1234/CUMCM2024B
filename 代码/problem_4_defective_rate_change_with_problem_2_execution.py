import random
import itertools
from scipy import stats


def sample_inspection(population_size, sample_size, true_defect_rate):
    """
    Perform a sample inspection and estimate the defect rate.
    """
    defects = sum(random.random() < true_defect_rate for _ in range(sample_size))
    sample_defect_rate = defects / sample_size
    
    # Calculate standard error
    std_error = (sample_defect_rate * (1 - sample_defect_rate) / sample_size) ** 0.5
    
    # Calculate confidence interval
    ci_lower = max(0, sample_defect_rate - 1.96 * std_error)
    ci_upper = min(1, sample_defect_rate + 1.96 * std_error)
    
    return sample_defect_rate, (ci_lower, ci_upper)


def improved_production_decision_process(
    initial_quantity,
    true_defect_rate_1, purchase_cost_1, inspection_cost_1,
    true_defect_rate_2, purchase_cost_2, inspection_cost_2,
    true_defect_rate_product, assembly_cost, inspection_cost_product,
    market_price, return_loss, disassembly_cost,
    inspect_component_1=True, inspect_component_2=True, inspect_product=True, 
    disassemble_defective=True, max_cycles=2,
    sample_size_1=100, sample_size_2=100, sample_size_product=100
):
    total_revenue = 0
    total_cost = 0
    
    # Initial purchase cost
    total_cost += initial_quantity * (purchase_cost_1 + purchase_cost_2)
    
    # Sample inspection of components
    defect_rate_1, _ = sample_inspection(initial_quantity, sample_size_1, true_defect_rate_1)
    defect_rate_2, _ = sample_inspection(initial_quantity, sample_size_2, true_defect_rate_2)
    
    if inspect_component_1:
        inventory_1 = int(initial_quantity * (1 - defect_rate_1))
        total_cost += initial_quantity * inspection_cost_1
    else:
        inventory_1 = initial_quantity
    
    if inspect_component_2:
        inventory_2 = int(initial_quantity * (1 - defect_rate_2))
        total_cost += initial_quantity * inspection_cost_2
    else:
        inventory_2 = initial_quantity
    
    for cycle in range(max_cycles):
        # Calculate current batch quality rate
        part1_quality = 1 - defect_rate_1 if not inspect_component_1 else 1.0
        part2_quality = 1 - defect_rate_2 if not inspect_component_2 else 1.0
        
        if inventory_1 == 0 or inventory_2 == 0:
            break

        assembled_products = min(inventory_1, inventory_2)
        
        inventory_1 -= assembled_products
        inventory_2 -= assembled_products
        total_cost += assembled_products * assembly_cost
        
        # Sample inspection of products
        defect_rate_product, _ = sample_inspection(assembled_products, sample_size_product, true_defect_rate_product)
        product_quality = part1_quality * part2_quality * (1 - defect_rate_product)
        
        if inspect_product:
            qualified_products = int(assembled_products * product_quality)
            defective_products = assembled_products - qualified_products
            total_cost += assembled_products * inspection_cost_product
            returned_products = 0
        else:
            qualified_products = int(assembled_products * product_quality)
            defective_products = assembled_products - qualified_products
            returned_products = defective_products
            total_cost += returned_products * return_loss

        total_revenue += qualified_products * market_price
        
        total_defective = defective_products

        if total_defective > 0:
            if disassemble_defective:
                total_cost += total_defective * disassembly_cost
                inventory_1 += total_defective
                inventory_2 += total_defective
            else:
                total_defective = 0

    profit = total_revenue - total_cost
    return profit, total_revenue, total_cost


def optimize_decisions(params):
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
        if profit > best_profit:
            best_profit = profit
            best_decisions = decisions
    
    return best_profit, best_decisions


def main():
    params = {
        'initial_quantity': 1000,
        'assembly_cost': 6, 'market_price': 56
    }

    table_cases = [
        {'true_defect_rate_1': 0.10, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'true_defect_rate_2': 0.10, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'true_defect_rate_product': 0.10, 'return_loss': 6, 'disassembly_cost': 5, 'inspection_cost_product': 3},
        
        {'true_defect_rate_1': 0.20, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'true_defect_rate_2': 0.20, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'true_defect_rate_product': 0.20, 'return_loss': 6, 'disassembly_cost': 5, 'inspection_cost_product': 3},
        
        {'true_defect_rate_1': 0.10, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'true_defect_rate_2': 0.10, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'true_defect_rate_product': 0.10, 'return_loss': 30, 'disassembly_cost': 5, 'inspection_cost_product': 3},
        
        {'true_defect_rate_1': 0.20, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'true_defect_rate_2': 0.20, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'true_defect_rate_product': 0.20, 'return_loss': 30, 'disassembly_cost': 5, 'inspection_cost_product': 2},
        
        {'true_defect_rate_1': 0.10, 'purchase_cost_1': 4, 'inspection_cost_1': 8,
         'true_defect_rate_2': 0.20, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'true_defect_rate_product': 0.10, 'return_loss': 10, 'disassembly_cost': 5, 'inspection_cost_product': 2},
        
        {'true_defect_rate_1': 0.05, 'purchase_cost_1': 4, 'inspection_cost_1': 2,
         'true_defect_rate_2': 0.05, 'purchase_cost_2': 18, 'inspection_cost_2': 3,
         'true_defect_rate_product': 0.05, 'return_loss': 10, 'disassembly_cost': 40, 'inspection_cost_product': 3}
    ]

    num_simulations = 1000  # Number of simulations for each case

    for i, case in enumerate(table_cases, 1):
        case_params = params.copy()
        case_params.update(case)
        
        total_profit = 0
        best_decisions_count = {(True, True, True, True): 0, (True, True, True, False): 0,
                                (True, True, False, True): 0, (True, True, False, False): 0,
                                (True, False, True, True): 0, (True, False, True, False): 0,
                                (True, False, False, True): 0, (True, False, False, False): 0,
                                (False, True, True, True): 0, (False, True, True, False): 0,
                                (False, True, False, True): 0, (False, True, False, False): 0,
                                (False, False, True, True): 0, (False, False, True, False): 0,
                                (False, False, False, True): 0, (False, False, False, False): 0}
        
        for _ in range(num_simulations):
            best_profit, best_decisions = optimize_decisions(case_params)
            total_profit += best_profit
            best_decisions_count[best_decisions] += 1
        
        avg_profit = total_profit / num_simulations
        most_common_decision = max(best_decisions_count, key=best_decisions_count.get)
        
        print(f"\nCase {i}:")
        print(f"Parameters: {case}")
        print(f"Average best profit: {avg_profit:.2f}")
        print(f"Most common best decision: Inspect Component 1: {most_common_decision[0]}, "
              f"Inspect Component 2: {most_common_decision[1]}, "
              f"Inspect Product: {most_common_decision[2]}, "
              f"Disassemble Defective: {most_common_decision[3]}")
        print(f"Decision distribution: {best_decisions_count}")


if __name__ == "__main__":
    main()