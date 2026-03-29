import pathlib
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.models.tables import Intervention
from app.time_freshness import select_primary_follow_up_intervention


class TimeFreshnessHelperTests(unittest.TestCase):
    def test_select_primary_follow_up_intervention_prefers_recent_unclosed(self) -> None:
        now = datetime.now(timezone.utc)
        older = Intervention(
            session_id="s-1",
            user_id="u-1",
            skill_name="thought_record",
            started_at=now - timedelta(days=5),
            completed=False,
            user_feedback=None,
            key_insight=None,
            homework_completed=False,
        )
        recent = Intervention(
            session_id="s-2",
            user_id="u-1",
            skill_name="breathing_478",
            started_at=now - timedelta(hours=20),
            completed=False,
            user_feedback=None,
            key_insight=None,
            homework_completed=False,
        )

        primary = select_primary_follow_up_intervention(
            [older, recent],
            user_message="我今天还是有点烦",
            now=now,
        )

        self.assertIsNotNone(primary)
        self.assertEqual(primary.skill_name, "breathing_478")

    def test_select_primary_follow_up_intervention_allows_reactivated_older_item(self) -> None:
        now = datetime.now(timezone.utc)
        recent_closed = Intervention(
            session_id="s-1",
            user_id="u-1",
            skill_name="breathing_478",
            started_at=now - timedelta(days=1),
            completed=True,
            user_feedback="helpful",
            key_insight="缓了一点",
            homework_completed=True,
        )
        older_open = Intervention(
            session_id="s-2",
            user_id="u-1",
            skill_name="thought_record",
            started_at=now - timedelta(days=6),
            completed=False,
            user_feedback=None,
            key_insight=None,
            homework_completed=False,
        )

        primary = select_primary_follow_up_intervention(
            [recent_closed, older_open],
            user_message="上次那个 thought_record 我还是卡住了",
            now=now,
        )

        self.assertIsNotNone(primary)
        self.assertEqual(primary.skill_name, "thought_record")

    def test_select_primary_follow_up_intervention_ignores_stale_background_items(self) -> None:
        now = datetime.now(timezone.utc)
        stale = Intervention(
            session_id="s-1",
            user_id="u-1",
            skill_name="gratitude_journal",
            started_at=now - timedelta(days=40),
            completed=False,
            user_feedback=None,
            key_insight=None,
            homework_completed=False,
        )

        primary = select_primary_follow_up_intervention(
            [stale],
            user_message="我今天上班还是很烦",
            now=now,
        )

        self.assertIsNone(primary)


if __name__ == "__main__":
    unittest.main()
