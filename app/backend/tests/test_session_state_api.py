import pathlib
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.main import get_session_state, get_session_state_history, get_session_timeline


class SessionStateApiTests(unittest.TestCase):
    def test_get_session_state_returns_payload(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: SimpleNamespace(
            current_focus={"summary": "担心绩效反馈"},
            semantic_summary={"primary_themes": ["绩效反馈"]},
            stable_state={"formulation": {"primary_issue": "绩效焦虑"}},
            updated_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
        )))

        payload = __import__("asyncio").run(get_session_state("session-1", db))

        self.assertEqual(payload["state"]["current_focus"]["summary"], "担心绩效反馈")

    def test_get_session_state_history_returns_history(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            SimpleNamespace(
                version=2,
                current_focus={"summary": "担心绩效反馈"},
                semantic_summary={"primary_themes": ["绩效反馈"]},
                stable_state={"formulation": {"primary_issue": "绩效焦虑"}},
                change_reason="semantic_summary_changed",
                change_summary={"added_themes": ["绩效反馈"]},
                created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
            ),
        ])))

        payload = __import__("asyncio").run(get_session_state_history("session-1", db))

        self.assertEqual(payload["history"][0]["version"], 2)

    def test_get_session_timeline_returns_phase_timeline(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            SimpleNamespace(
                turn_number=1,
                created_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
                llm_call={"phase_timeline": [{"phase": "working_context"}, {"phase": "final_answer"}]},
            ),
        ])))

        payload = __import__("asyncio").run(get_session_timeline("session-1", db))

        self.assertEqual(payload["timeline"][0]["phases"], ["working_context", "final_answer"])


if __name__ == "__main__":
    unittest.main()
