import numpy as np
from scipy.spatial import KDTree


class UniqueEmbeddingVerifier:
    def __init__(self, n, m, k,hardness):
        """
        初始化验证器
        :param n: 流形维度 (如2维环面)
        :param m: 目标空间维度 (必须 ≥ 2n)
        :param k: 允许的最大曲率
        """
        self.n = n
        self.m = m
        self.k = k
        self.hardness = hardness

        # 生成2n维环面采样点 (cosθ1, sinθ1, ..., cosθn, sinθn)
        self.manifold = self._generate_torus(self.hardness)

    def _generate_torus(self, num_points):
        """ 生成环面采样点 """
        angles = np.random.rand(num_points, self.n) * 2 * np.pi
        return np.hstack([np.cos(angles), np.sin(angles)])

    def _check_self_intersection(self, embedded):
        """ 快速自交检测 (时间复杂度O(n log n)) """
        tree = KDTree(embedded)
        return len(tree.query_pairs(0.1)) == 0  # 安全距离阈值

    def _check_curvature(self, embedded):
        """ 快速曲率估计 (基于协方差矩阵特征值) """
        cov = np.cov(embedded.T)
        return np.max(np.linalg.eigh(cov)[0]) <= self.k

    def solve(self, max_attempts=10000000, search_scale=1.0):
        """
        带难度控制的求解函数
        :param max_attempts: 最大尝试次数
        :param search_scale: 搜索范围缩放因子 (0.1-1.0)
        """
        for _ in range(max_attempts):
            # 生成候选嵌入 (控制搜索范围)
            A = np.random.randn(self.m, 2 * self.n) * 0.5 * search_scale
            b = np.random.randn(self.m) * 0.1 * search_scale

            # 执行嵌入
            embedded = self.manifold @ A.T + b

            # 快速验证
            if self._check_self_intersection(embedded) and self._check_curvature(embedded):
                # 返回嵌入函数
                return lambda x: x @ A.T + b
        return None


# 示例使用
if __name__ == "__main__":
    # 测试案例：2维环面嵌入5维空间，曲率约束1.0
    verifier = UniqueEmbeddingVerifier(n=2, m=5, k=1.0,hardness=20)

    # 简单模式 (小范围搜索)
    if embedding := verifier.solve(search_scale=0.5):
        sample = verifier.manifold[0]
        print("找到有效嵌入！示例转换：")
        print("原始点:", sample)
        print("嵌入后:", embedding(sample))
    else:
        print("未找到嵌入")
