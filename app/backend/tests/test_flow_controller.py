import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.flow_controller import normalize_phase_state, run_flow_controller


class FlowControllerTests(unittest.TestCase):
    def test_normalize_phase_state_fills_all_minimal_fields(self) -> None:
        normalized = normalize_phase_state(
            current_phase="p2_explorer",
            raw_phase_state={"explore": True, "asking": "feeling"},
            active_skill={"skill_name": "breathing_478"},
        )

        self.assertEqual(normalized["active_phase"], "p2_explorer")
        self.assertIsNone(normalized["phase_transition_reason"])
        self.assertTrue(normalized["explore"])
        self.assertEqual(normalized["asking"], "feeling")
        self.assertEqual(normalized["active_skill"]["skill_name"], "breathing_478")
        self.assertIn("chosen_intervention", normalized)
        self.assertIn("needs_more_exploration", normalized)

    def test_flow_controller_routes_direct_intent_to_p3_when_no_active_skill(self) -> None:
        decision = run_flow_controller(
            current_phase="p1_listener",
            raw_phase_state={"intent": True},
            active_skill=None,
        )

        self.assertEqual(decision.active_phase, "p3_recommender")
        self.assertEqual(decision.phase_transition_reason, "intent_detected")
        self.assertTrue(decision.normalized_phase_state["intent"])

    def test_flow_controller_routes_to_p4_when_active_skill_exists(self) -> None:
        decision = run_flow_controller(
            current_phase="p1_listener",
            raw_phase_state={"intent": True},
            active_skill={"skill_name": "breathing_478"},
        )

        self.assertEqual(decision.active_phase, "p4_interventor")
        self.assertEqual(decision.phase_transition_reason, "active_skill_in_progress")

    def test_flow_controller_keeps_p2_when_more_exploration_is_needed(self) -> None:
        decision = run_flow_controller(
            current_phase="p2_explorer",
            raw_phase_state={
                "formulation_confirmed": True,
                "needs_more_exploration": True,
                "asking": "thought",
            },
            active_skill=None,
        )

        self.assertEqual(decision.active_phase, "p2_explorer")
        self.assertEqual(decision.phase_transition_reason, "phase_unchanged")
        self.assertEqual(decision.normalized_phase_state["asking"], "thought")

    def test_flow_controller_routes_from_p3_to_p4_when_intervention_is_chosen(self) -> None:
        decision = run_flow_controller(
            current_phase="p3_recommender",
            raw_phase_state={"chosen_intervention": "breathing_478"},
            active_skill=None,
        )

        self.assertEqual(decision.active_phase, "p4_interventor")
        self.assertEqual(decision.phase_transition_reason, "intervention_chosen")

    def test_flow_controller_routes_from_p4_back_to_p1_when_intervention_completes(self) -> None:
        decision = run_flow_controller(
            current_phase="p4_interventor",
            raw_phase_state={"intervention_complete": True},
            active_skill=None,
        )

        self.assertEqual(decision.active_phase, "p1_listener")
        self.assertEqual(decision.phase_transition_reason, "intervention_completed")


if __name__ == "__main__":
    unittest.main()
