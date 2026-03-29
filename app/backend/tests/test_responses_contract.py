import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.responses_contract import (
    RUNTIME_LAYER_DEFINITIONS,
    build_working_contract_message,
    build_runtime_input,
    should_use_stateful_responses,
)


class ResponsesContractTests(unittest.TestCase):
    def test_should_use_stateful_responses_requires_store_and_previous_response_id(self) -> None:
        self.assertTrue(should_use_stateful_responses(True, "resp-1"))
        self.assertFalse(should_use_stateful_responses(False, "resp-1"))
        self.assertFalse(should_use_stateful_responses(True, None))

    def test_build_runtime_input_uses_runtime_layers_for_stateful_mode(self) -> None:
        effective_history = [{"role": "assistant", "content": "会话状态：当前目标=减轻压力"}]

        pending_input, active_previous_response_id = build_runtime_input(
            effective_history=effective_history,
            user_message="这周还是紧张",
            alignment_score=3,
            turn_number=3,
            previous_response_id="resp-prev",
            store_enabled=True,
        )

        self.assertEqual(active_previous_response_id, "resp-prev")
        self.assertEqual(pending_input[0]["phase"], "commentary")
        self.assertEqual(pending_input[1]["phase"], "commentary")
        self.assertEqual(pending_input[2]["role"], "user")

    def test_runtime_layer_definitions_cover_core_layers(self) -> None:
        self.assertIn("instructions", RUNTIME_LAYER_DEFINITIONS)
        self.assertIn("working_contract", RUNTIME_LAYER_DEFINITIONS)
        self.assertIn("working_context", RUNTIME_LAYER_DEFINITIONS)
        self.assertIn("previous_response_id", RUNTIME_LAYER_DEFINITIONS)
        self.assertIn("store", RUNTIME_LAYER_DEFINITIONS)

    def test_runtime_layer_definitions_explain_instructions_are_request_scoped(self) -> None:
        self.assertIn("不自动跨轮继承", RUNTIME_LAYER_DEFINITIONS["instructions"])
        self.assertIn("仅负责串接，不替代产品级 contract", RUNTIME_LAYER_DEFINITIONS["previous_response_id"])

    def test_working_contract_message_carries_prompt_style_rules_across_turns(self) -> None:
        message = build_working_contract_message(alignment_score=3, turn_number=3)

        self.assertIn("默认自然 prose，不使用列表、编号或文档腔", message)
        self.assertIn("默认探索驱动，而不是建议驱动", message)
        self.assertIn("工作性假设", message)
        self.assertIn("对齐状态较低", message)

    def test_stateless_runtime_input_drops_previous_response_id_dependency(self) -> None:
        effective_history = [{"role": "assistant", "content": "会话状态：当前目标=减轻压力"}]

        pending_input, active_previous_response_id = build_runtime_input(
            effective_history=effective_history,
            user_message="我还是想继续说说",
            alignment_score=15,
            turn_number=3,
            previous_response_id="resp-prev",
            store_enabled=False,
        )

        self.assertIsNone(active_previous_response_id)
        self.assertEqual(pending_input[-1]["role"], "user")
        self.assertEqual(pending_input[-1]["content"], "我还是想继续说说")


if __name__ == "__main__":
    unittest.main()
