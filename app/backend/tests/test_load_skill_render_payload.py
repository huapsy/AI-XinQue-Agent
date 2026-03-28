import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda text: {
    "name": "thought_record",
    "display_name": "想法记录",
    "category": "cbt",
    "output_type": "card",
    "card_template": "journal",
}))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import load_skill


class LoadSkillRenderPayloadTests(unittest.TestCase):
    def test_load_skill_returns_render_payload_for_journal_skill(self) -> None:
        skill_path = pathlib.Path(__file__).resolve().parents[2] / "skills" / "cbt" / "thought_record.skill.md"
        with patch("app.agent.tools.load_skill._find_skill_file", return_value=skill_path):
            raw = __import__("asyncio").run(load_skill.execute({"skill_name": "thought_record"}))
        payload = json.loads(raw)

        self.assertEqual(payload["skill_name"], "thought_record")
        self.assertEqual(payload["render_payload"]["card_type"], "journal")
        self.assertGreaterEqual(len(payload["render_payload"]["fields"]), 3)


if __name__ == "__main__":
    unittest.main()
