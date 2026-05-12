import unittest
from blockchain import Node


class TestBlockchainIntegration(unittest.TestCase):
    def test_mine_and_sync(self):
        # 降低难度以便测试运行快速
        node1 = Node("Node1", difficulty=3)
        node2 = Node("Node2", difficulty=3)

        # 添加交易
        node1.add_transaction("Alice", "Bob", 10.0)
        node1.add_transaction("Bob", "Charlie", 5.0)

        # 节点1 挖矿
        block = node1.mine()
        self.assertEqual(node1.get_chain_length(), 2)

        # 节点2 从节点1 同步
        synced = node2.sync_from(node1)
        self.assertGreaterEqual(synced, 1)
        self.assertEqual(node2.get_chain_length(), node1.get_chain_length())

        # 验证链完整性
        self.assertTrue(node1.blockchain.is_chain_valid())
        self.assertTrue(node2.blockchain.is_chain_valid())


if __name__ == "__main__":
    unittest.main()
