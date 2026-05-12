"""
一个简易但功能完整的区块链实现，包含：
1. 工作量证明（PoW）出块
2. 交易打包进入区块
3. 节点间区块同步

纯 Python 实现，无外部依赖，方便理解和测试。
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional


# ==================== 交易 ====================
@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Transaction":
        return cls(
            sender=d["sender"],
            receiver=d["receiver"],
            amount=d["amount"],
            timestamp=d["timestamp"],
        )

    def to_hashable_string(self) -> str:
        return f"{self.sender}->{self.receiver}:{self.amount}:{self.timestamp}"


# ==================== 区块 ====================
@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list  # list[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Block":
        block = cls(
            index=d["index"],
            timestamp=d["timestamp"],
            transactions=[Transaction.from_dict(tx) for tx in d["transactions"]],
            previous_hash=d["previous_hash"],
            nonce=d["nonce"],
            hash=d["hash"],
        )
        return block

    def compute_hash(self) -> str:
        """计算区块头部的 SHA256 哈希"""
        header = (
            f"{self.index}"
            f"{self.timestamp}"
            f"{self._transactions_hash()}"
            f"{self.previous_hash}"
            f"{self.nonce}"
        )
        return hashlib.sha256(header.encode("utf-8")).hexdigest()

    def _transactions_hash(self) -> str:
        """将交易列表序列化后取哈希"""
        tx_str = "|".join(tx.to_hashable_string() for tx in self.transactions)
        return hashlib.sha256(tx_str.encode("utf-8")).hexdigest()


# ==================== 区块链 ====================
class Blockchain:
    def __init__(self, difficulty: int = 4):
        """
        初始化区块链
        :param difficulty: PoW 难度，即区块哈希要求的前导零数量
        """
        self.difficulty = difficulty
        self.pending_transactions: list = []
        self.chain: list = []
        self.mining_reward = 50.0  # 矿工奖励
        self._create_genesis_block()

    def _create_genesis_block(self):
        """创建创世区块（固定时间戳，确保所有节点的创世区块一致）"""
        genesis_tx = Transaction(sender="0", receiver="genesis", amount=0, timestamp=0)
        genesis_block = Block(
            index=0,
            timestamp=0,
            transactions=[genesis_tx],
            previous_hash="0" * 64,
        )
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    @property
    def length(self) -> int:
        return len(self.chain)

    def add_transaction(self, sender: str, receiver: str, amount: float) -> Transaction:
        """将一笔交易加入待打包池"""
        tx = Transaction(sender=sender, receiver=receiver, amount=amount)
        self.pending_transactions.append(tx)
        return tx

    def mine_pending_transactions(self, miner_address: str) -> Block:
        """
        工作量证明挖矿：将待打包交易打包成新区块
        :param miner_address: 矿工地址，用于接收挖矿奖励
        :return: 新挖出的区块
        """
        # 矿工奖励交易
        reward_tx = Transaction(
            sender="network", receiver=miner_address, amount=self.mining_reward
        )

        # 待打包交易 = 矿工奖励 + 所有 pending 交易
        block_transactions = [reward_tx] + list(self.pending_transactions)

        new_block = Block(
            index=self.last_block.index + 1,
            timestamp=time.time(),
            transactions=block_transactions,
            previous_hash=self.last_block.hash,
        )

        # —— PoW 工作量证明 ——
        target_prefix = "0" * self.difficulty
        nonce = 0
        start = time.time()
        while True:
            new_block.nonce = nonce
            candidate_hash = new_block.compute_hash()
            if candidate_hash.startswith(target_prefix):
                new_block.hash = candidate_hash
                elapsed = time.time() - start
                print(
                    f"[PoW] 区块#{new_block.index} 挖出 | nonce={nonce} | "
                    f"哈希={candidate_hash[:16]}... | 耗时={elapsed:.3f}s | "
                    f"交易数={len(block_transactions)}"
                )
                break
            nonce += 1

        self.chain.append(new_block)
        self.pending_transactions.clear()
        return new_block

    def is_chain_valid(self) -> bool:
        """验证整条区块链的完整性"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # 验证当前区块哈希
            if current.hash != current.compute_hash():
                return False

            # 验证前驱哈希链接
            if current.previous_hash != previous.hash:
                return False

            # 验证 PoW 难度
            if not current.hash.startswith("0" * self.difficulty):
                return False

        return True

    def get_block_by_index(self, index: int) -> Optional[Block]:
        """按索引获取区块"""
        for block in self.chain:
            if block.index == index:
                return block
        return None

    def to_dict(self) -> list:
        """将整条链序列化为字典列表"""
        return [block.to_dict() for block in self.chain]

    @classmethod
    def from_dict(cls, data: list, difficulty: int = 4) -> "Blockchain":
        """从字典列表重建区块链"""
        bc = cls(difficulty=difficulty)
        bc.chain = [Block.from_dict(d) for d in data]
        return bc


# ==================== 节点 ====================
class Node:
    """
    模拟区块链网络中的一个节点。
    每个节点维护自己的一条区块链副本，可以从其他节点同步区块。
    """

    def __init__(self, node_id: str, difficulty: int = 4):
        self.node_id = node_id
        self.blockchain = Blockchain(difficulty=difficulty)

    def mine(self, miner_address: str = None) -> Block:
        """本节点执行一次挖矿"""
        if miner_address is None:
            miner_address = self.node_id
        return self.blockchain.mine_pending_transactions(miner_address)

    def add_transaction(self, sender: str, receiver: str, amount: float):
        """向本节点的交易池添加交易"""
        self.blockchain.add_transaction(sender, receiver, amount)

    def get_chain_length(self) -> int:
        return self.blockchain.length

    def sync_from(self, peer: "Node") -> int:
        """
        从对等节点同步区块：下载本节点缺失的区块
        :param peer: 对等节点
        :return: 同步的区块数量
        """
        synced_count = 0
        peer_chain = peer.blockchain.chain

        for block in peer_chain:
            if block.index >= self.blockchain.length:
                # 验证该区块与本节点最后区块的链接
                if block.index > 0:
                    prev_in_local = self.blockchain.get_block_by_index(block.index - 1)
                    if prev_in_local is None:
                        continue  # 跳过无法链接的区块
                    if block.previous_hash != prev_in_local.hash:
                        continue  # 哈希不匹配，拒绝

                # 验证 PoW
                if not block.hash.startswith("0" * self.blockchain.difficulty):
                    continue

                # 验证区块自身哈希
                if block.hash != block.compute_hash():
                    continue

                self.blockchain.chain.append(block)
                synced_count += 1
                print(
                    f"[同步] 节点 {self.node_id} 从 {peer.node_id} "
                    f"同步了区块#{block.index}"
                )

        return synced_count

    def to_dict(self) -> list:
        return self.blockchain.to_dict()

    @property
    def chain(self):
        return self.blockchain.chain
