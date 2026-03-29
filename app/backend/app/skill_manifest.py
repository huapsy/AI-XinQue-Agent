"""Skill manifest v2 校验与标准化。"""

from __future__ import annotations


class SkillManifestError(ValueError):
    """Skill manifest 非法时抛出。"""


ALLOWED_OUTPUT_TYPES = {"dialogue", "card"}
ALLOWED_CARD_TEMPLATES = {None, "guided_exercise", "journal", "checklist"}


def validate_skill_manifest(frontmatter: dict) -> dict:
    """校验并标准化 skill manifest v2。"""
    manifest = dict(frontmatter or {})

    required_fields = [
        "name",
        "version",
        "display_name",
        "category",
        "trigger",
        "output_type",
        "estimated_turns",
        "cooldown_hours",
        "follow_up_rules",
        "completion_signals",
    ]
    missing = [field for field in required_fields if field not in manifest]
    if missing:
        raise SkillManifestError(f"missing required fields: {', '.join(missing)}")

    if manifest.get("output_type") not in ALLOWED_OUTPUT_TYPES:
        raise SkillManifestError(f"invalid output_type: {manifest.get('output_type')}")

    if manifest.get("card_template") not in ALLOWED_CARD_TEMPLATES:
        raise SkillManifestError(f"invalid card_template: {manifest.get('card_template')}")

    cooldown_hours = manifest.get("cooldown_hours")
    if not isinstance(cooldown_hours, int) or cooldown_hours < 0:
        raise SkillManifestError("cooldown_hours must be a non-negative integer")

    if not isinstance(manifest.get("follow_up_rules"), list):
        raise SkillManifestError("follow_up_rules must be a list")
    if not isinstance(manifest.get("completion_signals"), list):
        raise SkillManifestError("completion_signals must be a list")

    contraindications = manifest.get("contraindications", [])
    if not isinstance(contraindications, list):
        raise SkillManifestError("contraindications must be a list")

    manifest["contraindications"] = contraindications
    manifest["version"] = str(manifest["version"])
    return manifest
