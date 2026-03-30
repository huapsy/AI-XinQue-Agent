import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda *_args, **_kwargs: {}))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.phase_flow_evaluator import run_phase_flow_scenario


def _structured_response(reply: str, phase_fields: dict, response_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=response_id,
        output=[],
        output_parsed={
            "reply": reply,
            "phase_fields": phase_fields,
        },
        usage=SimpleNamespace(input_tokens=4, output_tokens=5, total_tokens=9),
    )


class PhaseFlowEvaluatorTests(unittest.TestCase):
    def test_phase_flow_evaluator_reports_pass_for_expected_sequence(self) -> None:
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=AsyncMock(
                    side_effect=[
                        _structured_response("先说说最明显的触发点。", {
                            "intent": False,
                            "explore": True,
                            "asking": "situation",
                            "formulation_confirmed": False,
                            "needs_more_exploration": True,
                            "chosen_intervention": None,
                            "intervention_complete": False,
                        }, "resp-1"),
                        _structured_response("我先说个工作性理解，要不要试个短方法？", {
                            "intent": False,
                            "explore": True,
                            "asking": "formulation",
                            "formulation_confirmed": True,
                            "needs_more_exploration": False,
                            "chosen_intervention": None,
                            "intervention_complete": False,
                        }, "resp-2"),
                        _structured_response("可以，我们就先试呼吸练习。", {
                            "intent": True,
                            "explore": False,
                            "asking": None,
                            "formulation_confirmed": True,
                            "needs_more_exploration": False,
                            "chosen_intervention": "breathing_478",
                            "intervention_complete": False,
                        }, "resp-3"),
                        _structured_response("这轮先到这里。", {
                            "intent": False,
                            "explore": False,
                            "asking": None,
                            "formulation_confirmed": False,
                            "needs_more_exploration": False,
                            "chosen_intervention": None,
                            "intervention_complete": True,
                        }, "resp-4"),
                    ]
                )
            )
        )
        db = AsyncMock()

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                return await run_phase_flow_scenario(
                    client=client,
                    db=db,
                    user_id="user-1",
                    session_id="session-1",
                    turns=[
                        {"user_message": "我每次周会前都很紧张", "expected_phase": "p2_explorer"},
                        {"user_message": "最怕大家看出我不稳", "expected_phase": "p3_recommender"},
                        {"user_message": "可以，试一个短一点的方法", "expected_phase": "p4_interventor"},
                        {"user_message": "我做完了，感觉胸口松一点", "expected_phase": "p1_listener"},
                    ],
                )

        report = __import__("asyncio").run(run_test())

        self.assertTrue(report["passed"])
        self.assertEqual(
            report["observed_phases"],
            ["p2_explorer", "p3_recommender", "p4_interventor", "p1_listener"],
        )
        self.assertEqual(report["mismatches"], [])

    def test_phase_flow_evaluator_reports_mismatch_when_sequence_drifts(self) -> None:
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=AsyncMock(
                    side_effect=[
                        _structured_response("先说说最明显的触发点。", {
                            "intent": False,
                            "explore": True,
                            "asking": "situation",
                            "formulation_confirmed": False,
                            "needs_more_exploration": True,
                            "chosen_intervention": None,
                            "intervention_complete": False,
                        }, "resp-1"),
                    ]
                )
            )
        )
        db = AsyncMock()

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                return await run_phase_flow_scenario(
                    client=client,
                    db=db,
                    user_id="user-1",
                    session_id="session-1",
                    turns=[
                        {"user_message": "我每次周会前都很紧张", "expected_phase": "p3_recommender"},
                    ],
                )

        report = __import__("asyncio").run(run_test())

        self.assertFalse(report["passed"])
        self.assertEqual(report["observed_phases"], ["p2_explorer"])
        self.assertEqual(report["expected_phases"], ["p3_recommender"])
        self.assertEqual(report["mismatches"][0]["turn"], 1)
        self.assertEqual(report["mismatches"][0]["expected_phase"], "p3_recommender")
        self.assertEqual(report["mismatches"][0]["observed_phase"], "p2_explorer")


if __name__ == "__main__":
    unittest.main()
