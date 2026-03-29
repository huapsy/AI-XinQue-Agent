import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.evaluation_helpers import run_llm_judge


class JudgeEvaluationTests(unittest.TestCase):
    def test_run_llm_judge_returns_structured_scores(self) -> None:
        payload = {
            "empathy": 4,
            "safety": 5,
            "stage_appropriateness": 4,
            "intervention_quality": 3,
            "alignment_sensitivity": 4,
            "summary": "整体稳定，安全合规。",
        }
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="message",
                    role="assistant",
                    phase="final_answer",
                    content=[
                        SimpleNamespace(type="output_text", text=json.dumps(payload, ensure_ascii=False))
                    ],
                )
            ]
        )
        client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=response))
        )

        async def run_test():
            return await run_llm_judge(
                client=client,
                model="judge-model",
                session_id="session-1",
                messages=[
                    {"role": "user", "content": "我最近开会前总是很紧张。"},
                    {"role": "assistant", "content": "听起来你最近一直在绷着。"},
                ],
            )

        result = __import__("asyncio").run(run_test())

        self.assertEqual(result["session_id"], "session-1")
        self.assertEqual(result["scores"]["safety"], 5)
        self.assertEqual(result["scores"]["empathy"], 4)
        self.assertIn("整体稳定", result["summary"])
        create_kwargs = client.responses.create.await_args.kwargs
        self.assertIn("text", create_kwargs)
        self.assertEqual(create_kwargs["text"]["format"]["type"], "json_schema")
        self.assertEqual(create_kwargs["text"]["format"]["name"], "judge_result")

    def test_run_llm_judge_parses_fenced_json(self) -> None:
        payload = {
            "empathy": 5,
            "safety": 4,
            "stage_appropriateness": 4,
            "intervention_quality": 4,
            "alignment_sensitivity": 5,
            "summary": "总体表现稳定。",
        }
        fenced = f"```json\n{json.dumps(payload, ensure_ascii=False)}\n```"
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="message",
                    role="assistant",
                    phase="final_answer",
                    content=[SimpleNamespace(type="output_text", text=fenced)],
                )
            ]
        )
        client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=response))
        )

        async def run_test():
            return await run_llm_judge(
                client=client,
                model="judge-model",
                session_id="session-2",
                messages=[{"role": "user", "content": "我今天好一些。"}],
            )

        result = __import__("asyncio").run(run_test())

        self.assertEqual(result["scores"]["empathy"], 5)
        self.assertEqual(result["scores"]["alignment_sensitivity"], 5)

    def test_run_llm_judge_returns_structured_error_when_json_is_invalid(self) -> None:
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="message",
                    role="assistant",
                    phase="final_answer",
                    content=[SimpleNamespace(type="output_text", text="not-json")],
                )
            ]
        )
        client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=response))
        )

        async def run_test():
            return await run_llm_judge(
                client=client,
                model="judge-model",
                session_id="session-3",
                messages=[{"role": "user", "content": "我今天好一些。"}],
            )

        result = __import__("asyncio").run(run_test())

        self.assertEqual(result["scores"]["safety"], 0)
        self.assertEqual(result["error"]["type"], "judge_parse_error")

    def test_run_llm_judge_prefers_parsed_structured_output(self) -> None:
        payload = {
            "empathy": 3,
            "safety": 5,
            "stage_appropriateness": 3,
            "intervention_quality": 2,
            "alignment_sensitivity": 4,
            "summary": "已按 schema 返回。",
        }
        response = SimpleNamespace(output_parsed=payload, output=[])
        client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=response))
        )

        async def run_test():
            return await run_llm_judge(
                client=client,
                model="judge-model",
                session_id="session-4",
                messages=[{"role": "user", "content": "这两天总在担心绩效。"}],
            )

        result = __import__("asyncio").run(run_test())

        self.assertEqual(result["scores"]["safety"], 5)
        self.assertEqual(result["summary"], "已按 schema 返回。")


if __name__ == "__main__":
    unittest.main()
