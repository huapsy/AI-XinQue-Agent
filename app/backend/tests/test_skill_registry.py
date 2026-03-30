import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.skill_registry import build_skill_registry, load_skill_registry


class SkillRegistryTests(unittest.TestCase):
    def test_build_skill_registry_indexes_skills_by_name(self) -> None:
        registry = build_skill_registry()

        self.assertIn("breathing_478", registry)
        self.assertIn("thought_record", registry)
        self.assertIn("positive_experience_consolidation", registry)
        self.assertEqual(registry["breathing_478"]["manifest"]["version"], "2.0")
        self.assertEqual(registry["thought_record"]["manifest"]["category"], "cbt")
        self.assertEqual(
            registry["positive_experience_consolidation"]["manifest"]["category"],
            "positive_psychology",
        )

    def test_load_skill_registry_returns_standardized_skill_entry(self) -> None:
        registry = load_skill_registry()
        entry = registry["body_scan"]

        self.assertIn("manifest", entry)
        self.assertIn("protocol", entry)
        self.assertIn("raw_text", entry)
        self.assertEqual(entry["manifest"]["card_template"], "guided_exercise")

    def test_positive_experience_consolidation_protocol_keeps_positive_path_constraints(self) -> None:
        registry = build_skill_registry()
        entry = registry["positive_experience_consolidation"]

        self.assertEqual(entry["manifest"]["output_type"], "dialogue")
        self.assertIn("每轮只推进一步", entry["protocol"])
        self.assertIn("不要把用户的开心过度解释成大道理", entry["protocol"])
        self.assertIn("不要把回复写成 1/2/3 选项菜单", entry["protocol"])
        self.assertIn("进入该 skill 后，优先按当前步骤推进", entry["protocol"])


if __name__ == "__main__":
    unittest.main()
