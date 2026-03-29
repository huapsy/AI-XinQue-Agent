import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.skill_manifest import SkillManifestError, validate_skill_manifest


class SkillManifestValidationTests(unittest.TestCase):
    def test_validate_skill_manifest_accepts_v2_manifest(self) -> None:
        manifest = validate_skill_manifest({
            "name": "breathing_478",
            "version": "2.0",
            "display_name": "4-7-8 呼吸法",
            "category": "mindfulness",
            "trigger": "用户焦虑、紧张，需要快速降唤醒",
            "output_type": "card",
            "card_template": "guided_exercise",
            "estimated_turns": "3-4",
            "contraindications": [{"risk_category": "crisis"}],
            "cooldown_hours": 48,
            "follow_up_rules": ["24小时内优先询问是否尝试、效果如何"],
            "completion_signals": ["我做完了", "刚试了", "感觉缓下来一点"],
        })

        self.assertEqual(manifest["version"], "2.0")
        self.assertEqual(manifest["cooldown_hours"], 48)
        self.assertEqual(manifest["card_template"], "guided_exercise")

    def test_validate_skill_manifest_rejects_missing_version(self) -> None:
        with self.assertRaises(SkillManifestError):
            validate_skill_manifest({
                "name": "breathing_478",
                "display_name": "4-7-8 呼吸法",
                "category": "mindfulness",
                "trigger": "用户焦虑、紧张，需要快速降唤醒",
                "output_type": "card",
                "estimated_turns": "3-4",
            })

    def test_validate_skill_manifest_rejects_invalid_card_template(self) -> None:
        with self.assertRaises(SkillManifestError):
            validate_skill_manifest({
                "name": "breathing_478",
                "version": "2.0",
                "display_name": "4-7-8 呼吸法",
                "category": "mindfulness",
                "trigger": "用户焦虑、紧张，需要快速降唤醒",
                "output_type": "card",
                "card_template": "unknown",
                "estimated_turns": "3-4",
                "cooldown_hours": 48,
                "follow_up_rules": [],
                "completion_signals": [],
            })


if __name__ == "__main__":
    unittest.main()
