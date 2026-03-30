import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.session_context import build_layered_context, build_persisted_session_state


class SessionContextTests(unittest.TestCase):
    def test_build_layered_context_returns_explicit_layers(self) -> None:
        history = [
            {"role": "user", "content": "最近工作压力一直很大。"},
            {"role": "assistant", "content": "听起来你最近一直很绷。"},
            {"role": "user", "content": "每次周会前都会反复担心说错话。"},
            {"role": "assistant", "content": "周会像是一个明显触发点。"},
            {"role": "user", "content": "之前试过呼吸练习，能缓一点。"},
            {"role": "assistant", "content": "至少它能先帮你降一点身体唤醒。"},
        ]
        stable_state = {
            "profile_snapshot": {"nickname": "阿明", "risk_level": "low"},
            "runtime_time_context": {
                "current_time_iso": "2026-03-29T09:30:00+08:00",
                "current_date": "2026-03-29",
                "timezone": "Asia/Shanghai",
            },
            "formulation": {"readiness": "sufficient", "primary_issue": "周会焦虑"},
            "recent_intervention": {
                "skill_name": "breathing_478",
                "completed": True,
                "started_at_iso": "2026-03-28T20:00:00+08:00",
                "relative_time": "昨天",
            },
            "last_session_summary": "上次主要聊了周会焦虑和呼吸练习。",
        }

        context = build_layered_context(
            history=history,
            user_message="今天的新情况是我更担心明天的一对一沟通，不想一直重复讲周会。",
            stable_state=stable_state,
            keep_last=4,
        )

        self.assertIn("current_focus", context)
        self.assertIn("working_memory", context)
        self.assertIn("stable_state", context)
        self.assertIn("retrieval_context", context)
        self.assertIn("semantic_summary", context)
        self.assertEqual(context["stable_state"]["formulation"]["primary_issue"], "周会焦虑")
        self.assertEqual(context["working_memory"], history[-4:])
        self.assertEqual(context["current_focus"]["priority"], "current_turn")
        self.assertIn("一对一沟通", context["current_focus"]["summary"])
        self.assertEqual(context["stable_state"]["runtime_time_context"]["timezone"], "Asia/Shanghai")

    def test_build_layered_context_uses_semantic_summary_sections(self) -> None:
        history = [
            {"role": "user", "content": "最近工作压力大，特别怕周会发言。"},
            {"role": "assistant", "content": "周会像是高压场景。"},
            {"role": "user", "content": "我也会担心领导对我失望。"},
            {"role": "assistant", "content": "这像是自我怀疑被触发。"},
            {"role": "user", "content": "你之前带我做过呼吸练习。"},
            {"role": "assistant", "content": "那个练习是先稳定身体反应。"},
            {"role": "user", "content": "但我还没想好怎么面对下周汇报。"},
        ]

        context = build_layered_context(
            history=history,
            user_message="我现在更想聊下周汇报，不想只重复之前的周会内容。",
            stable_state={},
            keep_last=3,
        )

        summary = context["semantic_summary"]
        self.assertIn("primary_themes", summary)
        self.assertIn("active_concerns", summary)
        self.assertIn("attempted_methods", summary)
        self.assertIn("open_loops", summary)
        self.assertTrue(any("工作压力" in item or "周会" in item for item in summary["primary_themes"]))
        self.assertTrue(any("呼吸" in item for item in summary["attempted_methods"]))
        self.assertTrue(any("下周汇报" in item or "汇报" in item for item in summary["open_loops"]))

    def test_build_layered_context_prefers_persisted_summary_but_overrides_focus(self) -> None:
        persisted_state = {
            "current_focus": {"priority": "current_turn", "summary": "上轮主要担心周会"},
            "semantic_summary": {
                "primary_themes": ["工作压力"],
                "active_concerns": ["周会发言"],
                "attempted_methods": ["478呼吸练习"],
                "open_loops": ["如何面对领导反馈"],
            },
            "stable_state": {
                "formulation": {"primary_issue": "工作中的自我怀疑"},
            },
        }

        context = build_layered_context(
            history=[{"role": "user", "content": "我现在更担心明天的一对一反馈。"}],
            user_message="我现在更担心明天的一对一反馈。",
            stable_state={"formulation": {"readiness": "sufficient"}},
            persisted_state=persisted_state,
            keep_last=4,
        )

        self.assertEqual(context["current_focus"]["summary"], "我现在更担心明天的一对一反馈。")
        self.assertIn("工作压力", context["semantic_summary"]["primary_themes"])
        self.assertIn("478呼吸练习", context["semantic_summary"]["attempted_methods"])
        self.assertIn("如何面对领导反馈", context["semantic_summary"]["open_loops"])

    def test_rendered_context_message_includes_time_context(self) -> None:
        context = build_layered_context(
            history=[{"role": "user", "content": "我今天更担心明天的一对一反馈。"}],
            user_message="我今天更担心明天的一对一反馈。",
            stable_state={
                "runtime_time_context": {
                    "current_time_iso": "2026-03-29T09:30:00+08:00",
                    "current_date": "2026-03-29",
                    "timezone": "Asia/Shanghai",
                },
                "recent_intervention": {
                    "skill_name": "breathing_478",
                    "started_at_iso": "2026-03-28T20:00:00+08:00",
                    "relative_time": "昨天",
                },
            },
        )

        from app.session_context import render_layered_context_message

        message = render_layered_context_message(context)

        self.assertIn("当前时间", message)
        self.assertIn("Asia/Shanghai", message)
        self.assertIn("昨天", message)

    def test_persisted_session_state_keeps_active_skill(self) -> None:
        context = build_layered_context(
            history=[{"role": "user", "content": "我想继续刚才那个练习。"}],
            user_message="我想继续刚才那个练习。",
            stable_state={
                "active_skill": {
                    "skill_name": "positive_experience_consolidation",
                    "display_name": "积极体验巩固",
                },
            },
        )

        persisted = build_persisted_session_state(context)

        self.assertEqual(
            persisted["stable_state"]["active_skill"]["skill_name"],
            "positive_experience_consolidation",
        )

    def test_rendered_context_message_includes_active_skill(self) -> None:
        context = build_layered_context(
            history=[{"role": "user", "content": "我想继续刚才那个练习。"}],
            user_message="我想继续刚才那个练习。",
            stable_state={
                "active_skill": {
                    "skill_name": "positive_experience_consolidation",
                    "display_name": "积极体验巩固",
                },
            },
        )

        from app.session_context import render_layered_context_message

        message = render_layered_context_message(context)

        self.assertIn("active_skill=positive_experience_consolidation", message)

    def test_persisted_session_state_keeps_active_phase(self) -> None:
        context = build_layered_context(
            history=[{"role": "user", "content": "我继续说刚才那个问题。"}],
            user_message="我继续说刚才那个问题。",
            stable_state={
                "active_phase": "p2_explorer",
            },
        )

        persisted = build_persisted_session_state(context)

        self.assertEqual(persisted["stable_state"]["active_phase"], "p2_explorer")

    def test_rendered_context_message_includes_active_phase(self) -> None:
        context = build_layered_context(
            history=[{"role": "user", "content": "我继续说刚才那个问题。"}],
            user_message="我继续说刚才那个问题。",
            stable_state={
                "active_phase": "p3_recommender",
            },
        )

        from app.session_context import render_layered_context_message

        message = render_layered_context_message(context)

        self.assertIn("active_phase=p3_recommender", message)


if __name__ == "__main__":
    unittest.main()
