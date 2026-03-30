import pathlib
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.trace_helpers import (
    build_phase_flow_report,
    build_session_analysis_payload,
    serialize_phase_timeline,
    serialize_trace_records,
)


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

    def test_serialize_phase_timeline_flattens_trace_timelines(self) -> None:
        payload = serialize_phase_timeline([
            SimpleNamespace(
                turn_number=1,
                created_at=datetime(2026, 3, 28, tzinfo=timezone.utc),
                llm_call={"phase_timeline": [{"phase": "working_context"}, {"phase": "final_answer"}]},
            ),
            SimpleNamespace(
                turn_number=2,
                created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
                llm_call={"phase_timeline": [{"phase": "tool_call"}]},
            ),
        ])

        self.assertEqual(payload["timeline"][0]["turn_number"], 1)
        self.assertEqual(payload["timeline"][0]["phases"], ["working_context", "final_answer"])
        self.assertEqual(payload["timeline"][1]["phases"], ["tool_call"])

    def test_build_session_analysis_payload_summarizes_focus_phases_and_changes(self) -> None:
        payload = build_session_analysis_payload(
            session_id="session-1",
            state_history=[
                SimpleNamespace(
                    version=2,
                    current_focus={"summary": "担心绩效反馈"},
                    change_reason="semantic_summary_changed",
                    created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
                ),
                SimpleNamespace(
                    version=1,
                    current_focus={"summary": "担心周会发言"},
                    change_reason="current_focus_changed",
                    created_at=datetime(2026, 3, 28, tzinfo=timezone.utc),
                ),
            ],
            traces=[
                SimpleNamespace(
                    turn_number=1,
                    llm_call={"phase_timeline": [{"phase": "working_context"}, {"phase": "final_answer"}]},
                ),
                SimpleNamespace(
                    turn_number=2,
                    llm_call={"phase_timeline": [{"phase": "tool_call"}, {"phase": "final_answer"}]},
                ),
            ],
        )

        self.assertEqual(payload["session_id"], "session-1")
        self.assertEqual(payload["analysis"]["current_focus_summary"], "担心绩效反馈")
        self.assertEqual(payload["analysis"]["latest_phases"], ["tool_call", "final_answer"])
        self.assertEqual(payload["analysis"]["phase_counts"]["final_answer"], 2)
        self.assertEqual(payload["analysis"]["key_state_changes"][0]["change_reason"], "semantic_summary_changed")

    def test_build_phase_flow_report_summarizes_sequence_and_transitions(self) -> None:
        payload = build_phase_flow_report([
            SimpleNamespace(
                turn_number=1,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p2_explorer"}]},
            ),
            SimpleNamespace(
                turn_number=2,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p3_recommender"}]},
            ),
            SimpleNamespace(
                turn_number=3,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p4_interventor"}]},
            ),
            SimpleNamespace(
                turn_number=4,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p1_listener"}]},
            ),
        ])

        self.assertEqual(payload["phase_sequence"], ["p2_explorer", "p3_recommender", "p4_interventor", "p1_listener"])
        self.assertEqual(payload["phase_counts"]["p2_explorer"], 1)
        self.assertEqual(
            payload["transition_pairs"],
            ["p2_explorer->p3_recommender", "p3_recommender->p4_interventor", "p4_interventor->p1_listener"],
        )
        self.assertEqual(payload["repeated_phase_runs"], [])

    def test_build_phase_flow_report_detects_stuck_regression_and_unfinished_p4(self) -> None:
        payload = build_phase_flow_report([
            SimpleNamespace(
                turn_number=1,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p2_explorer"}]},
            ),
            SimpleNamespace(
                turn_number=2,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p2_explorer"}]},
            ),
            SimpleNamespace(
                turn_number=3,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p3_recommender"}]},
            ),
            SimpleNamespace(
                turn_number=4,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p2_explorer"}]},
            ),
            SimpleNamespace(
                turn_number=5,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p4_interventor"}]},
            ),
        ])

        self.assertTrue(payload["anomalies"]["stuck_in_p2"])
        self.assertTrue(payload["anomalies"]["phase_regression"])
        self.assertTrue(payload["anomalies"]["unfinished_p4"])


if __name__ == "__main__":
    unittest.main()
