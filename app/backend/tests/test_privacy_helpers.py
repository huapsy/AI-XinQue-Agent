import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.privacy_helpers import redact_sensitive_text


class PrivacyHelperTests(unittest.TestCase):
    def test_redact_sensitive_text_masks_phone_email_and_uuid(self) -> None:
        text = (
            "联系我：13812345678，邮箱 foo@example.com，"
            "会话 550e8400-e29b-41d4-a716-446655440000。"
        )

        redacted = redact_sensitive_text(text, limit=200)

        self.assertNotIn("13812345678", redacted)
        self.assertNotIn("foo@example.com", redacted)
        self.assertNotIn("550e8400-e29b-41d4-a716-446655440000", redacted)
        self.assertIn("[phone]", redacted)
        self.assertIn("[email]", redacted)
        self.assertIn("[id]", redacted)

    def test_redact_sensitive_text_truncates_after_masking(self) -> None:
        text = "患者邮箱 test@example.com " + ("很长的文本" * 50)

        redacted = redact_sensitive_text(text, limit=80)

        self.assertLessEqual(len(redacted), 83)
        self.assertTrue(redacted.endswith("..."))


if __name__ == "__main__":
    unittest.main()
