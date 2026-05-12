import os
import tempfile
import unittest

from pow_rsa_xunf import (
    pow_calculate,
    generate_rsa_key_pair,
    export_private_key_encrypted,
    export_public_key,
    rsa_sign,
    rsa_verify,
)


class TestPowRsaXunf(unittest.TestCase):
    def test_pow_calculate_low_difficulty(self):
        nonce, hash_hex, elapsed = pow_calculate("unittest", target_leading_zeros=1, max_nonce=10000)
        self.assertIsNotNone(nonce)
        self.assertIsInstance(hash_hex, str)
        self.assertGreaterEqual(len(hash_hex), 1)
        self.assertTrue(hash_hex.startswith("0"))
        self.assertGreaterEqual(elapsed, 0.0)

    def test_pow_calculate_timeout(self):
        nonce, hash_hex, elapsed = pow_calculate("unittest", target_leading_zeros=64, timeout=0.001)
        self.assertIsNone(nonce)
        self.assertIsInstance(hash_hex, str)
        self.assertGreaterEqual(elapsed, 0.0)

    def test_rsa_sign_and_verify(self):
        private_key, public_key = generate_rsa_key_pair(key_size=1024)
        message = "hello pow rsa"
        signature = rsa_sign(private_key, message)
        self.assertTrue(rsa_verify(public_key, message.encode("utf-8"), signature))
        self.assertFalse(rsa_verify(public_key, b"bad message", signature))

    def test_export_keys_to_temp_files(self):
        private_key, public_key = generate_rsa_key_pair(key_size=1024)
        with tempfile.TemporaryDirectory() as tmpdir:
            priv_path = os.path.join(tmpdir, "private_key.pem")
            pub_path = os.path.join(tmpdir, "public_key.pem")
            export_private_key_encrypted(private_key, password="testpass", filename=priv_path)
            export_public_key(public_key, filename=pub_path)

            self.assertTrue(os.path.exists(priv_path))
            self.assertTrue(os.path.exists(pub_path))

            with open(priv_path, "rb") as priv_file:
                priv_data = priv_file.read()
            with open(pub_path, "rb") as pub_file:
                pub_data = pub_file.read()

            self.assertIn(b"BEGIN ENCRYPTED PRIVATE KEY", priv_data)
            self.assertIn(b"BEGIN PUBLIC KEY", pub_data)


if __name__ == "__main__":
    unittest.main()
