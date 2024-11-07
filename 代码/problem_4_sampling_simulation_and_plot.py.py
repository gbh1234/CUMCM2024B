import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def sample_inspection(population_size, sample_size, true_defect_rate):
    defects = sum(random.random() < true_defect_rate for _ in range(sample_size))
    # 添加小的随机扰动以创造连续分布
    sample_defect_rate = (defects + random.uniform(0, 1)) / (sample_size + 1)
    std_error = (sample_defect_rate * (1 - sample_defect_rate) / sample_size) ** 0.5
    ci_lower = max(0, sample_defect_rate - 1.96 * std_error)
    ci_upper = min(1, sample_defect_rate + 1.96 * std_error)
    return sample_defect_rate, (ci_lower, ci_upper)

def run_multiple_inspections(population_size, sample_size, true_defect_rate, num_simulations):
    return [sample_inspection(population_size, sample_size, true_defect_rate)[0] for _ in range(num_simulations)]

def analyze_results(results, true_defect_rate):
    mean = np.mean(results)
    std_dev = np.std(results)
    median = np.median(results)
    
    print(f"真实次品率: {true_defect_rate:.4f}")
    print(f"平均估计次品率: {mean:.4f}")
    print(f"中位数估计次品率: {median:.4f}")
    print(f"标准差: {std_dev:.4f}")
    
    sem = std_dev / np.sqrt(len(results))
    ci_lower = mean - 1.96 * sem
    ci_upper = mean + 1.96 * sem
    print(f"95%置信区间: ({ci_lower:.4f}, {ci_upper:.4f})")
    
    # 添加偏差和均方根误差
    bias = mean - true_defect_rate
    rmse = np.sqrt(np.mean((np.array(results) - true_defect_rate)**2))
    print(f"偏差: {bias:.4f}")
    print(f"均方根误差: {rmse:.4f}")

def plot_results(results, true_defect_rate):
    plt.figure(figsize=(12, 7))
    n, bins, patches = plt.hist(results, bins=50, edgecolor='black', alpha=0.7)
    plt.axvline(true_defect_rate, color='r', linestyle='dashed', linewidth=2, label='真实次品率')
    plt.axvline(np.mean(results), color='g', linestyle='dashed', linewidth=2, label='平均估计次品率')
    
    plt.xlabel('估计次品率')
    plt.ylabel('频数')
    plt.title('次品率估计分布')
    plt.legend()
    
    # 添加注释
    plt.annotate(f'真实次品率: {true_defect_rate:.4f}', xy=(0.7, 0.95), xycoords='axes fraction')
    plt.annotate(f'平均估计次品率: {np.mean(results):.4f}', xy=(0.7, 0.90), xycoords='axes fraction')
    plt.annotate(f'标准差: {np.std(results):.4f}', xy=(0.7, 0.85), xycoords='axes fraction')
    
    plt.savefig('defect_rate_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    population_size = 10000
    sample_size = 100
    true_defect_rate = 0.10
    num_simulations = 50000  # 增加模拟次数

    results = run_multiple_inspections(population_size, sample_size, true_defect_rate, num_simulations)
    
    analyze_results(results, true_defect_rate)
    plot_results(results, true_defect_rate)

    print("分布图已保存为 'defect_rate_distribution.png'")

if __name__ == "__main__":
    main()