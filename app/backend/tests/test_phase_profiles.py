import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.phase_profiles import get_phase_profile, list_phase_profiles


class PhaseProfilesTests(unittest.TestCase):
    def test_list_phase_profiles_returns_all_phase_profiles(self) -> None:
        profiles = list_phase_profiles()

        self.assertEqual(
            set(profiles.keys()),
            {"p1_listener", "p2_explorer", "p3_recommender", "p4_interventor"},
        )

    def test_each_phase_profile_exposes_minimal_contract_fields(self) -> None:
        profile = get_phase_profile("p2_explorer")

        self.assertEqual(profile.key, "p2_explorer")
        self.assertTrue(profile.display_name)
        self.assertTrue(profile.goal)
        self.assertTrue(profile.allowed_tools)
        self.assertTrue(profile.prompt_block)

    def test_p4_interventor_allowed_tools_match_intervention_runtime(self) -> None:
        profile = get_phase_profile("p4_interventor")

        self.assertIn("load_skill", profile.allowed_tools)
        self.assertIn("record_outcome", profile.allowed_tools)
        self.assertNotIn("match_intervention", profile.allowed_tools)


if __name__ == "__main__":
    unittest.main()
