# 区块链原理实践

基于 Python 实现的简易区块链系统，覆盖区块链三大核心原理。

## 文件结构

```
.
├── blockchain.py              # 区块链核心实现
├── tests/
│   └── test_blockchain.py     # 自动化测试（25 个用例）
├── pow_rsa_xunf.py            # PoW + RSA 签名实践
└── tests/
    └── test_pow_rsa_xunf.py   # PoW + RSA 测试
```

## blockchain.py 核心组件

| 组件 | 说明 |
|---|---|
| `Transaction` | 交易数据结构，包含发送方、接收方、金额、时间戳，支持序列化 |
| `Block` | 区块，包含索引、时间戳、交易列表、前驱哈希、nonce、自身哈希 |
| `Blockchain` | 区块链主体，管理创世块、交易池、PoW 挖矿、整链验证 |
| `Node` | 模拟网络节点，封装一条独立链，支持从对等节点同步区块 |

## 三大核心功能

### 1. 工作量证明（PoW）出块

- `Blockchain.mine_pending_transactions()` 方法
- 通过 SHA256 暴力搜索 nonce，使区块哈希满足前导零数量要求
- 难度由 `difficulty` 参数控制（默认为 4 个前导零）

```python
bc = Blockchain(difficulty=4)
bc.add_transaction("alice", "bob", 10)
new_block = bc.mine_pending_transactions("miner_address")
```

### 2. 交易打包进入区块

- `Blockchain.add_transaction()` 将交易放入待打包池
- 挖矿时自动将矿工奖励 + 所有待打包交易打包进新区块
- 挖矿完成后清空待打包池

```python
bc.add_transaction("alice", "bob", 10)      # 加入交易池
bc.add_transaction("charlie", "dave", 20)    # 再加入一笔
bc.mine_pending_transactions("miner1")       # 打包出块
```

### 3. 节点同步区块

- `Node.sync_from(peer)` 从对等节点拉取缺失区块
- 同步时验证：PoW 难度、区块哈希、前驱哈希链接
- 拒绝非法区块，确保链完整性

```python
node_a = Node("node_a")
node_a.add_transaction("alice", "bob", 10)
node_a.mine()

node_b = Node("node_b")
node_b.sync_from(node_a)  # B 从 A 同步区块
```

## 运行测试

```bash
python3 -m unittest tests.test_blockchain -v
```

25 个测试覆盖：
- 交易创建与序列化
- 区块哈希计算
- PoW 难度验证
- 交易打包正确性
- 链完整性验证（交易篡改、哈希断裂、难度伪造）
- 节点同步（两节点、三节点、增量同步、非法区块拒绝）
- 整链序列化/反序列化
