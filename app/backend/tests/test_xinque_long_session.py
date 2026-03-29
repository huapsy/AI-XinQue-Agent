import pathlib
import sys
import unittest
from types import SimpleNamespace

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda *_args, **_kwargs: {}))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent import xinque
from app.session_context import build_layered_context


class XinqueLongSessionTests(unittest.TestCase):
    def test_compact_history_injects_summary_for_long_sessions(self) -> None:
        history = [
            {"role": "user", "content": "第一轮我提到最近工作压力很大。"},
            {"role": "assistant", "content": "你最近好像一直绷着。"},
            {"role": "user", "content": "后来又说到每次周会都紧张。"},
            {"role": "assistant", "content": "周会像是一个明显触发点。"},
            {"role": "user", "content": "我也提到和领导沟通会自我怀疑。"},
            {"role": "assistant", "content": "这和自我评价关系很大。"},
            {"role": "user", "content": "然后我们聊到呼吸练习。"},
            {"role": "assistant", "content": "那个练习是为了先降身体唤醒。"},
            {"role": "user", "content": "最近我又开始反复想周会的事。"},
            {"role": "assistant", "content": "看起来这个循环又出现了。"},
        ]

        context = build_layered_context(
            history=history,
            user_message="我今天更想聊明天和领导的一对一，不想一直绕在周会上。",
            stable_state={"formulation": {"readiness": "sufficient"}},
        )
        compacted = xinque._build_context_messages(context)

        self.assertLess(len(compacted), len(history))
        self.assertEqual(compacted[0]["role"], "assistant")
        self.assertIn("会话状态", compacted[0]["content"])
        self.assertIn("当前目标", compacted[0]["content"])
        self.assertIn("一对一", compacted[0]["content"])
        self.assertIn("呼吸练习", compacted[0]["content"])
        self.assertEqual(compacted[1:], history[-4:])

    def test_compact_history_keeps_short_sessions_unchanged(self) -> None:
        history = [
            {"role": "user", "content": "我今天有点累。"},
            {"role": "assistant", "content": "听起来你今天已经撑了很久。"},
        ]

        context = build_layered_context(
            history=history,
            user_message="我今天有点累。",
            stable_state={},
        )
        compacted = xinque._build_context_messages(context)

        self.assertEqual(compacted[0]["role"], "assistant")
        self.assertEqual(compacted[1:], history)


if __name__ == "__main__":
    unittest.main()
