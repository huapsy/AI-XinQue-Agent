"""用户画像聚合与合并辅助函数。"""

from __future__ import annotations

from copy import deepcopy


def _merge_unique_list(existing: list | None, new: list | None) -> list:
    """合并两个列表，保持顺序并去重。"""
    merged = list(existing or [])
    for item in new or []:
        if item not in merged:
            merged.append(item)
    return merged


def _merge_dict(existing: dict | None, patch: dict | None) -> dict:
    """递归合并 dict；列表字段走去重合并。"""
    result = deepcopy(existing or {})
    for key, value in (patch or {}).items():
        if isinstance(value, dict):
            result[key] = _merge_dict(result.get(key), value)
        elif isinstance(value, list):
            result[key] = _merge_unique_list(result.get(key), value)
        else:
            result[key] = value
    return result


def apply_profile_patch(existing: dict | None, patch: dict | None) -> dict:
    """合并画像 patch，避免 JSON 字段互相覆盖。"""
    return _merge_dict(existing, patch)


def build_clinical_profile_patch_from_formulation(formulation: dict) -> dict:
    """从 formulation 返回值提炼出 clinical_profile patch。"""
    context = formulation.get("context") or {}
    emotions = formulation.get("emotions") or []
    cognitions = formulation.get("cognitive_patterns") or []
    behaviors = formulation.get("behavioral_patterns") or {}

    dominant_emotions = [item["name"] for item in emotions if item.get("name")]
    cognitive_distortions = [item["type"] for item in cognitions if item.get("type")]
    behavioral_patterns = (behaviors.get("maladaptive") or []) + (behaviors.get("adaptive") or [])

    patch: dict[str, list | str] = {}
    if context.get("domain"):
        patch["key_themes"] = [context["domain"]]
    if dominant_emotions:
        patch["dominant_emotions"] = dominant_emotions
    if cognitive_distortions:
        patch["cognitive_distortions"] = cognitive_distortions
    if behavioral_patterns:
        patch["behavioral_patterns"] = behavioral_patterns
    if formulation.get("primary_issue"):
        patch["primary_issue"] = formulation["primary_issue"]
    return patch


def build_alliance_patch(
    existing: dict | None,
    next_score: int,
    signal_type: str | None,
    session_id: str,
) -> dict:
    """构建 alliance patch，保留历史并追加最新信号。"""
    history = list((existing or {}).get("misalignment_history", []))
    if signal_type:
        history.append({"type": signal_type, "session_id": session_id})
        history = history[-10:]
    return {
        "alignment_score": next_score,
        "misalignment_history": history,
    }


def build_preference_patch_from_outcome(
    category: str | None,
    skill_name: str,
    user_feedback: str | None,
) -> dict:
    """根据干预反馈生成偏好 patch。"""
    if user_feedback not in {"helpful", "unhelpful"}:
        return {}

    key = "preferred_techniques" if user_feedback == "helpful" else "disliked_techniques"
    values = []
    if category:
        values.append(category)
    values.append(skill_name)
    return {key: values}
