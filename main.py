from blockchain import Node

# 创建两个节点
node1 = Node("Node1")
node2 = Node("Node2")

# 添加交易
node1.add_transaction("Alice", "Bob", 10.0)
node1.add_transaction("Bob", "Charlie", 5.0)

# 节点1 挖矿
node1.mine()

# 节点2 从节点1 同步
node2.sync_from(node1)

print(f"节点1 链长度: {node1.get_chain_length()}")
print(f"节点2 链长度: {node2.get_chain_length()}")
