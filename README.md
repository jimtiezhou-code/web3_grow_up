# web3_grow_up
web从认识到精通学习house

 一、完成训练作业：
   实践 POW ⽤⾃⼰的昵称 + nonce， 不断的 sha256 Hash :
   • 直到满⾜ 4 个0 开头，打印出花费的时间
   • 直到满⾜ 5 个0 开头，打印出花费的时间
   • 实践⾮对称加密 RSA
   • 先⽣成⼀个公私钥对
   • ⽤私钥对符合POW⼀个昵称 + nonce 进⾏私钥签名
   • ⽤公钥验证
（pow_rsa_xunf.py的实现逻辑解释对应这个pow_rsa_xunf_steps.md说明）

二、练习作业（可选）
实践区块链原理（编程语言不限）满足以下需求，并能进行自动化测试验证结果：
1、工作量证明出块
2、交易打包进入区块
3、节点同步区块
实现代码blockchain.py 测试代码test_blockchain
