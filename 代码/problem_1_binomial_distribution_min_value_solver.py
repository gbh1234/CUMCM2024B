import scipy.stats as stats

# 定义标称次品率 p0 和显著性水平 alpha
p0 = 0.1
alpha = 0.05

# 计算从 n = 1 到 n = 29 的样本数及临界值
def find_critical_values_binomial(p0, alpha, max_n=29):
    results = []
    for n in range(1, max_n + 1):
        for k in range(n + 1):
            # 计算二项分布的右尾概率
            p_value = 1 - stats.binom.cdf(k - 1, n, p0)
            if p_value < alpha:
                results.append((n, k, p_value))  # 存储 n, k 和 p 值
                break  # 找到第一个符合条件的 k 就跳出循环
    return results

# 计算 n 从 1 到 29 的临界值 k 和 p 值
results = find_critical_values_binomial(p0, alpha)

# 输出结果
for n, k, p_value in results:
    print(f"样本量 n = {n}, 临界值 k = {k}, 对应 p 值 = {p_value:.6f}")

