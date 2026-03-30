"""主 agent 的最小 phase 路由器。"""

from __future__ import annotations

from dataclasses import dataclass

from app.agent.flow_controller import run_flow_controller


@dataclass(frozen=True)
class PhaseRouteDecision:
    """phase 路由结果。"""

    active_phase: str
    transition_reason: str


def decide_next_phase(current_phase: str, phase_state: dict) -> PhaseRouteDecision:
    """根据最小 flow state 决定下一阶段。"""
    decision = run_flow_controller(
        current_phase=current_phase,
        raw_phase_state=phase_state,
        active_skill=phase_state.get("active_skill"),
    )
    return PhaseRouteDecision(decision.active_phase, decision.phase_transition_reason)
