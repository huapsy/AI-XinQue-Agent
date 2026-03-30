import os
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.settings import (
    get_cors_origins,
    get_encryption_key_version,
    get_otel_enabled,
    get_otel_exporter_endpoint,
    get_responses_store_enabled,
)


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

    def test_get_otel_enabled_defaults_false(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(get_otel_enabled())

    def test_get_otel_exporter_endpoint_reads_env(self) -> None:
        with patch.dict(os.environ, {"OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector:4318"}, clear=False):
            self.assertEqual(get_otel_exporter_endpoint(), "http://collector:4318")

    def test_get_encryption_key_version_defaults_v1(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_encryption_key_version(), "v1")

    def test_get_encryption_key_version_reads_env(self) -> None:
        with patch.dict(os.environ, {"XINQUE_ENCRYPTION_KEY_VERSION": "v3"}, clear=False):
            self.assertEqual(get_encryption_key_version(), "v3")


if __name__ == "__main__":
    unittest.main()
