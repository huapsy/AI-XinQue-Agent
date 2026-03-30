import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.phase_state import build_default_phase_state


class PhaseStateTests(unittest.TestCase):
    def test_build_default_phase_state_returns_minimal_fields(self) -> None:
        state = build_default_phase_state()

        self.assertEqual(
            set(state.keys()),
            {
                "active_phase",
                "phase_transition_reason",
                "intent",
                "explore",
                "asking",
                "formulation_confirmed",
                "needs_more_exploration",
                "chosen_intervention",
                "intervention_complete",
                "active_skill",
            },
        )
        self.assertEqual(state["active_phase"], "p1_listener")
        self.assertIsNone(state["phase_transition_reason"])
        self.assertFalse(state["intent"])
        self.assertFalse(state["explore"])


if __name__ == "__main__":
    unittest.main()
