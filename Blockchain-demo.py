import threading
import time
from Validator import UniqueEmbeddingVerifier


class Block:
    def __init__(self, curvature, miner_id):
        self.curvature = curvature
        self.miner_id = miner_id
        self.timestamp = time.time()


class Blockchain:
    def __init__(self, n, m, k, hardness):
        self.chain = []
        self.pending_blocks = []
        self.mining_event = threading.Event()
        self.lock = threading.Lock()
        self.verifier_params = (n, m, k, hardness)

    def broadcast_start(self):
        with self.lock:
            self.mining_event.set()
            self.pending_blocks = []
        print("\n[区块链] 挖矿开始广播")

    def broadcast_stop(self):
        with self.lock:
            self.mining_event.clear()
            if self.pending_blocks:
                best_block = max(self.pending_blocks, key=lambda x: x.curvature)
                self.chain.append(best_block)
                print(f"[区块链] 接受最优区块：曲率 {best_block.curvature:.4f} 来自 {best_block.miner_id}")
            print(f"[区块链] 本轮共收到 {len(self.pending_blocks)} 个候选区块")
        print("[区块链] 挖矿结束广播")

    def submit_block(self, block):
        with self.lock:
            if self.mining_event.is_set():
                self.pending_blocks.append(block)
                print(f"[矿工 {block.miner_id}] 提交候选区块，曲率 {block.curvature:.4f}")
                return True
        return False


class Miner:
    def __init__(self, miner_id, blockchain):
        self.id = miner_id
        self.blockchain = blockchain
        self.thread = None

    def start_mining(self):
        def mining_process():
            params = self.blockchain.verifier_params
            while self.blockchain.mining_event.is_set():
                verifier = UniqueEmbeddingVerifier(*params)
                if solver := verifier.solve(search_scale=0.5):
                    curvature = verifier.get_curvature()
                    self.blockchain.submit_block(Block(curvature, self.id))
                time.sleep(0.1)

        self.thread = threading.Thread(target=mining_process)
        self.thread.start()
