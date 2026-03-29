import pathlib
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.chat_service import load_previous_response_id, load_previous_session_state


class ResponseStateTests(unittest.TestCase):
    def test_load_previous_response_id_returns_last_recorded_response(self) -> None:
        record = SimpleNamespace(
            llm_call={"response_ids": ["resp-1", "resp-2"]},
            created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
            turn_number=2,
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: record))

        response_id = __import__("asyncio").run(load_previous_response_id(db, "session-1"))

        self.assertEqual(response_id, "resp-2")

    def test_load_previous_response_id_returns_none_when_missing(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: None))

        response_id = __import__("asyncio").run(load_previous_response_id(db, "session-1"))

        self.assertIsNone(response_id)

    def test_load_previous_session_state_returns_last_persisted_state(self) -> None:
        session_state = SimpleNamespace(
            current_focus={"summary": "独立状态焦点"},
            semantic_summary={"primary_themes": ["工作压力"]},
            stable_state={"formulation": {"primary_issue": "周会焦虑"}},
        )
        record = SimpleNamespace(
            llm_call={
                "response_ids": ["resp-1", "resp-2"],
                "persisted_session_state": {
                    "current_focus": {"summary": "旧焦点"},
                    "semantic_summary": {"primary_themes": ["工作压力"]},
                    "stable_state": {"formulation": {"primary_issue": "周会焦虑"}},
                },
            },
            created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
            turn_number=2,
        )
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: session_state),
            SimpleNamespace(scalar_one_or_none=lambda: record),
        ])

        state = __import__("asyncio").run(load_previous_session_state(db, "session-1"))

        self.assertEqual(state["current_focus"]["summary"], "独立状态焦点")
        self.assertEqual(state["semantic_summary"]["primary_themes"], ["工作压力"])
        self.assertEqual(state["stable_state"]["formulation"]["primary_issue"], "周会焦虑")

    def test_load_previous_session_state_falls_back_to_trace_when_model_missing(self) -> None:
        record = SimpleNamespace(
            llm_call={
                "persisted_session_state": {
                    "current_focus": {"summary": "trace焦点"},
                    "semantic_summary": {"primary_themes": ["trace主题"]},
                    "stable_state": {"formulation": {"primary_issue": "trace问题"}},
                },
            },
            created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
            turn_number=2,
        )
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: None),
            SimpleNamespace(scalar_one_or_none=lambda: record),
        ])

        state = __import__("asyncio").run(load_previous_session_state(db, "session-1"))

        self.assertEqual(state["current_focus"]["summary"], "trace焦点")


if __name__ == "__main__":
    unittest.main()
