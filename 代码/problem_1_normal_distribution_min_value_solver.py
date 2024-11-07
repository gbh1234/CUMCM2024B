import math
from scipy import stats

def calculate_sample_size(p, confidence, margin_of_error):
    z = stats.norm.ppf((1 + confidence) / 2)
    return math.ceil((z**2 * p * (1-p)) / (margin_of_error**2))

def calculate_rejection_threshold(n, p, confidence):
    return math.ceil(stats.binom.ppf(confidence, n, p))

def calculate_acceptance_threshold(n, p, confidence):
    return math.floor(stats.binom.isf(1 - confidence, n, p))

def find_optimal_sample_size(p, confidence):
    n = calculate_sample_size(p, confidence, 0.05)  # 使用5%的误差范围作为起始点
    threshold = calculate_rejection_threshold(n, p, confidence)
    return n, threshold

# 参数设置
p = 0.10  # 标称次品率

# 情况1：95%的信度下认定零配件次品率超过标称值
print("情况1：95%的信度下认定零配件次品率超过标称值")
n1, threshold1 = find_optimal_sample_size(p, 0.95)
print(f"抽样数量: {n1}")
print(f"拒收阈值: 如果不合格品数量 >= {threshold1}，则拒收")
alpha1 = 1 - stats.binom.cdf(threshold1 - 1, n1, p)
print(f"第一类错误概率 (误拒概率): {alpha1:.4f}")

print("\n" + "="*50 + "\n")

# 情况2：90%的信度下认定零配件次品率不超过标称值
print("情况2：90%的信度下认定零配件次品率不超过标称值")
n2, threshold2 = find_optimal_sample_size(p, 0.90)
acceptance_threshold2 = calculate_acceptance_threshold(n2, p, 0.90)
print(f"抽样数量: {n2}")
print(f"接收阈值: 如果不合格品数量 <= {acceptance_threshold2}，则接收")
beta2 = stats.binom.cdf(acceptance_threshold2, n2, p)
print(f"第二类错误概率 (误收概率): {beta2:.4f}")
