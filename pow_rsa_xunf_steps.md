# `pow_rsa_xunf.py` 代码逻辑实现步骤

## 1. PoW 工作量证明部分

1. 导入 `hashlib`、`time`、`logging` 等模块。
2. 定义函数 `pow_calculate(nickname, target_leading_zeros, max_nonce=None, timeout=None, progress_interval=100000)`。
3. 记录起始时间 `start_time`，并初始化 `nonce = 0`。
4. 进入循环，直到找到满足前导零数量的哈希，或触发超时/最大 nonce 限制：
   - 使用 `f"{nickname}#{nonce}"` 拼接输入字符串。
   - 计算输入字符串的 SHA256 哈希并转换为十六进制字符串。
   - 统计哈希字符串前导零的数量。
   - 如果前导零数量达到 `target_leading_zeros`，则记录结束时间，返回 `nonce`、`hash_hex` 和耗时。
5. 在每次迭代后判断：
   - `max_nonce` 是否达到，如果是则提前返回失败状态；
   - `timeout` 是否超过，如果是则提前返回失败状态。
6. 可选地，每隔 `progress_interval` 次迭代，记录调试日志用于观察进度。

## 2. RSA 非对称加密部分

1. 导入 `cryptography.hazmat.primitives` 内的 RSA、填充、哈希和序列化相关模块。
2. 定义 `generate_rsa_key_pair(key_size=2048)`：
   - 调用 `rsa.generate_private_key(public_exponent=65537, key_size=key_size)` 生成私钥。
   - 从私钥获取公钥。
   - 返回 `(private_key, public_key)`。
3. 定义 `export_private_key_encrypted(private_key, password, filename="private_key.pem")`：
   - 要求密码非空，否则抛出 `ValueError`。
   - 将私钥以 `PKCS8` 格式和 `BestAvailableEncryption` 进行加密。
   - 写入 PEM 文件并返回文件路径。
4. 定义 `export_public_key(public_key, filename="public_key.pem")`：
   - 将公钥序列化为 PEM 格式并写入文件。
   - 返回文件路径。
5. 定义 `rsa_sign(private_key, data)`：
   - 将原始字符串编码为 UTF-8 字节。
   - 使用 `PSS` 填充和 `SHA256` 对数据进行签名。
   - 返回签名字节。
6. 定义 `rsa_verify(public_key, data, signature)`：
   - 使用公钥验证签名，若验证通过返回 `True`。
   - 若签名无效捕获 `InvalidSignature`，返回 `False`。

## 3. 主程序执行流程

1. 在 `main()` 中定义 `YOUR_NICKNAME = "jim123"`。
2. 打印任务开始状态。
3. 执行两次 PoW：
   - 第一次目标 4 个前导零；
   - 第二次目标 5 个前导零。
4. 生成 RSA 密钥对。
5. 取第一个 PoW 的结果字符串 `f"{YOUR_NICKNAME}#{nonce_4}"` 作为待签名数据。
6. 使用私钥签名该字符串，并输出签名结果的十六进制前缀。
7. 使用公钥验证签名：
   - 若验证成功，输出成功提示；
   - 否则输出失败提示。
8. 测试伪造数据验证：
   - 对 `f"{YOUR_NICKNAME}#{nonce_4 + 1}"` 验证相同签名；
   - 若验证失败，则说明签名机制安全。
9. 解析命令行参数：
   - `--export`：用于导出加密私钥；
   - `--export-path`：指定导出目录；
   - `--debug`：启用调试日志。
10. 根据参数或环境变量 `POW_RSA_EXPORT_PW` 导出私钥与公钥。

## 4. 注意事项

- `main()` 中 `logging.basicConfig()` 在 PoW 执行之后设置，导致 PoW 阶段的日志可能无法输出，建议将日志配置提前。
- `pow_calculate()` 支持 `max_nonce` 和 `timeout`，适合用于控制高难度 PoW 的运行时间。
- RSA 签名部分使用的是推荐的 `PSS` 填充方式，符合当前安全最佳实践。
