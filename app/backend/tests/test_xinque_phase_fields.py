import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda *_args, **_kwargs: {}))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent import xinque


class XinquePhaseFieldTests(unittest.TestCase):
    def test_chat_prefers_structured_phase_fields_from_output_parsed(self) -> None:
        response = SimpleNamespace(
            id="resp-1",
            output=[],
            output_parsed={
                "reply": "听起来你这两天一直在为周会发言绷着。我们先把最刺耳的那个担心说清楚，好吗？",
                "phase_fields": {
                    "intent": False,
                    "explore": True,
                    "asking": "thought",
                    "formulation_confirmed": False,
                    "needs_more_exploration": True,
                    "chosen_intervention": None,
                    "intervention_complete": False,
                },
            },
            usage=SimpleNamespace(input_tokens=5, output_tokens=7, total_tokens=12),
        )
        create = AsyncMock(return_value=response)
        client = SimpleNamespace(responses=SimpleNamespace(create=create))

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                return await xinque.chat(
                    client=client,
                    history=[],
                    user_message="我每次周会前都怕自己说错话",
                    user_id="user-1",
                    session_id="session-1",
                    db=AsyncMock(),
                    trace_collector=[],
                )

        result = __import__("asyncio").run(run_test())

        self.assertIn("周会发言", result["reply"])
        self.assertEqual(
            result["llm_trace"]["persisted_session_state"]["stable_state"]["active_phase"],
            "p2_explorer",
        )
        self.assertEqual(
            result["llm_trace"]["persisted_session_state"]["stable_state"]["asking"],
            "thought",
        )
        create_kwargs = create.await_args.kwargs
        self.assertEqual(create_kwargs["text"]["format"]["type"], "json_schema")
        self.assertEqual(create_kwargs["text"]["format"]["name"], "assistant_phase_turn")

    def test_multi_turn_phase_script_covers_p1_to_p2_to_p3_to_p4_to_p1(self) -> None:
        responses = [
            SimpleNamespace(
                id="resp-1",
                output=[],
                output_parsed={
                    "reply": "先说说这件事最让你绷住的瞬间是什么。",
                    "phase_fields": {
                        "intent": False,
                        "explore": True,
                        "asking": "situation",
                        "formulation_confirmed": False,
                        "needs_more_exploration": True,
                        "chosen_intervention": None,
                        "intervention_complete": False,
                    },
                },
                usage=SimpleNamespace(input_tokens=4, output_tokens=5, total_tokens=9),
            ),
            SimpleNamespace(
                id="resp-2",
                output=[],
                output_parsed={
                    "reply": "我先说个工作性理解：你像是在会前就开始预演失败结果。要不要试一个很短的稳定方法？",
                    "phase_fields": {
                        "intent": False,
                        "explore": True,
                        "asking": "formulation",
                        "formulation_confirmed": True,
                        "needs_more_exploration": False,
                        "chosen_intervention": None,
                        "intervention_complete": False,
                    },
                },
                usage=SimpleNamespace(input_tokens=4, output_tokens=6, total_tokens=10),
            ),
            SimpleNamespace(
                id="resp-3",
                output=[],
                output_parsed={
                    "reply": "可以，我们就先试 4-7-8 呼吸，不铺太多内容。",
                    "phase_fields": {
                        "intent": True,
                        "explore": False,
                        "asking": None,
                        "formulation_confirmed": True,
                        "needs_more_exploration": False,
                        "chosen_intervention": "breathing_478",
                        "intervention_complete": False,
                    },
                },
                usage=SimpleNamespace(input_tokens=5, output_tokens=6, total_tokens=11),
            ),
            SimpleNamespace(
                id="resp-4",
                output=[],
                output_parsed={
                    "reply": "这轮先到这里。你刚才已经把呼吸节奏跟上了，等会儿只要记得先慢下来就行。",
                    "phase_fields": {
                        "intent": False,
                        "explore": False,
                        "asking": None,
                        "formulation_confirmed": False,
                        "needs_more_exploration": False,
                        "chosen_intervention": None,
                        "intervention_complete": True,
                    },
                },
                usage=SimpleNamespace(input_tokens=5, output_tokens=6, total_tokens=11),
            ),
        ]
        create = AsyncMock(side_effect=responses)
        client = SimpleNamespace(responses=SimpleNamespace(create=create))
        persisted_state = None

        async def run_turn(user_message: str, prior_state):
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                return await xinque.chat(
                    client=client,
                    history=[],
                    user_message=user_message,
                    user_id="user-1",
                    session_id="session-1",
                    db=AsyncMock(),
                    trace_collector=[],
                    persisted_session_state=prior_state,
                )

        turn1 = __import__("asyncio").run(run_turn("我每次周会前都很紧张", persisted_state))
        turn2 = __import__("asyncio").run(run_turn("最怕大家看出我不稳", turn1["llm_trace"]["persisted_session_state"]))
        turn3 = __import__("asyncio").run(run_turn("可以，试一个短一点的方法", turn2["llm_trace"]["persisted_session_state"]))
        turn4 = __import__("asyncio").run(run_turn("我做完了，感觉胸口松一点", turn3["llm_trace"]["persisted_session_state"]))

        self.assertEqual(turn1["llm_trace"]["persisted_session_state"]["stable_state"]["active_phase"], "p2_explorer")
        self.assertEqual(turn2["llm_trace"]["persisted_session_state"]["stable_state"]["active_phase"], "p3_recommender")
        self.assertEqual(turn3["llm_trace"]["persisted_session_state"]["stable_state"]["active_phase"], "p4_interventor")
        self.assertEqual(turn4["llm_trace"]["persisted_session_state"]["stable_state"]["active_phase"], "p1_listener")


if __name__ == "__main__":
    unittest.main()
