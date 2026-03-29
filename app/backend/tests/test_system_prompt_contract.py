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

    def test_prompt_prefers_exploration_driven_negative_flow(self) -> None:
        prompt = build_system_prompt(alignment_score=15, turn_number=3)

        self.assertIn("默认不是建议驱动，而是探索驱动", prompt)
        self.assertIn("接住 -> 正常化 -> 缩小问题 -> 一个具体问题", prompt)
        self.assertIn("不要一上来给出 A/B/C 建议清单", prompt)


if __name__ == "__main__":
    unittest.main()
