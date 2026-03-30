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

    def test_working_contract_message_carries_phase_and_verification_rules(self) -> None:
        message = build_working_contract_message(alignment_score=15, turn_number=3)

        self.assertIn("phase", message)
        self.assertIn("commentary", message)
        self.assertIn("final answer", message)
        self.assertIn("输出前验证", message)
        self.assertIn("空结果或低置信度", message)
        self.assertIn("intent", message)
        self.assertIn("chosen_intervention", message)

    def test_working_contract_message_carries_minimal_persona_summary(self) -> None:
        message = build_working_contract_message(alignment_score=15, turn_number=3)

        self.assertIn("心雀", message)
        self.assertIn("心理支持助手", message)
        self.assertIn("专业、温和、自然", message)
        self.assertIn("不生硬、说教或教程化", message)

    def test_working_contract_message_carries_stage_and_reply_structure_rules(self) -> None:
        message = build_working_contract_message(alignment_score=15, turn_number=3)

        self.assertIn("P1 不做表单式分流", message)
        self.assertIn("P2 先探索和形成理解", message)
        self.assertIn("接住、正常化、缩小问题、一个具体问题", message)
        self.assertIn("默认每轮只问一个具体问题", message)

    def test_working_contract_message_carries_active_skill_lock_rule(self) -> None:
        message = build_working_contract_message(
            alignment_score=15,
            turn_number=4,
            active_skill={"skill_name": "positive_experience_consolidation"},
        )

        self.assertIn("当前 active skill=positive_experience_consolidation", message)
        self.assertIn("未完成前优先继续当前 skill", message)

    def test_working_contract_message_carries_active_phase_rule(self) -> None:
        message = build_working_contract_message(
            alignment_score=15,
            turn_number=4,
            active_phase="p3_recommender",
        )

        self.assertIn("当前 active phase=p3_recommender", message)
        self.assertIn("本轮优先遵守该阶段子Agent的行为边界", message)

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
