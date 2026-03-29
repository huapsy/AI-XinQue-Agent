import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from sqlalchemy.exc import ResourceClosedError

sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda *_args, **_kwargs: {}))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.tool_runtime import execute_tool_runtime_call, load_recent_interventions, preflight_tool_call


class ToolRuntimeTests(unittest.TestCase):
    def test_load_recent_interventions_does_not_close_result_before_collecting_rows(self) -> None:
        recent = SimpleNamespace(user_id="user-1", skill_name="breathing_478")
        result = SimpleNamespace(_closed=False)

        def scalar_one_or_none():
            result._closed = True
            return None

        def scalars():
            if result._closed:
                raise ResourceClosedError("This result object is closed.")
            return SimpleNamespace(all=lambda: [recent])

        result.scalar_one_or_none = scalar_one_or_none
        result.scalars = scalars
        db = AsyncMock()
        db.execute.return_value = result

        items = __import__("asyncio").run(load_recent_interventions(db, "user-1"))

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].skill_name, "breathing_478")

    def test_execute_tool_runtime_call_normalizes_payload_and_appends_state(self) -> None:
        tool_state: list[dict] = []
        tool_call = SimpleNamespace(
            name="match_intervention",
            arguments="{}",
            call_id="call-1",
        )

        async def fake_preflight(**_kwargs):
            return None

        async def fake_execute_tool(**_kwargs):
            return json.dumps({"plans": [{"skill_name": "breathing_478"}]}, ensure_ascii=False)

        envelope, pending_output, card_data = __import__("asyncio").run(
            execute_tool_runtime_call(
                tool_call,
                user_id="user-1",
                session_id="session-1",
                user_message="还有别的方法吗",
                db=AsyncMock(),
                tool_state=tool_state,
                execute_tool=fake_execute_tool,
                preflight_tool=fake_preflight,
                trace_collector=[],
            )
        )

        self.assertEqual(envelope["status"], "ok")
        self.assertEqual(envelope["tool"], "match_intervention")
        self.assertEqual(envelope["payload"]["plans"][0]["skill_name"], "breathing_478")
        self.assertIsNone(card_data)
        self.assertEqual(tool_state[0]["tool"], "match_intervention")
        self.assertEqual(tool_state[0]["call_id"], "call-1")
        self.assertEqual(tool_state[0]["payload"]["plans"][0]["skill_name"], "breathing_478")
        self.assertEqual(pending_output["type"], "function_call_output")
        self.assertEqual(pending_output["call_id"], "call-1")
        self.assertIn("\"status\": \"ok\"", pending_output["output"])

    def test_execute_tool_runtime_call_extracts_card_data_from_payload(self) -> None:
        tool_state: list[dict] = []
        tool_call = SimpleNamespace(
            name="render_card",
            arguments='{"card_type":"checklist","title":"t"}',
            id="fc-id-only",
        )

        async def fake_preflight(**_kwargs):
            return None

        async def fake_execute_tool(**_kwargs):
            return json.dumps({
                "status": "ok",
                "tool": "render_card",
                "card_data": {"type": "checklist", "title": "t"},
            }, ensure_ascii=False)

        envelope, pending_output, card_data = __import__("asyncio").run(
            execute_tool_runtime_call(
                tool_call,
                user_id="user-1",
                session_id="session-1",
                user_message="test",
                db=AsyncMock(),
                tool_state=tool_state,
                execute_tool=fake_execute_tool,
                preflight_tool=fake_preflight,
                trace_collector=[],
            )
        )

        self.assertEqual(envelope["status"], "ok")
        self.assertEqual(card_data["type"], "checklist")
        self.assertEqual(tool_state[0]["payload"]["card_data"]["title"], "t")
        self.assertEqual(pending_output["call_id"], "fc-id-only")

    def test_preflight_reads_unified_tool_state_for_same_turn_chain(self) -> None:
        tool_state = [
            {
                "tool": "match_intervention",
                "payload": {"plans": [{"skill_name": "breathing_478"}]},
                "status": "ok",
            },
            {
                "tool": "load_skill",
                "payload": {"skill_name": "breathing_478"},
                "status": "ok",
            },
        ]

        load_result = __import__("asyncio").run(
            preflight_tool_call(
                "load_skill",
                {"skill_name": "breathing_478"},
                user_id="user-1",
                session_id="session-1",
                user_message="那继续吧",
                db=AsyncMock(),
                tool_state=tool_state[:1],
            )
        )
        outcome_result = __import__("asyncio").run(
            preflight_tool_call(
                "record_outcome",
                {"skill_name": "breathing_478", "user_feedback": "helpful"},
                user_id="user-1",
                session_id="session-1",
                user_message="嗯",
                db=AsyncMock(),
                tool_state=tool_state,
            )
        )

        self.assertIsNone(load_result)
        self.assertIsNone(outcome_result)


if __name__ == "__main__":
    unittest.main()
