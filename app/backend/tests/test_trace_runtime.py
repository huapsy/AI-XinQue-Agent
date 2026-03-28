import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.tables import TraceRecord
from app.trace_helpers import create_trace_record, serialize_trace_records


class TraceRuntimeTests(unittest.TestCase):
    def test_create_trace_record_builds_model_instance(self) -> None:
        record = create_trace_record(
            trace_model=TraceRecord,
            session_id="session-1",
            turn_number=2,
            input_safety={"triggered": False},
            llm_call={"model": "gpt-5.4", "tool_calls": []},
            output_safety={"triggered": False},
            total_latency_ms=1234,
        )

        self.assertEqual(record.session_id, "session-1")
        self.assertEqual(record.turn_number, 2)
        self.assertEqual(record.llm_call["model"], "gpt-5.4")

    def test_serialize_trace_records_returns_payload(self) -> None:
        payload = serialize_trace_records([
            SimpleNamespace(
                trace_id="trace-1",
                turn_number=1,
                input_safety={"triggered": False},
                llm_call={"model": "gpt-5.4"},
                output_safety={"triggered": False},
                total_latency_ms=500,
                created_at=datetime(2026, 3, 28, tzinfo=timezone.utc),
            ),
        ])

        self.assertEqual(payload["traces"][0]["trace_id"], "trace-1")
        self.assertEqual(payload["traces"][0]["total_latency_ms"], 500)


if __name__ == "__main__":
    unittest.main()
