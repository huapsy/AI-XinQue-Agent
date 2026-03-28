import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import render_card


class RenderCardToolTests(unittest.TestCase):
    def test_render_card_normalizes_journal_card(self) -> None:
        raw = __import__("asyncio").run(render_card.execute({
            "card_type": "journal",
            "title": "想法记录",
            "description": "记录情境、想法和情绪",
            "fields": ["触发情境", "自动思维", "情绪强度"],
        }))
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["card_data"]["type"], "journal")
        self.assertEqual(payload["card_data"]["fields"][0]["label"], "触发情境")

    def test_render_card_builds_checklist_items(self) -> None:
        raw = __import__("asyncio").run(render_card.execute({
            "card_type": "checklist",
            "title": "睡前检查",
            "items": ["离开工位", "关闭消息通知", "做一次呼吸练习"],
        }))
        payload = json.loads(raw)

        self.assertEqual(payload["card_data"]["type"], "checklist")
        self.assertEqual(len(payload["card_data"]["items"]), 3)


if __name__ == "__main__":
    unittest.main()
