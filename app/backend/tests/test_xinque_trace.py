import pathlib
import sys
import unittest
from contextlib import ExitStack
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda *_args, **_kwargs: {}))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent import xinque


class XinqueTraceTests(unittest.TestCase):
    def test_tool_failure_is_recorded_in_trace_collector(self) -> None:
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(name="formulate", arguments='{"primary_issue":"x"}'),
        )
        choice = SimpleNamespace(
            finish_reason="tool_calls",
            message=SimpleNamespace(
                tool_calls=[tool_call],
                model_dump=lambda: {"role": "assistant", "tool_calls": []},
            ),
        )
        response = SimpleNamespace(choices=[choice], usage=None)

        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=AsyncMock(return_value=response))
            )
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

    def test_chat_returns_llm_trace_metadata(self) -> None:
        final_choice = SimpleNamespace(
            finish_reason="stop",
            message=SimpleNamespace(content="你好"),
        )
        response = SimpleNamespace(
            choices=[final_choice],
            usage=SimpleNamespace(prompt_tokens=12, completion_tokens=8, total_tokens=20),
        )
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=AsyncMock(return_value=response))
            )
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
        self.assertEqual(result["llm_trace"]["prompt_tokens"], 12)
        self.assertEqual(result["llm_trace"]["completion_tokens"], 8)
        self.assertEqual(result["llm_trace"]["total_tokens"], 20)
        self.assertGreaterEqual(result["llm_trace"]["latency_ms"], 0)


if __name__ == "__main__":
    unittest.main()
