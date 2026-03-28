import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.trace_helpers import build_tool_trace_entry, redact_trace_text


class TraceHelperTests(unittest.TestCase):
    def test_redact_trace_text_truncates_long_sensitive_content(self) -> None:
        text = "用户原文：" + ("很长的内容" * 40)
        redacted = redact_trace_text(text, limit=60)

        self.assertLessEqual(len(redacted), 63)
        self.assertTrue(redacted.endswith("..."))

    def test_build_tool_trace_entry_keeps_minimal_diagnostic_fields(self) -> None:
        entry = build_tool_trace_entry(
            tool_name="formulate",
            arguments='{"primary_issue":"工作压力"}',
            result='{"formulation":{"readiness":"sufficient"}}',
            success=True,
            latency_ms=123,
        )

        self.assertEqual(entry["tool"], "formulate")
        self.assertEqual(entry["success"], True)
        self.assertEqual(entry["latency_ms"], 123)
        self.assertIn("arguments", entry)
        self.assertIn("result", entry)

    def test_build_tool_trace_entry_can_mark_failure(self) -> None:
        entry = build_tool_trace_entry(
            tool_name="load_skill",
            arguments='{"skill_name":"breathing_478"}',
            result="RuntimeError: missing file",
            success=False,
            latency_ms=9,
        )

        self.assertEqual(entry["tool"], "load_skill")
        self.assertEqual(entry["success"], False)
        self.assertEqual(entry["latency_ms"], 9)


if __name__ == "__main__":
    unittest.main()
