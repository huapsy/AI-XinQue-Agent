import asyncio
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import referral


class ReferralToolTests(unittest.TestCase):
    def test_default_referral_keeps_hotlines_when_urgency_missing(self) -> None:
        raw = asyncio.run(referral.execute({"reason": "问题超出能力范围"}))
        payload = json.loads(raw)

        self.assertEqual(payload["card_data"]["type"], "referral")
        self.assertEqual(payload["card_data"]["title"], "紧急支持资源")
        self.assertGreater(len(payload["card_data"]["resources"]), 1)
        self.assertEqual(payload["card_data"]["footer"], "紧急情况请拨打 120 或 110")

    def test_normal_referral_only_shows_booking_entry(self) -> None:
        raw = asyncio.run(referral.execute({"reason": "用户主动要求", "urgency": "normal"}))
        payload = json.loads(raw)

        self.assertEqual(payload["card_data"]["title"], "预约专业咨询师")
        self.assertEqual(len(payload["card_data"]["resources"]), 1)
        self.assertEqual(payload["card_data"]["resources"][0]["name"], "EAP 员工援助计划")


if __name__ == "__main__":
    unittest.main()
