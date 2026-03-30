import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.evaluation_helpers import build_combined_evaluation_payload, run_llm_judge


class JudgeEvaluationTests(unittest.TestCase):
    def test_run_llm_judge_returns_structured_scores(self) -> None:
        payload = {
            "empathy": 4,
            "safety": 5,
            "stage_appropriateness": 4,
            "intervention_quality": 3,
            "alignment_sensitivity": 4,
            "prompt_review": {
                "premature_advice": 1,
                "format_heaviness": 0,
                "assumption_as_fact": 1,
                "tool_discipline": 4,
                "stage_discipline": 4,
                "reply_micro_structure": 5,
                "form_like_triage": 0,
                "translationese": 1,
            },
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
        self.assertEqual(result["prompt_review"]["premature_advice"], 1)
        self.assertEqual(result["prompt_review"]["tool_discipline"], 4)
        self.assertEqual(result["prompt_review"]["stage_discipline"], 4)
        self.assertEqual(result["prompt_review"]["reply_micro_structure"], 5)
        self.assertEqual(result["prompt_review"]["translationese"], 1)
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
            "prompt_review": {
                "premature_advice": 0,
                "format_heaviness": 1,
                "assumption_as_fact": 0,
                "tool_discipline": 5,
                "stage_discipline": 5,
                "reply_micro_structure": 4,
                "form_like_triage": 0,
                "translationese": 0,
            },
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
        self.assertEqual(result["prompt_review"]["format_heaviness"], 1)
        self.assertEqual(result["prompt_review"]["reply_micro_structure"], 4)
        self.assertEqual(result["prompt_review"]["translationese"], 0)

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
        self.assertEqual(result["prompt_review"]["tool_discipline"], 0)
        self.assertEqual(result["prompt_review"]["stage_discipline"], 0)
        self.assertEqual(result["prompt_review"]["translationese"], 0)

    def test_run_llm_judge_prefers_parsed_structured_output(self) -> None:
        payload = {
            "empathy": 3,
            "safety": 5,
            "stage_appropriateness": 3,
            "intervention_quality": 2,
            "alignment_sensitivity": 4,
            "prompt_review": {
                "premature_advice": 2,
                "format_heaviness": 1,
                "assumption_as_fact": 1,
                "tool_discipline": 3,
                "stage_discipline": 2,
                "reply_micro_structure": 1,
                "form_like_triage": 4,
                "translationese": 5,
            },
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
        self.assertEqual(result["prompt_review"]["assumption_as_fact"], 1)
        self.assertEqual(result["prompt_review"]["form_like_triage"], 4)
        self.assertEqual(result["prompt_review"]["translationese"], 5)

    def test_build_combined_evaluation_payload_merges_judge_and_phase_flow(self) -> None:
        payload = build_combined_evaluation_payload(
            judge_result={
                "session_id": "session-1",
                "scores": {
                    "empathy": 4,
                    "safety": 5,
                    "stage_appropriateness": 3,
                    "intervention_quality": 3,
                    "alignment_sensitivity": 4,
                },
                "prompt_review": {
                    "premature_advice": 1,
                    "format_heaviness": 0,
                    "assumption_as_fact": 1,
                    "tool_discipline": 4,
                    "stage_discipline": 3,
                    "reply_micro_structure": 4,
                    "form_like_triage": 0,
                    "translationese": 2,
                },
                "summary": "整体稳定。",
            },
            phase_flow_report={
                "phase_sequence": ["p2_explorer", "p3_recommender", "p2_explorer", "p4_interventor"],
                "phase_counts": {"p2_explorer": 2, "p3_recommender": 1, "p4_interventor": 1},
                "transition_pairs": ["p2_explorer->p3_recommender", "p3_recommender->p2_explorer", "p2_explorer->p4_interventor"],
                "repeated_phase_runs": [],
                "anomalies": {
                    "stuck_in_p2": False,
                    "phase_regression": True,
                    "unfinished_p4": True,
                },
            },
        )

        self.assertEqual(payload["session_id"], "session-1")
        self.assertEqual(payload["scores"]["safety"], 5)
        self.assertTrue(payload["phase_anomalies"]["phase_regression"])
        self.assertTrue(payload["phase_anomalies"]["unfinished_p4"])
        self.assertEqual(payload["prompt_review"]["translationese"], 2)
        self.assertIn("phase_regression", payload["risk_flags"])
        self.assertIn("unfinished_p4", payload["risk_flags"])


if __name__ == "__main__":
    unittest.main()
