import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.phase_router import decide_next_phase


class PhaseRouterTests(unittest.TestCase):
    def test_router_keeps_p1_when_no_explore_signal(self) -> None:
        route = decide_next_phase(
            current_phase="p1_listener",
            phase_state={"intent": False, "explore": False},
        )

        self.assertEqual(route.active_phase, "p1_listener")
        self.assertEqual(route.transition_reason, "phase_unchanged")

    def test_router_moves_to_p2_when_explore_true(self) -> None:
        route = decide_next_phase(
            current_phase="p1_listener",
            phase_state={"intent": False, "explore": True},
        )

        self.assertEqual(route.active_phase, "p2_explorer")
        self.assertEqual(route.transition_reason, "explore_detected")

    def test_router_moves_to_p3_when_direct_intent_is_true_without_active_skill(self) -> None:
        route = decide_next_phase(
            current_phase="p1_listener",
            phase_state={"intent": True},
        )

        self.assertEqual(route.active_phase, "p3_recommender")
        self.assertEqual(route.transition_reason, "intent_detected")

    def test_router_keeps_p4_when_active_skill_is_present(self) -> None:
        route = decide_next_phase(
            current_phase="p2_explorer",
            phase_state={"active_skill": {"skill_name": "breathing_478"}},
        )

        self.assertEqual(route.active_phase, "p4_interventor")
        self.assertEqual(route.transition_reason, "active_skill_in_progress")

    def test_router_moves_from_p2_to_p3_only_when_more_exploration_is_not_needed(self) -> None:
        route = decide_next_phase(
            current_phase="p2_explorer",
            phase_state={
                "formulation_confirmed": True,
                "needs_more_exploration": False,
            },
        )

        self.assertEqual(route.active_phase, "p3_recommender")
        self.assertEqual(route.transition_reason, "formulation_confirmed")


if __name__ == "__main__":
    unittest.main()
