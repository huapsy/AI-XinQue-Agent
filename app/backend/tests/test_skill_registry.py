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
        self.assertEqual(registry["breathing_478"]["manifest"]["version"], "2.0")
        self.assertEqual(registry["thought_record"]["manifest"]["category"], "cbt")

    def test_load_skill_registry_returns_standardized_skill_entry(self) -> None:
        registry = load_skill_registry()
        entry = registry["body_scan"]

        self.assertIn("manifest", entry)
        self.assertIn("protocol", entry)
        self.assertIn("raw_text", entry)
        self.assertEqual(entry["manifest"]["card_template"], "guided_exercise")


if __name__ == "__main__":
    unittest.main()
