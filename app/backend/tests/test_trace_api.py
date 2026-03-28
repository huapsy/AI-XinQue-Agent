import pathlib
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.trace_helpers import serialize_trace_records


class TraceApiTests(unittest.TestCase):
    def test_get_session_traces_returns_ordered_trace_payloads(self) -> None:
        payload = serialize_trace_records([
            SimpleNamespace(
                trace_id="trace-1",
                turn_number=1,
                input_safety={"triggered": False},
                llm_call={"model": "gpt-5.4"},
                output_safety={"triggered": False},
                total_latency_ms=1000,
                created_at=datetime(2026, 3, 28, tzinfo=timezone.utc),
            ),
            SimpleNamespace(
                trace_id="trace-2",
                turn_number=2,
                input_safety={"triggered": True},
                llm_call={"skipped": True},
                output_safety={"triggered": False},
                total_latency_ms=10,
                created_at=datetime(2026, 3, 28, tzinfo=timezone.utc),
            ),
        ])

        self.assertEqual(payload["traces"][0]["trace_id"], "trace-1")
        self.assertEqual(payload["traces"][1]["turn_number"], 2)
        self.assertEqual(payload["traces"][1]["llm_call"]["skipped"], True)


if __name__ == "__main__":
    unittest.main()
