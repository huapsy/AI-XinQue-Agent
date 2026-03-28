import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.profile_helpers import (
    apply_profile_patch,
    build_alliance_patch,
    build_clinical_profile_patch_from_formulation,
    build_preference_patch_from_outcome,
)


class ProfileHelperTests(unittest.TestCase):
    def test_apply_profile_patch_keeps_existing_json_sections(self) -> None:
        existing = {
            "risk_level": "low",
            "alliance": {"alignment_score": 12, "misalignment_history": []},
            "preferences": {"preferred_techniques": ["mindfulness"]},
            "clinical_profile": {"key_themes": ["work_pressure"]},
        }

        merged = apply_profile_patch(
            existing,
            {
                "alliance": {"alignment_score": 9},
                "clinical_profile": {"dominant_emotions": ["anxiety"]},
            },
        )

        self.assertEqual(merged["risk_level"], "low")
        self.assertEqual(merged["preferences"]["preferred_techniques"], ["mindfulness"])
        self.assertEqual(merged["alliance"]["alignment_score"], 9)
        self.assertEqual(merged["clinical_profile"]["key_themes"], ["work_pressure"])
        self.assertEqual(merged["clinical_profile"]["dominant_emotions"], ["anxiety"])

    def test_build_clinical_profile_patch_from_formulation_aggregates_distinct_values(self) -> None:
        patch = build_clinical_profile_patch_from_formulation(
            {
                "primary_issue": "工作压力下的自我怀疑",
                "context": {"domain": "workplace"},
                "emotions": [{"name": "焦虑"}, {"name": "无力感"}],
                "cognitive_patterns": [
                    {"content": "我永远做不完", "type": "catastrophizing"},
                    {"content": "领导会觉得我不行", "type": "mind_reading"},
                ],
                "behavioral_patterns": {
                    "maladaptive": ["拖延", "回避反馈"],
                    "adaptive": ["写待办清单"],
                },
            }
        )

        self.assertEqual(patch["key_themes"], ["workplace"])
        self.assertEqual(set(patch["dominant_emotions"]), {"焦虑", "无力感"})
        self.assertEqual(set(patch["cognitive_distortions"]), {"catastrophizing", "mind_reading"})
        self.assertEqual(set(patch["behavioral_patterns"]), {"拖延", "回避反馈", "写待办清单"})

    def test_build_alliance_patch_updates_score_without_dropping_history(self) -> None:
        patch = build_alliance_patch(
            existing={"alignment_score": 12, "misalignment_history": [{"type": "confusion", "session_id": "s-1"}]},
            next_score=7,
            signal_type="dissatisfaction",
            session_id="s-2",
        )

        self.assertEqual(patch["alignment_score"], 7)
        self.assertEqual(len(patch["misalignment_history"]), 2)
        self.assertEqual(patch["misalignment_history"][-1]["type"], "dissatisfaction")

    def test_build_preference_patch_from_outcome_uses_feedback_to_update_preference(self) -> None:
        helpful = build_preference_patch_from_outcome("mindfulness", "breathing_478", "helpful")
        unhelpful = build_preference_patch_from_outcome("cbt", "thought_record", "unhelpful")

        self.assertEqual(helpful, {"preferred_techniques": ["mindfulness", "breathing_478"]})
        self.assertEqual(unhelpful, {"disliked_techniques": ["cbt", "thought_record"]})


if __name__ == "__main__":
    unittest.main()
