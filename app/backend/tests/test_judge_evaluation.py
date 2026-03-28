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
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps(payload, ensure_ascii=False))
                )
            ]
        )
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=AsyncMock(return_value=response))
            )
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


if __name__ == "__main__":
    unittest.main()
