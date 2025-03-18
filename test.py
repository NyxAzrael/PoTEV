from blockchain import Blockchain,Miner

def test_blockchain():
    # 初始化区块链（2维环面嵌入5维空间，曲率限制1.0）
    blockchain = Blockchain(n=2, m=5, k=1.0, hardness=20)

    # 创建3个矿工
    miners = [Miner(f"矿工{i + 1}", blockchain) for i in range(3)]

    # 开始挖矿周期
    blockchain.broadcast_start()
    for miner in miners:
        miner.start_mining()

    # 允许挖矿10秒
    time.sleep(10)

    # 结束挖矿周期
    blockchain.broadcast_stop()

    # 等待矿工线程结束
    for miner in miners:
        if miner.thread:
            miner.thread.join(timeout=1)

    # 显示最终结果
    print("\n=== 区块链验证 ===")
    if blockchain.chain:
        print(f"区块链高度：{len(blockchain.chain)}")
        print(f"当前最佳曲率：{blockchain.chain[-1].curvature:.4f}")
        print(f"区块创建者：{blockchain.chain[-1].miner_id}")
    else:
        print("区块链尚未包含任何有效区块")


if __name__ == "__main__":
    test_blockchain()
