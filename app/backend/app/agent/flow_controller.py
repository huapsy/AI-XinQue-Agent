"""Flow Controller：阶段字段归一化与阶段迁移控制平面。"""

from __future__ import annotations

from dataclasses import dataclass


ALLOWED_ASKING_VALUES = {"situation", "feeling", "thought", "formulation", "other"}


@dataclass(frozen=True)
class FlowControllerDecision:
    """Flow Controller 的单次决策结果。"""

    active_phase: str
    phase_transition_reason: str
    raw_phase_state: dict
    normalized_phase_state: dict


def build_minimal_flow_state(
    *,
    active_phase: str = "p1_listener",
    active_skill: dict | None = None,
) -> dict:
    """构造最小 flow state 默认值。"""
    return {
        "active_phase": active_phase,
        "phase_transition_reason": None,
        "intent": False,
        "explore": False,
        "asking": None,
        "formulation_confirmed": False,
        "needs_more_exploration": False,
        "chosen_intervention": None,
        "intervention_complete": False,
        "active_skill": dict(active_skill or {}),
    }


def normalize_phase_state(
    *,
    current_phase: str,
    raw_phase_state: dict | None,
    active_skill: dict | None,
) -> dict:
    """把零散阶段字段收口为最小稳定 flow state。"""
    raw_phase_state = dict(raw_phase_state or {})
    normalized = build_minimal_flow_state(
        active_phase=str(raw_phase_state.get("active_phase") or current_phase or "p1_listener"),
        active_skill=active_skill or raw_phase_state.get("active_skill"),
    )

    normalized["intent"] = bool(raw_phase_state.get("intent"))
    normalized["explore"] = bool(raw_phase_state.get("explore"))
    asking = raw_phase_state.get("asking")
    if isinstance(asking, str):
        asking = asking.strip().lower()
    normalized["asking"] = asking if asking in ALLOWED_ASKING_VALUES else None
    normalized["formulation_confirmed"] = bool(raw_phase_state.get("formulation_confirmed"))
    normalized["needs_more_exploration"] = bool(raw_phase_state.get("needs_more_exploration"))
    normalized["chosen_intervention"] = raw_phase_state.get("chosen_intervention") or None
    normalized["intervention_complete"] = bool(raw_phase_state.get("intervention_complete"))

    return normalized


def run_flow_controller(
    *,
    current_phase: str,
    raw_phase_state: dict | None,
    active_skill: dict | None,
) -> FlowControllerDecision:
    """执行一次 flow controller：归一化字段并给出下一阶段。"""
    normalized = normalize_phase_state(
        current_phase=current_phase,
        raw_phase_state=raw_phase_state,
        active_skill=active_skill,
    )

    if normalized.get("active_skill"):
        next_phase = "p4_interventor"
        reason = "active_skill_in_progress"
    elif current_phase == "p4_interventor" and normalized.get("intervention_complete"):
        next_phase = "p1_listener"
        reason = "intervention_completed"
    elif current_phase == "p3_recommender" and normalized.get("chosen_intervention"):
        next_phase = "p4_interventor"
        reason = "intervention_chosen"
    elif (
        current_phase in {"p1_listener", "p2_explorer"}
        and normalized.get("formulation_confirmed")
        and not normalized.get("needs_more_exploration")
    ):
        next_phase = "p3_recommender"
        reason = "formulation_confirmed"
    elif current_phase == "p1_listener" and normalized.get("explore"):
        next_phase = "p2_explorer"
        reason = "explore_detected"
    elif current_phase == "p1_listener" and normalized.get("intent"):
        next_phase = "p3_recommender"
        reason = "intent_detected"
    else:
        next_phase = current_phase
        reason = "phase_unchanged"

    normalized["active_phase"] = next_phase
    normalized["phase_transition_reason"] = reason
    return FlowControllerDecision(
        active_phase=next_phase,
        phase_transition_reason=reason,
        raw_phase_state=raw_phase_state or {},
        normalized_phase_state=normalized,
    )
