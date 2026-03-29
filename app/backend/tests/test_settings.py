import os
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.settings import get_cors_origins, get_responses_store_enabled


class SettingsTests(unittest.TestCase):
    def test_get_cors_origins_uses_default_for_empty_env(self) -> None:
        with patch.dict(os.environ, {"CORS_ORIGINS": ""}, clear=False):
            origins = get_cors_origins()

        self.assertIn("http://127.0.0.1:5173", origins)
        self.assertIn("http://localhost:5173", origins)

    def test_get_cors_origins_parses_csv(self) -> None:
        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": "https://a.example.com, https://b.example.com "},
            clear=False,
        ):
            origins = get_cors_origins()

        self.assertEqual(origins, ["https://a.example.com", "https://b.example.com"])

    def test_get_responses_store_enabled_defaults_true(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(get_responses_store_enabled())

    def test_get_responses_store_enabled_accepts_false_values(self) -> None:
        for value in ("false", "0", "off", "no"):
            with self.subTest(value=value):
                with patch.dict(os.environ, {"XINQUE_RESPONSES_STORE": value}, clear=False):
                    self.assertFalse(get_responses_store_enabled())


if __name__ == "__main__":
    unittest.main()
