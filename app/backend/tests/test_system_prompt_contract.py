import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.system_prompt import build_system_prompt


class SystemPromptContractTests(unittest.TestCase):
    def test_build_system_prompt_includes_contract_sections(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=1)

        self.assertIn("## 持久人格", prompt)
        self.assertIn("## 输出契约", prompt)
        self.assertIn("## 工具契约", prompt)
        self.assertIn("## 完成契约", prompt)
        self.assertIn("## 验证契约", prompt)
        self.assertIn("## 长会话契约", prompt)
        self.assertIn("## 回合级写作控制", prompt)

    def test_first_turn_prompt_requires_context_recall(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=1)

        self.assertIn("首轮回合", prompt)
        self.assertIn("优先调用 recall_context", prompt)

    def test_later_turn_prompt_adds_long_session_guidance(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=7)

        self.assertIn("当前会话已经持续多轮", prompt)
        self.assertIn("优先复用已有总结", prompt)

    def test_prompt_mentions_recent_intervention_follow_up_priority(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("最近 48 小时内已有尚未收口的 intervention", prompt)
        self.assertIn("今天或昨天发生的事项优先 follow-up", prompt)

    def test_prompt_mentions_recent_memories_should_outrank_old_background(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("多个记忆都相关时", prompt)
        self.assertIn("更早的记忆默认作为背景", prompt)

    def test_prompt_clamps_default_bulleted_reply_style(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("默认不使用 bullet list、编号列表或小标题块", prompt)
        self.assertIn("只有内容天然属于步骤、资源、卡片、清单", prompt)

    def test_prompt_requires_hypothesis_language_for_psychological_understanding(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("工作性假设", prompt)
        self.assertIn("不要把总结、归因、机制判断写成确定事实", prompt)

    def test_prompt_prefers_short_low_load_supportive_replies(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("句子普遍要短，认知负担低", prompt)
        self.assertIn("普通支持性回复优先控制在 2-4 句内", prompt)

    def test_prompt_clamps_translationese_and_written_register(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("像中国人平时会说的话", prompt)
        self.assertIn("不要像翻译腔、配音腔、客服腔", prompt)
        self.assertIn("少用“此刻”“压迫感”“收口”“具体地说”这类书面或翻译味较重的词", prompt)

    def test_prompt_includes_colloquial_rewrite_examples(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("别说“听起来你现在被压力压得有点喘不过气”", prompt)
        self.assertIn("更像“这么多事一下压过来，谁都会慌”", prompt)
        self.assertIn("别把每一步都解释给用户听", prompt)

    def test_prompt_prefers_exploration_driven_negative_flow(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("默认不是建议驱动，而是探索驱动", prompt)
        self.assertIn("接住 -> 正常化 -> 缩小问题 -> 一个具体问题", prompt)
        self.assertIn("不要一上来给出 A/B/C 建议清单", prompt)

    def test_prompt_mentions_phase_discipline_for_long_running_responses(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("中间 commentary", prompt)
        self.assertIn("tool 过渡", prompt)
        self.assertIn("final answer", prompt)

    def test_prompt_mentions_empty_result_recovery_and_output_gate(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("空结果或低置信度结果", prompt)
        self.assertIn("输出前验证闸门", prompt)

    def test_prompt_upgrades_persona_to_support_assistant_with_rogers_style(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("心理支持助手", prompt)
        self.assertIn("罗杰斯的人本主义理念", prompt)
        self.assertIn("被理解、被承接、被安全地陪伴", prompt)
        self.assertIn("稳定和可信赖，优先于“显得聪明”", prompt)

    def test_prompt_makes_stage_discipline_explicit(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("P1 不要写成分类题、表单式分流或多选入口", prompt)
        self.assertIn("P2 未形成足够理解前，不要进入 P3 推荐与激发", prompt)
        self.assertIn("P4 只有在用户已接受并进入练习时才进入", prompt)

    def test_prompt_makes_four_step_reply_structure_explicit(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("接住 -> 正常化 -> 缩小问题 -> 一个具体问题", prompt)
        self.assertIn("默认每轮只问一个具体问题", prompt)
        self.assertIn("不要用分类选项、多入口并列问题或表单式分流替代这四步结构", prompt)

    def test_prompt_allows_positive_experience_consolidation_for_positive_sentiment(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("positive_experience_consolidation", prompt)
        self.assertIn("刚开始明确表达积极情绪或良好状态", prompt)
        self.assertIn("进入该 skill 后不要改写成菜单式分流", prompt)

    def test_prompt_includes_only_requested_phase_profile(self) -> None:
        prompt = build_system_prompt(
            alignment_score=15,
            turn_number=3,
            active_phase="p2_explorer",
        )

        self.assertIn("## 当前阶段子Agent", prompt)
        self.assertIn("P2 子Agent", prompt)
        self.assertNotIn("P3 子Agent", prompt)


if __name__ == "__main__":
    unittest.main()
