import pathlib
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.main import (
    get_session_combined_evaluation,
    get_session_analysis,
    get_session_phase_flow,
    get_session_state,
    get_session_state_history,
    get_session_timeline,
)


class SessionStateApiTests(unittest.TestCase):
    def test_get_session_state_returns_payload(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: SimpleNamespace(
            current_focus={"summary": "担心绩效反馈"},
            semantic_summary={"primary_themes": ["绩效反馈"]},
            stable_state={"formulation": {"primary_issue": "绩效焦虑"}},
            updated_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
        )))

        payload = __import__("asyncio").run(get_session_state("session-1", db))

        self.assertEqual(payload["state"]["current_focus"]["summary"], "担心绩效反馈")

    def test_get_session_state_history_returns_history(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            SimpleNamespace(
                version=2,
                current_focus={"summary": "担心绩效反馈"},
                semantic_summary={"primary_themes": ["绩效反馈"]},
                stable_state={"formulation": {"primary_issue": "绩效焦虑"}},
                change_reason="semantic_summary_changed",
                change_summary={"added_themes": ["绩效反馈"]},
                created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
            ),
        ])))

        payload = __import__("asyncio").run(get_session_state_history("session-1", db))

        self.assertEqual(payload["history"][0]["version"], 2)

    def test_get_session_state_history_supports_filters_and_meta(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            SimpleNamespace(
                version=2,
                current_focus={"summary": "担心绩效反馈"},
                semantic_summary={"primary_themes": ["绩效反馈"]},
                stable_state={"formulation": {"primary_issue": "绩效焦虑"}},
                change_reason="semantic_summary_changed",
                change_summary={"added_themes": ["绩效反馈"]},
                created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
            ),
        ])))

        payload = __import__("asyncio").run(
            get_session_state_history(
                "session-1",
                db,
                limit=1,
                before_version=3,
                change_reason="semantic_summary_changed",
            )
        )

        self.assertEqual(payload["history"][0]["version"], 2)
        self.assertEqual(payload["meta"]["limit"], 1)
        self.assertEqual(payload["meta"]["returned"], 1)
        self.assertFalse(payload["meta"]["has_more"])
        self.assertIsNone(payload["meta"]["next_before_version"])
        statement = db.execute.await_args.args[0]
        compiled = str(statement)
        self.assertIn("session_state_history.version < ", compiled)
        self.assertIn("session_state_history.change_reason = ", compiled)

    def test_get_session_timeline_returns_phase_timeline(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            SimpleNamespace(
                turn_number=1,
                created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
                llm_call={"phase_timeline": [{"phase": "working_context"}, {"phase": "final_answer"}]},
            ),
        ])))

        payload = __import__("asyncio").run(get_session_timeline("session-1", db))

        self.assertEqual(payload["timeline"][0]["phases"], ["working_context", "final_answer"])

    def test_get_session_timeline_supports_filters_and_meta(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            SimpleNamespace(
                turn_number=2,
                created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
                llm_call={"phase_timeline": [{"phase": "tool_call"}, {"phase": "final_answer"}]},
            ),
        ])))

        payload = __import__("asyncio").run(
            get_session_timeline(
                "session-1",
                db,
                limit=1,
                before_turn=3,
                phase="tool_call",
            )
        )

        self.assertEqual(payload["timeline"][0]["turn_number"], 2)
        self.assertEqual(payload["timeline"][0]["phases"], ["tool_call", "final_answer"])
        self.assertEqual(payload["meta"]["limit"], 1)
        self.assertEqual(payload["meta"]["returned"], 1)
        self.assertEqual(payload["meta"]["phase"], "tool_call")
        self.assertFalse(payload["meta"]["has_more"])
        self.assertIsNone(payload["meta"]["next_before_turn"])

    def test_get_session_analysis_returns_aggregated_payload(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(
                    version=2,
                    current_focus={"summary": "担心绩效反馈"},
                    semantic_summary={"primary_themes": ["绩效反馈"]},
                    stable_state={"formulation": {"primary_issue": "绩效焦虑"}},
                    change_reason="semantic_summary_changed",
                    change_summary={"added_themes": ["绩效反馈"]},
                    created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
                ),
            ])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(
                    turn_number=2,
                    llm_call={"phase_timeline": [{"phase": "tool_call"}, {"phase": "final_answer"}]},
                ),
            ])),
        ])

        payload = __import__("asyncio").run(get_session_analysis("session-1", db))

        self.assertEqual(payload["session_id"], "session-1")
        self.assertEqual(payload["analysis"]["current_focus_summary"], "担心绩效反馈")
        self.assertEqual(payload["analysis"]["phase_counts"]["tool_call"], 1)
        self.assertEqual(payload["analysis"]["key_state_changes"][0]["change_reason"], "semantic_summary_changed")
        self.assertIn("phase_flow", payload["analysis"])
        self.assertIn("phase_anomalies", payload["analysis"])

    def test_get_session_phase_flow_returns_report(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            SimpleNamespace(
                turn_number=1,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p2_explorer"}]},
            ),
            SimpleNamespace(
                turn_number=2,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p3_recommender"}]},
            ),
        ])))

        payload = __import__("asyncio").run(get_session_phase_flow("session-1", db))

        self.assertEqual(payload["session_id"], "session-1")
        self.assertEqual(payload["phase_flow"]["phase_sequence"], ["p2_explorer", "p3_recommender"])
        self.assertEqual(payload["phase_flow"]["transition_pairs"], ["p2_explorer->p3_recommender"])

    def test_get_session_combined_evaluation_returns_phase_risk_payload(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
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
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p4_interventor"}]},
            ),
        ])))

        async def run_test():
            with patch("app.main.load_history_messages", AsyncMock(return_value=[])):
                with patch("app.main.run_llm_judge", AsyncMock(return_value={
                    "session_id": "session-1",
                    "scores": {},
                    "prompt_review": {},
                    "summary": "",
                })):
                    with patch("app.main.save_combined_evaluation", AsyncMock()):
                        with patch("app.main.client", SimpleNamespace()):
                            return await get_session_combined_evaluation("session-1", db)

        payload = __import__("asyncio").run(run_test())

        self.assertEqual(payload["session_id"], "session-1")
        self.assertIn("phase_flow", payload)
        self.assertIn("phase_anomalies", payload)
        self.assertIn("risk_flags", payload)
        self.assertTrue(payload["phase_anomalies"]["stuck_in_p2"])
        self.assertTrue(payload["phase_anomalies"]["unfinished_p4"])
        self.assertIn("stuck_in_p2", payload["risk_flags"])

    def test_get_session_combined_evaluation_includes_real_judge_result(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            SimpleNamespace(
                turn_number=1,
                llm_call={"phase_timeline": [{"phase": "phase_routing", "active_phase": "p2_explorer"}]},
            ),
        ])))

        async def run_test():
            with patch("app.main.load_history_messages", AsyncMock(return_value=[
                {"role": "user", "content": "我最近总在担心绩效反馈。"},
                {"role": "assistant", "content": "听起来你最近一直很绷。"},
            ])):
                with patch("app.main.run_llm_judge", AsyncMock(return_value={
                    "session_id": "session-1",
                    "scores": {"safety": 5, "empathy": 4},
                    "prompt_review": {"stage_discipline": 4},
                    "summary": "整体稳定。",
                })) as judge_mock:
                    with patch("app.main.save_combined_evaluation", AsyncMock()) as save_mock:
                        with patch("app.main.client", SimpleNamespace()):
                            payload = await get_session_combined_evaluation("session-1", db)
                            self.assertTrue(save_mock.await_count >= 1)
                            return payload

        payload = __import__("asyncio").run(run_test())

        self.assertEqual(payload["scores"]["safety"], 5)
        self.assertEqual(payload["summary"], "整体稳定。")
        self.assertEqual(payload["prompt_review"]["stage_discipline"], 4)
        self.assertIn("phase_flow", payload)


if __name__ == "__main__":
    unittest.main()
