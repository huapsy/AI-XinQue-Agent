import pathlib
import sys
import unittest
import json
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda *_args, **_kwargs: {}))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent import xinque
from app.models.tables import CaseFormulation


def _response_message(text: str, *, phase: str = "final_answer") -> SimpleNamespace:
    return SimpleNamespace(
        type="message",
        role="assistant",
        phase=phase,
        content=[SimpleNamespace(type="output_text", text=text)],
    )


def _response_function_call(name: str, arguments: str, *, call_id: str = "call-1") -> SimpleNamespace:
    return SimpleNamespace(
        type="function_call",
        id="fc-1",
        call_id=call_id,
        name=name,
        arguments=arguments,
        status="completed",
    )


def _response_function_call_with_id_only(name: str, arguments: str, *, response_id: str = "fc-1") -> SimpleNamespace:
    return SimpleNamespace(
        type="function_call",
        id=response_id,
        name=name,
        arguments=arguments,
        status="completed",
    )


class XinqueTraceTests(unittest.TestCase):
    def test_tool_failure_is_recorded_in_trace_collector(self) -> None:
        response = SimpleNamespace(
            id="resp-1",
            output=[_response_function_call("formulate", '{"primary_issue":"x"}')],
            usage=None,
        )
        client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=response))
        )
        trace_collector: list[dict] = []

        async def run_test():
            with ExitStack() as stack:
                stack.enter_context(patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False))
                stack.enter_context(patch("app.agent.xinque._execute_tool", side_effect=RuntimeError("boom")))
                with self.assertRaises(RuntimeError):
                    await xinque.chat(
                        client=client,
                        history=[],
                        user_message="test",
                        user_id="user-1",
                        session_id="session-1",
                        db=AsyncMock(),
                        trace_collector=trace_collector,
                    )

        __import__("asyncio").run(run_test())

        self.assertEqual(trace_collector[0]["tool"], "formulate")
        self.assertEqual(trace_collector[0]["success"], False)
        self.assertIn("boom", trace_collector[0]["result"])

    def test_chat_returns_llm_trace_metadata_and_phase(self) -> None:
        response = SimpleNamespace(
            id="resp-1",
            output=[_response_message("你好", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=12, output_tokens=8, total_tokens=20),
        )
        client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=response))
        )

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                return await xinque.chat(
                    client=client,
                    history=[],
                    user_message="test",
                    user_id="user-1",
                    session_id="session-1",
                    db=AsyncMock(),
                    trace_collector=[],
                )

        result = __import__("asyncio").run(run_test())

        self.assertEqual(result["reply"], "你好")
        self.assertEqual(result["llm_trace"]["model"], "test-deployment")
        self.assertEqual(result["llm_trace"]["endpoint"], "responses")
        self.assertEqual(result["llm_trace"]["prompt_tokens"], 12)
        self.assertEqual(result["llm_trace"]["completion_tokens"], 8)
        self.assertEqual(result["llm_trace"]["total_tokens"], 20)
        self.assertEqual(result["llm_trace"]["final_phase"], "final_answer")
        self.assertEqual(result["llm_trace"]["response_ids"], ["resp-1"])
        self.assertEqual(result["llm_trace"]["runtime_mode"], "stateless")
        self.assertIn("instructions", result["llm_trace"]["runtime_layers"])
        self.assertEqual(result["llm_trace"]["phase_timeline"][0]["phase"], "working_contract")
        self.assertEqual(result["llm_trace"]["phase_timeline"][1]["phase"], "working_context")
        self.assertEqual(result["llm_trace"]["phase_timeline"][-1]["phase"], "final_answer")
        self.assertIn("semantic_summary", result["llm_trace"]["persisted_session_state"])
        self.assertGreaterEqual(result["llm_trace"]["latency_ms"], 0)
        create_kwargs = client.responses.create.await_args.kwargs
        self.assertEqual(create_kwargs["tools"][0]["type"], "function")
        self.assertEqual(create_kwargs["tools"][0]["name"], "recall_context")
        self.assertNotIn("function", create_kwargs["tools"][0])

    def test_chat_replays_tool_output_with_previous_response_id(self) -> None:
        first = SimpleNamespace(
            id="resp-1",
            output=[_response_function_call("render_card", '{"card_type":"checklist","title":"t"}')],
            usage=None,
        )
        second = SimpleNamespace(
            id="resp-2",
            output=[_response_message("已为你整理成卡片。", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=4, output_tokens=6, total_tokens=10),
        )
        create = AsyncMock(side_effect=[first, second])
        client = SimpleNamespace(responses=SimpleNamespace(create=create))

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                with patch("app.agent.xinque._execute_tool", AsyncMock(return_value='{"card_data":{"type":"checklist","title":"t"}}')):
                    return await xinque.chat(
                        client=client,
                        history=[],
                        user_message="test",
                        user_id="user-1",
                        session_id="session-1",
                        db=AsyncMock(),
                        trace_collector=[],
                    )

        result = __import__("asyncio").run(run_test())

        self.assertEqual(result["reply"], "已为你整理成卡片。")
        self.assertEqual(result["card_data"]["type"], "checklist")
        first_kwargs = create.await_args_list[0].kwargs
        second_kwargs = create.await_args_list[1].kwargs
        self.assertNotIn("previous_response_id", first_kwargs)
        self.assertEqual(second_kwargs["previous_response_id"], "resp-1")
        self.assertEqual(second_kwargs["input"][0]["type"], "function_call_output")

    def test_chat_uses_previous_response_id_across_turns_without_replaying_history(self) -> None:
        response = SimpleNamespace(
            id="resp-2",
            output=[_response_message("继续说吧。", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=3, output_tokens=4, total_tokens=7),
        )
        create = AsyncMock(return_value=response)
        client = SimpleNamespace(responses=SimpleNamespace(create=create))
        history = [
            {"role": "user", "content": "上次我提到工作压力很大。"},
            {"role": "assistant", "content": "你那时一直很绷着。"},
        ]

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                return await xinque.chat(
                    client=client,
                    history=history,
                    user_message="这周周会又开始紧张了",
                    user_id="user-1",
                    session_id="session-1",
                    db=AsyncMock(),
                    trace_collector=[],
                    previous_response_id="resp-prev",
                )

        result = __import__("asyncio").run(run_test())

        self.assertEqual(result["reply"], "继续说吧。")
        kwargs = create.await_args.kwargs
        self.assertEqual(kwargs["previous_response_id"], "resp-prev")
        self.assertEqual(kwargs["input"][0]["role"], "assistant")
        self.assertEqual(kwargs["input"][0]["phase"], "commentary")
        self.assertIn("最小系统契约", kwargs["input"][0]["content"])
        self.assertEqual(kwargs["input"][1]["role"], "assistant")
        self.assertEqual(kwargs["input"][1]["phase"], "commentary")
        self.assertIn("当前目标", kwargs["input"][1]["content"])
        self.assertEqual(kwargs["input"][2], {"type": "message", "role": "user", "content": "这周周会又开始紧张了"})
        self.assertNotIn("instructions", kwargs)

    def test_chat_injects_alignment_warning_into_previous_response_path(self) -> None:
        response = SimpleNamespace(
            id="resp-2",
            output=[_response_message("先慢一点。", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=3, output_tokens=4, total_tokens=7),
        )
        create = AsyncMock(return_value=response)
        client = SimpleNamespace(responses=SimpleNamespace(create=create))

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                return await xinque.chat(
                    client=client,
                    history=[],
                    user_message="你根本没理解我",
                    user_id="user-1",
                    session_id="session-1",
                    db=AsyncMock(),
                    trace_collector=[],
                    previous_response_id="resp-prev",
                    alignment_score=3,
                )

        __import__("asyncio").run(run_test())
        kwargs = create.await_args.kwargs
        self.assertIn("对齐状态较低", kwargs["input"][0]["content"])

    def test_chat_supports_function_calls_with_id_only(self) -> None:
        first = SimpleNamespace(
            id="resp-1",
            output=[_response_function_call_with_id_only("render_card", '{"card_type":"checklist","title":"t"}', response_id="fc-only")],
            usage=None,
        )
        second = SimpleNamespace(
            id="resp-2",
            output=[_response_message("已为你整理成卡片。", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=4, output_tokens=6, total_tokens=10),
        )
        create = AsyncMock(side_effect=[first, second])
        client = SimpleNamespace(responses=SimpleNamespace(create=create))

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                with patch("app.agent.xinque._execute_tool", AsyncMock(return_value='{"card_data":{"type":"checklist","title":"t"}}')):
                    return await xinque.chat(
                        client=client,
                        history=[],
                        user_message="test",
                        user_id="user-1",
                        session_id="session-1",
                        db=AsyncMock(),
                        trace_collector=[],
                    )

        __import__("asyncio").run(run_test())
        second_kwargs = create.await_args_list[1].kwargs
        self.assertEqual(second_kwargs["input"][0]["call_id"], "fc-only")

    def test_chat_allows_match_then_load_in_same_turn_without_acceptance_keyword(self) -> None:
        first = SimpleNamespace(
            id="resp-1",
            output=[_response_function_call("match_intervention", "{}")],
            usage=None,
        )
        second = SimpleNamespace(
            id="resp-2",
            output=[_response_function_call("load_skill", '{"skill_name":"breathing_478"}')],
            usage=None,
        )
        third = SimpleNamespace(
            id="resp-3",
            output=[_response_message("我们来试试这个呼吸练习。", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=6, output_tokens=8, total_tokens=14),
        )
        create = AsyncMock(side_effect=[first, second, third])
        client = SimpleNamespace(responses=SimpleNamespace(create=create))

        async def fake_execute_tool(tool_name: str, arguments: str, *_args, **_kwargs):
            if tool_name == "match_intervention":
                return json.dumps({"plans": [{"skill_name": "breathing_478"}]}, ensure_ascii=False)
            if tool_name == "load_skill":
                return json.dumps({"skill_name": "breathing_478", "steps": []}, ensure_ascii=False)
            return "{}"

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                with patch("app.agent.xinque._execute_tool", side_effect=fake_execute_tool) as execute_mock:
                    db = AsyncMock()
                    db.execute = AsyncMock(return_value=SimpleNamespace(
                        scalar_one_or_none=lambda: CaseFormulation(
                            session_id="session-1",
                            user_id="user-1",
                            readiness="sufficient",
                            missing=[],
                        )
                    ))
                    result = await xinque.chat(
                        client=client,
                        history=[],
                        user_message="还有别的方法吗",
                        user_id="user-1",
                        session_id="session-1",
                        db=db,
                        trace_collector=[],
                    )
                    self.assertEqual(execute_mock.await_args_list[1].kwargs["tool_name"], "load_skill")
                    return result

        result = __import__("asyncio").run(run_test())
        self.assertIn("呼吸练习", result["reply"])

    def test_chat_trace_keeps_compatibility_copy_of_persisted_state(self) -> None:
        response = SimpleNamespace(
            id="resp-1",
            output=[_response_message("你好", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=2, output_tokens=3, total_tokens=5),
        )
        client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=response))
        )

        async def run_test():
            with patch.dict("os.environ", {"AZURE_OPENAI_DEPLOYMENT": "test-deployment"}, clear=False):
                return await xinque.chat(
                    client=client,
                    history=[],
                    user_message="test",
                    user_id="user-1",
                    session_id="session-1",
                    db=AsyncMock(),
                    trace_collector=[],
                )

        result = __import__("asyncio").run(run_test())

        self.assertIn("persisted_session_state", result["llm_trace"])
        self.assertIn("current_focus", result["llm_trace"]["persisted_session_state"])

    def test_chat_respects_store_environment_flag(self) -> None:
        response = SimpleNamespace(
            id="resp-1",
            output=[_response_message("你好", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=2, output_tokens=3, total_tokens=5),
        )
        create = AsyncMock(return_value=response)
        client = SimpleNamespace(responses=SimpleNamespace(create=create))

        async def run_test():
            with patch.dict(
                "os.environ",
                {
                    "AZURE_OPENAI_DEPLOYMENT": "test-deployment",
                    "XINQUE_RESPONSES_STORE": "false",
                },
                clear=False,
            ):
                return await xinque.chat(
                    client=client,
                    history=[],
                    user_message="test",
                    user_id="user-1",
                    session_id="session-1",
                    db=AsyncMock(),
                    trace_collector=[],
                )

        __import__("asyncio").run(run_test())
        kwargs = create.await_args.kwargs
        self.assertFalse(kwargs["store"])

    def test_chat_falls_back_to_stateless_mode_when_store_is_disabled(self) -> None:
        response = SimpleNamespace(
            id="resp-2",
            output=[_response_message("继续说吧。", phase="final_answer")],
            usage=SimpleNamespace(input_tokens=3, output_tokens=4, total_tokens=7),
        )
        create = AsyncMock(return_value=response)
        client = SimpleNamespace(responses=SimpleNamespace(create=create))
        history = [
            {"role": "user", "content": "上次我提到工作压力很大。"},
            {"role": "assistant", "content": "你那时一直很绷着。"},
        ]

        async def run_test():
            with patch.dict(
                "os.environ",
                {
                    "AZURE_OPENAI_DEPLOYMENT": "test-deployment",
                    "XINQUE_RESPONSES_STORE": "false",
                },
                clear=False,
            ):
                return await xinque.chat(
                    client=client,
                    history=history,
                    user_message="这周周会又开始紧张了",
                    user_id="user-1",
                    session_id="session-1",
                    db=AsyncMock(),
                    trace_collector=[],
                    previous_response_id="resp-prev",
                )

        result = __import__("asyncio").run(run_test())

        self.assertEqual(result["reply"], "继续说吧。")
        self.assertEqual(result["llm_trace"]["runtime_mode"], "stateless")
        kwargs = create.await_args.kwargs
        self.assertFalse(kwargs["store"])
        self.assertNotIn("previous_response_id", kwargs)
        self.assertIn("instructions", kwargs)
        self.assertGreater(len(kwargs["input"]), 2)


if __name__ == "__main__":
    unittest.main()
