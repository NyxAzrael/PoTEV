# 修改后的blockchain.py
import hashlib
import json
import time
import numpy as np
from Validator import UniqueEmbeddingVerifier


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, proof_data):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.proof_data = proof_data  # 存储A、b和manifold
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """计算区块哈希"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "A": self.proof_data["A"].tolist(),
            "b": self.proof_data["b"].tolist()
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self, n=2, m=5, k=1.0, hardness=20):
        self.n = n
        self.m = m
        self.k = k
        self.hardness = hardness
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 0.5  # 初始搜索范围系数

    def create_genesis_block(self):
        """修复创世区块初始化问题"""
        return Block(0, time.time(), [], "0", {
            "A": np.zeros((self.m, 2 * self.n)),
            "b": np.zeros(self.m),
            "manifold": np.zeros((10, 2 * self.n))  # 简化初始样本
        })

    def add_transaction(self, sender, recipient, amount):
        """添加交易到待处理列表"""
        self.pending_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "timestamp": time.time()
        })

    def mine_pending_transactions(self):
        """修复挖矿逻辑"""
        last_block = self.chain[-1]

        verifier = UniqueEmbeddingVerifier(self.n, self.m, self.k, self.hardness)

        # 获取嵌入参数和函数
        if result := self.find_valid_embedding(verifier):
            A, b, embed_func = result
            new_proof = {
                "A": A,
                "b": b,
                "manifold": verifier.manifold
            }

            new_block = Block(
                index=last_block.index + 1,
                timestamp=time.time(),
                transactions=self.pending_transactions,
                previous_hash=last_block.hash,
                proof_data=new_proof
            )

            if self.validate_block(new_block, verifier):
                self.chain.append(new_block)
                self.pending_transactions = []
                return new_block
        return None

    def find_valid_embedding(self, verifier):
        """改进的嵌入搜索方法"""
        for _ in range(1000):
            A = np.random.randn(verifier.m, 2 * verifier.n) * 0.5 * self.difficulty
            b = np.random.randn(verifier.m) * 0.1 * self.difficulty

            embedded = verifier.manifold @ A.T + b

            if (verifier._check_self_intersection(embedded) and
                    verifier._check_curvature(embedded)):
                return A, b, lambda x: x @ A.T + b
        return None

    def validate_block(self, block, verifier):
        """改进的区块验证"""
        # 验证哈希链
        if block.previous_hash != self.chain[-1].hash:
            return False

        # 验证数学证明
        try:
            embedded = block.proof_data["manifold"] @ block.proof_data["A"].T + block.proof_data["b"]
            return (verifier._check_self_intersection(embedded) and
                    verifier._check_curvature(embedded))
        except:
            return False


# 示例用法
if __name__ == "__main__":
    chain = Blockchain()

    # 添加测试交易
    chain.add_transaction("Alice", "Bob", 5.0)

    # 挖矿
    if new_block := chain.mine_pending_transactions():
        print(f"新区块哈希: {new_block.hash[:16]}...")
        print(f"包含交易数: {len(new_block.transactions)}")
    else:
        print("挖矿失败")
