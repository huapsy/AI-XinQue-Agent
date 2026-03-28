import os
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.encryption_helpers import decrypt_text, encrypt_text, is_encrypted


class EncryptionHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_key = os.environ.get("XINQUE_ENCRYPTION_KEY")
        os.environ["XINQUE_ENCRYPTION_KEY"] = "unit-test-encryption-key"

    def tearDown(self) -> None:
        if self.original_key is None:
            os.environ.pop("XINQUE_ENCRYPTION_KEY", None)
        else:
            os.environ["XINQUE_ENCRYPTION_KEY"] = self.original_key

    def test_encrypt_and_decrypt_round_trip(self) -> None:
        cipher = encrypt_text("用户原文：我最近很焦虑。")

        self.assertTrue(is_encrypted(cipher))
        self.assertNotEqual(cipher, "用户原文：我最近很焦虑。")
        self.assertEqual(decrypt_text(cipher), "用户原文：我最近很焦虑。")

    def test_plain_text_is_left_untouched_by_decrypt(self) -> None:
        self.assertEqual(decrypt_text("plain text"), "plain text")

    def test_encrypt_requires_configured_key(self) -> None:
        os.environ.pop("XINQUE_ENCRYPTION_KEY", None)

        with self.assertRaises(RuntimeError):
            encrypt_text("需要显式配置密钥")


if __name__ == "__main__":
    unittest.main()
