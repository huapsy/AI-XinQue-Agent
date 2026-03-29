import pathlib
import sys
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools.match_intervention import _match_skills
from app.models.tables import CaseFormulation, Intervention


class MatchInterventionRankingTests(unittest.TestCase):
    def test_recent_same_skill_is_not_ranked_first_when_alternative_exists(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            cognitive_patterns=[{"type": "negative_filtering"}],
            emotional_state=[{"name": "低落"}],
        )
        skills = [
            {"name": "thought_record", "category": "cbt"},
            {"name": "cognitive_restructuring", "category": "cbt"},
        ]
        recent = Intervention(
            session_id="session-0",
            user_id="user-1",
            skill_name="thought_record",
            started_at=datetime.now(timezone.utc) - timedelta(hours=12),
            completed=True,
            user_feedback="helpful",
            key_insight="有点帮助",
            homework_completed=True,
        )

        with patch(
            "app.agent.tools.match_intervention.load_skill_registry",
            return_value={
                "thought_record": {"manifest": {"category": "cbt"}},
                "cognitive_restructuring": {"manifest": {"category": "cbt"}},
            },
        ):
            matched = _match_skills(
                formulation=formulation,
                profile=None,
                skills=skills,
                recent_interventions=[recent],
            )

        self.assertEqual(matched[0]["name"], "cognitive_restructuring")

    def test_cooldown_hours_from_manifest_controls_recent_penalty(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            emotional_state=[{"name": "焦虑"}],
        )
        skills = [
            {"name": "breathing_478", "category": "mindfulness", "cooldown_hours": 24},
            {"name": "body_scan", "category": "mindfulness", "cooldown_hours": 24},
        ]
        recent = Intervention(
            session_id="session-0",
            user_id="user-1",
            skill_name="breathing_478",
            started_at=datetime.now(timezone.utc) - timedelta(hours=20),
            completed=True,
            user_feedback="helpful",
            key_insight="有点帮助",
            homework_completed=True,
        )

        with patch(
            "app.agent.tools.match_intervention.load_skill_registry",
            return_value={
                "breathing_478": {"manifest": {"category": "mindfulness"}},
                "body_scan": {"manifest": {"category": "mindfulness"}},
            },
        ):
            matched = _match_skills(
                formulation=formulation,
                profile=None,
                skills=skills,
                recent_interventions=[recent],
            )

        self.assertEqual(matched[0]["name"], "body_scan")


if __name__ == "__main__":
    unittest.main()
