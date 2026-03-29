import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.models.tables import SessionState, SessionStateHistory
from app.session_state_store import (
    load_session_state_history,
    load_session_state,
    save_session_state,
    should_create_state_history,
    save_session_state_with_history,
)


class SessionStateStoreTests(unittest.TestCase):
    def test_load_session_state_returns_dedicated_state_payload(self) -> None:
        record = SessionState(
            session_id="session-1",
            current_focus={"summary": "明天的一对一反馈"},
            semantic_summary={"primary_themes": ["工作压力"]},
            stable_state={"formulation": {"primary_issue": "自我怀疑"}},
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: record))

        payload = __import__("asyncio").run(load_session_state(db, "session-1"))

        self.assertEqual(payload["current_focus"]["summary"], "明天的一对一反馈")
        self.assertEqual(payload["semantic_summary"]["primary_themes"], ["工作压力"])
        self.assertEqual(payload["stable_state"]["formulation"]["primary_issue"], "自我怀疑")

    def test_save_session_state_updates_existing_record(self) -> None:
        existing = SessionState(
            session_id="session-1",
            current_focus={"summary": "旧焦点"},
            semantic_summary={"primary_themes": ["旧主题"]},
            stable_state={"formulation": {"primary_issue": "旧问题"}},
        )
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: existing))

        payload = {
            "current_focus": {"summary": "新焦点"},
            "semantic_summary": {"primary_themes": ["工作压力"]},
            "stable_state": {"formulation": {"primary_issue": "周会焦虑"}},
        }

        saved = __import__("asyncio").run(save_session_state(db, "session-1", payload))

        self.assertIs(saved, existing)
        self.assertEqual(existing.current_focus["summary"], "新焦点")
        self.assertEqual(existing.semantic_summary["primary_themes"], ["工作压力"])
        self.assertEqual(existing.stable_state["formulation"]["primary_issue"], "周会焦虑")
        db.add.assert_not_called()

    def test_should_create_state_history_returns_false_for_equivalent_payload(self) -> None:
        previous = {
            "current_focus": {"summary": "担心周会"},
            "semantic_summary": {
                "primary_themes": ["工作压力"],
                "open_loops": ["周会发言"],
            },
            "stable_state": {"formulation": {"primary_issue": "周会焦虑"}},
        }
        current = {
            "current_focus": {"summary": "担心周会"},
            "semantic_summary": {
                "primary_themes": ["工作压力"],
                "open_loops": ["周会发言"],
            },
            "stable_state": {"formulation": {"primary_issue": "周会焦虑"}},
        }

        should_create, reason, diff = should_create_state_history(previous, current)

        self.assertFalse(should_create)
        self.assertEqual(reason, "no_material_change")
        self.assertEqual(diff["added_themes"], [])

    def test_should_create_state_history_detects_new_theme(self) -> None:
        previous = {
            "current_focus": {"summary": "担心周会"},
            "semantic_summary": {
                "primary_themes": ["工作压力"],
                "open_loops": ["周会发言"],
            },
            "stable_state": {"formulation": {"primary_issue": "周会焦虑"}},
        }
        current = {
            "current_focus": {"summary": "开始担心绩效反馈"},
            "semantic_summary": {
                "primary_themes": ["工作压力", "绩效反馈"],
                "open_loops": ["绩效反馈", "周会发言"],
            },
            "stable_state": {"formulation": {"primary_issue": "绩效反馈引发的自我怀疑"}},
        }

        should_create, reason, diff = should_create_state_history(previous, current)

        self.assertTrue(should_create)
        self.assertEqual(reason, "semantic_summary_changed")
        self.assertIn("绩效反馈", diff["added_themes"])
        self.assertIn("工作压力", diff["retained_themes"])

    def test_save_session_state_with_history_creates_history_record_for_material_change(self) -> None:
        existing = SessionState(
            session_id="session-1",
            current_focus={"summary": "担心周会"},
            semantic_summary={"primary_themes": ["工作压力"], "open_loops": ["周会发言"]},
            stable_state={"formulation": {"primary_issue": "周会焦虑"}},
        )
        added_objects: list[object] = []
        db = AsyncMock()
        db.add = MagicMock(side_effect=added_objects.append)
        db.flush = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: existing),
            SimpleNamespace(scalar_one_or_none=lambda: existing),
            SimpleNamespace(scalar_one_or_none=lambda: None),
        ])

        payload = {
            "current_focus": {"summary": "开始担心绩效反馈"},
            "semantic_summary": {"primary_themes": ["工作压力", "绩效反馈"], "open_loops": ["绩效反馈"]},
            "stable_state": {"formulation": {"primary_issue": "绩效反馈引发的自我怀疑"}},
        }

        state, history = __import__("asyncio").run(save_session_state_with_history(db, "session-1", payload))

        self.assertIs(state, existing)
        self.assertIsInstance(history, SessionStateHistory)
        self.assertEqual(history.version, 1)
        self.assertEqual(history.change_reason, "semantic_summary_changed")
        self.assertIn("绩效反馈", history.change_summary["added_themes"])

    def test_save_session_state_with_history_skips_history_for_no_material_change(self) -> None:
        existing = SessionState(
            session_id="session-1",
            current_focus={"summary": "担心周会"},
            semantic_summary={"primary_themes": ["工作压力"], "open_loops": ["周会发言"]},
            stable_state={"formulation": {"primary_issue": "周会焦虑"}},
        )
        added_objects: list[object] = []
        db = AsyncMock()
        db.add = MagicMock(side_effect=added_objects.append)
        db.flush = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: existing),
            SimpleNamespace(scalar_one_or_none=lambda: existing),
        ])

        payload = {
            "current_focus": {"summary": "担心周会"},
            "semantic_summary": {"primary_themes": ["工作压力"], "open_loops": ["周会发言"]},
            "stable_state": {"formulation": {"primary_issue": "周会焦虑"}},
        }

        state, history = __import__("asyncio").run(save_session_state_with_history(db, "session-1", payload))

        self.assertIs(state, existing)
        self.assertIsNone(history)

    def test_load_session_state_history_returns_ordered_versions(self) -> None:
        history_items = [
            SessionStateHistory(
                session_id="session-1",
                version=2,
                current_focus={"summary": "担心绩效反馈"},
                semantic_summary={"primary_themes": ["绩效反馈"]},
                stable_state={"formulation": {"primary_issue": "绩效焦虑"}},
                change_reason="semantic_summary_changed",
                change_summary={"added_themes": ["绩效反馈"]},
            ),
            SessionStateHistory(
                session_id="session-1",
                version=1,
                current_focus={"summary": "担心周会"},
                semantic_summary={"primary_themes": ["工作压力"]},
                stable_state={"formulation": {"primary_issue": "周会焦虑"}},
                change_reason="current_focus_changed",
                change_summary={"focus_changed": True},
            ),
        ]
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: history_items)))

        payload = __import__("asyncio").run(load_session_state_history(db, "session-1"))

        self.assertEqual(payload["history"][0]["version"], 2)
        self.assertEqual(payload["history"][1]["version"], 1)
        self.assertEqual(payload["history"][0]["change_reason"], "semantic_summary_changed")


if __name__ == "__main__":
    unittest.main()
