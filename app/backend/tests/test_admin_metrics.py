import pathlib
import sys
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.admin_metrics_helpers import build_admin_metrics_payload
from app.main import get_admin_metrics


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

    def test_build_admin_metrics_payload_includes_combined_evaluation_summary(self) -> None:
        sessions = [
            SimpleNamespace(session_id="s1"),
            SimpleNamespace(session_id="s2"),
            SimpleNamespace(session_id="s3"),
        ]
        combined_evaluations = [
            SimpleNamespace(payload={
                "scores": {"safety": 5, "empathy": 4},
                "risk_flags": ["unfinished_p4"],
                "phase_anomalies": {"unfinished_p4": True, "phase_regression": False},
            }),
            SimpleNamespace(payload={
                "scores": {"safety": 3, "empathy": 2},
                "risk_flags": ["phase_regression"],
                "phase_anomalies": {"unfinished_p4": False, "phase_regression": True},
            }),
        ]

        payload = build_admin_metrics_payload(
            sessions=sessions,
            interventions=[],
            traces=[],
            message_counts={},
            combined_evaluations=combined_evaluations,
        )

        summary = payload["combined_evaluation_summary"]
        self.assertEqual(summary["evaluated_session_count"], 2)
        self.assertEqual(summary["coverage_rate"], 0.67)
        self.assertEqual(summary["sessions_with_risk_flags"], 2)
        self.assertEqual(summary["risk_flag_counts"]["unfinished_p4"], 1)
        self.assertEqual(summary["risk_flag_counts"]["phase_regression"], 1)
        self.assertEqual(summary["average_scores"]["safety"], 4.0)
        self.assertEqual(summary["average_scores"]["empathy"], 3.0)

    def test_get_admin_metrics_returns_combined_evaluation_summary(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [SimpleNamespace(session_id="s1")])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: ["s1", "s1"])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(session_id="s1", payload={
                    "scores": {"safety": 5},
                    "risk_flags": ["unfinished_p4"],
                    "phase_anomalies": {"unfinished_p4": True},
                }),
            ])),
        ])

        payload = __import__("asyncio").run(get_admin_metrics(db))

        self.assertEqual(payload["session_count"], 1)
        self.assertIn("combined_evaluation_summary", payload)
        self.assertEqual(payload["combined_evaluation_summary"]["evaluated_session_count"], 1)
        self.assertEqual(payload["combined_evaluation_summary"]["risk_flag_counts"]["unfinished_p4"], 1)

    def test_get_admin_metrics_supports_recent_sessions_filter(self) -> None:
        now = datetime(2026, 3, 30, tzinfo=timezone.utc)
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(session_id="s-new", started_at=now),
                SimpleNamespace(session_id="s-old", started_at=now - timedelta(days=3)),
            ])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(session_id="s-new", completed=True),
                SimpleNamespace(session_id="s-old", completed=False),
            ])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: ["s-new", "s-new", "s-old", "s-old"])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(session_id="s-new", payload={"scores": {"safety": 5}, "risk_flags": []}),
                SimpleNamespace(session_id="s-old", payload={"scores": {"safety": 1}, "risk_flags": ["phase_regression"]}),
            ])),
        ])

        payload = __import__("asyncio").run(get_admin_metrics(db, recent_sessions=1))

        self.assertEqual(payload["session_count"], 1)
        self.assertEqual(payload["average_turns"], 1.0)
        self.assertEqual(payload["combined_evaluation_summary"]["evaluated_session_count"], 1)
        self.assertEqual(payload["combined_evaluation_summary"]["average_scores"]["safety"], 5.0)
        self.assertEqual(payload["combined_evaluation_summary"]["risk_flag_counts"], {})

    def test_get_admin_metrics_supports_since_days_filter(self) -> None:
        now = datetime(2026, 3, 30, tzinfo=timezone.utc)
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(session_id="s-recent", started_at=now - timedelta(days=2)),
                SimpleNamespace(session_id="s-stale", started_at=now - timedelta(days=10)),
            ])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: ["s-recent", "s-recent", "s-stale", "s-stale"])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(session_id="s-recent", payload={"scores": {"empathy": 4}, "risk_flags": ["unfinished_p4"]}),
                SimpleNamespace(session_id="s-stale", payload={"scores": {"empathy": 1}, "risk_flags": ["phase_regression"]}),
            ])),
        ])

        payload = __import__("asyncio").run(get_admin_metrics(db, since_days=7, now=now))

        self.assertEqual(payload["session_count"], 1)
        self.assertEqual(payload["combined_evaluation_summary"]["evaluated_session_count"], 1)
        self.assertEqual(payload["combined_evaluation_summary"]["risk_flag_counts"]["unfinished_p4"], 1)
        self.assertNotIn("phase_regression", payload["combined_evaluation_summary"]["risk_flag_counts"])


if __name__ == "__main__":
    unittest.main()
