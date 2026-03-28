import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.models.tables import TraceRecord
from app.trace_sink import DatabaseTraceSink


class TraceSinkTests(unittest.TestCase):
    def test_database_trace_sink_builds_trace_record(self) -> None:
        sink = DatabaseTraceSink(TraceRecord)

        record = sink.build_record(
            session_id="session-1",
            turn_number=3,
            input_safety={"triggered": False, "latency_ms": 1},
            llm_call={"model": "gpt-5.4", "tool_calls": []},
            output_safety={"triggered": False, "latency_ms": 2},
            total_latency_ms=30,
        )

        self.assertEqual(record.session_id, "session-1")
        self.assertEqual(record.turn_number, 3)
        self.assertEqual(record.total_latency_ms, 30)


if __name__ == "__main__":
    unittest.main()
