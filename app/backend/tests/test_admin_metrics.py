import pathlib
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.admin_metrics_helpers import build_admin_metrics_payload


class AdminMetricsTests(unittest.TestCase):
    def test_build_admin_metrics_payload_aggregates_core_values(self) -> None:
        sessions = [
            SimpleNamespace(session_id="s1", started_at=datetime(2026, 3, 28, tzinfo=timezone.utc)),
            SimpleNamespace(session_id="s2", started_at=datetime(2026, 3, 28, tzinfo=timezone.utc)),
        ]
        interventions = [
            SimpleNamespace(completed=True),
            SimpleNamespace(completed=False),
        ]
        traces = [
            SimpleNamespace(llm_call={"tool_calls": [{"success": False}]}, input_safety={"triggered": True}, total_latency_ms=1200),
            SimpleNamespace(llm_call={"tool_calls": [{"success": True}]}, input_safety={"triggered": False}, total_latency_ms=800),
        ]
        messages = {"s1": 4, "s2": 8}

        payload = build_admin_metrics_payload(sessions, interventions, traces, messages)

        self.assertEqual(payload["session_count"], 2)
        self.assertEqual(payload["average_turns"], 3.0)
        self.assertEqual(payload["intervention_completion_rate"], 0.5)
        self.assertEqual(payload["safety_trigger_rate"], 0.5)
        self.assertEqual(payload["tool_failure_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
