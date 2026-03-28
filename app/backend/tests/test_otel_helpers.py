import json
import pathlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app import otel_helpers


class OTelHelperTests(unittest.TestCase):
    def test_export_trace_event_writes_jsonl_record(self) -> None:
        target = Path(__file__).resolve().parents[1] / "data" / "test-otel.jsonl"
        try:
            if target.exists():
                target.unlink()
            with patch.object(otel_helpers, "_OTEL_PATH", target):
                otel_helpers.export_trace_event("xinque.trace", {"session_id": "session-1"})

            lines = target.read_text(encoding="utf-8").strip().splitlines()
            payload = json.loads(lines[0])
            self.assertEqual(payload["name"], "xinque.trace")
            self.assertEqual(payload["attributes"]["session_id"], "session-1")
        finally:
            if target.exists():
                target.unlink()


if __name__ == "__main__":
    unittest.main()
