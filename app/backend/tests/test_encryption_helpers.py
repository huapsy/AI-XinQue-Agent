import base64
import hashlib
import os
import pathlib
import sys
import unittest

from cryptography.fernet import Fernet

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.encryption_helpers import decrypt_text, encrypt_text, is_encrypted


class EncryptionHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_key = os.environ.get("XINQUE_ENCRYPTION_KEY")
        self.original_key_version = os.environ.get("XINQUE_ENCRYPTION_KEY_VERSION")
        os.environ["XINQUE_ENCRYPTION_KEY"] = "unit-test-encryption-key"
        os.environ["XINQUE_ENCRYPTION_KEY_VERSION"] = "v7"

    def tearDown(self) -> None:
        if self.original_key is None:
            os.environ.pop("XINQUE_ENCRYPTION_KEY", None)
        else:
            os.environ["XINQUE_ENCRYPTION_KEY"] = self.original_key
        if self.original_key_version is None:
            os.environ.pop("XINQUE_ENCRYPTION_KEY_VERSION", None)
        else:
            os.environ["XINQUE_ENCRYPTION_KEY_VERSION"] = self.original_key_version

    @staticmethod
    def _build_legacy_cipher(value: str) -> str:
        digest = hashlib.sha256(b"unit-test-encryption-key").digest()
        key = base64.urlsafe_b64encode(digest)
        token = Fernet(key).encrypt(value.encode("utf-8")).decode("utf-8")
        return f"enc::{token}"

    def test_encrypt_and_decrypt_round_trip(self) -> None:
        cipher = encrypt_text("用户原文：我最近很焦虑。")

        self.assertTrue(is_encrypted(cipher))
        self.assertNotEqual(cipher, "用户原文：我最近很焦虑。")
        self.assertTrue(cipher.startswith("enc::v7::"))
        self.assertEqual(decrypt_text(cipher), "用户原文：我最近很焦虑。")

    def test_plain_text_is_left_untouched_by_decrypt(self) -> None:
        self.assertEqual(decrypt_text("plain text"), "plain text")

    def test_decrypt_supports_legacy_unversioned_cipher(self) -> None:
        legacy_cipher = self._build_legacy_cipher("历史密文")

        self.assertTrue(is_encrypted(legacy_cipher))
        self.assertEqual(decrypt_text(legacy_cipher), "历史密文")

    def test_encrypt_requires_configured_key(self) -> None:
        os.environ.pop("XINQUE_ENCRYPTION_KEY", None)

        with self.assertRaises(RuntimeError):
            encrypt_text("需要显式配置密钥")


if __name__ == "__main__":
    unittest.main()
