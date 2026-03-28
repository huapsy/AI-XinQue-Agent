import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.red_team_runner import RED_TEAM_CASES, run_red_team_suite
from app.safety.input_guard import CRISIS_RESPONSE, INJECTION_RESPONSE
from app.safety.output_guard import SAFE_REPLACEMENT


class RedTeamRegressionTests(unittest.TestCase):
    def test_red_team_suite_covers_required_categories(self) -> None:
        categories = {case["category"] for case in RED_TEAM_CASES}
        self.assertEqual(categories, {
            "crisis",
            "indirect_crisis",
            "prompt_injection",
            "diagnosis_bait",
            "medication_bait",
            "alignment_attack",
        })

    def test_red_team_suite_is_repeatable(self) -> None:
        results = run_red_team_suite()

        self.assertEqual(len(results), len(RED_TEAM_CASES))
        self.assertTrue(all(result["passed"] for result in results))
        crisis = next(result for result in results if result["category"] == "crisis")
        injection = next(result for result in results if result["category"] == "prompt_injection")
        diagnosis = next(result for result in results if result["category"] == "diagnosis_bait")

        self.assertEqual(crisis["actual"], CRISIS_RESPONSE)
        self.assertEqual(injection["actual"], INJECTION_RESPONSE)
        self.assertEqual(diagnosis["actual"], SAFE_REPLACEMENT)


if __name__ == "__main__":
    unittest.main()
