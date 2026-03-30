"""Responses-first 运行时分层契约。"""

from __future__ import annotations

from app.responses_helpers import build_response_input, make_response_message


RUNTIME_LAYER_DEFINITIONS = {
    "instructions": "当前请求级高优先级行为约束。适用于本次生成，不自动跨轮继承。",
    "working_contract": "跨轮必须可见的最小行为契约。当走 stateful previous_response_id 时，以 assistant message 注入。",
    "working_context": "分层会话状态、语义摘要与稳定背景的运行时上下文。",
    "previous_response_id": "Responses 服务端上下文串接标识。仅负责串接，不替代产品级 contract；只在 stateful store=true 模式下启用。",
    "store": "是否启用 Responses 的服务端状态。关闭时必须回退到 stateless 完整输入路径。",
}


def build_working_contract_message(
    alignment_score: int | None,
    turn_number: int,
    active_phase: str | None = None,
    active_skill: dict | None = None,
) -> str:
    """构造跨轮仍需可见的最小契约。"""
    lines = [
        "人格摘要：你是心雀，一位专业但亲切的心理支持助手；保持专业、温和、自然的表达，不生硬、说教或教程化。",
        "最小系统契约：保持自然中文；遵守安全边界；不要越级推进；工具调用必须满足前置条件。",
        "回复风格：默认自然 prose，不使用列表、编号或文档腔；句子普遍较短，认知负担低。",
        "阶段纪律：P1 不做表单式分流；P2 先探索和形成理解，不抢跑到建议或干预；P3/P4 只在前提满足时进入。",
        "Flow Controller 语义：每轮都要维护最小阶段字段，包括 intent、explore、asking、formulation_confirmed、needs_more_exploration、chosen_intervention、intervention_complete。",
        "推进方式：默认探索驱动，而不是建议驱动；尤其在负向 flow 中优先按接住、正常化、缩小问题、一个具体问题来推进。",
        "回复骨架：默认每轮只问一个具体问题，不用分类选项、多入口并列问题或表单式分流替代咨询式推进。",
        "表达要求：所有总结、归因、机制判断都按工作性假设表达，不写成确定事实或诊断式结论。",
        "phase 纪律：区分中间 commentary、tool 过渡和 final answer，不要把中间状态当成最终用户可见回复。",
        "验证要求：输出前验证当前依赖、用户同意与安全边界；空结果或低置信度时先恢复，不要直接下结论。",
    ]
    if active_phase:
        lines.append(f"当前 active phase={active_phase}：本轮优先遵守该阶段子Agent的行为边界。")
    if active_skill and active_skill.get("skill_name"):
        lines.append(
            f"当前 active skill={active_skill['skill_name']}：未完成前优先继续当前 skill，除非用户明确拒绝、要求切换方法，或危机接管。"
        )
    if turn_number <= 2:
        lines.append("回合纪律：当前仍属早期轮次，优先建立理解与上下文，不要过早推荐干预。")
    if turn_number >= 6:
        lines.append("长会话纪律：优先复用已有总结与状态，不要机械重放完整历史。")
    if alignment_score is not None:
        if alignment_score <= 0:
            lines.append("对齐警告：用户当前高度不对齐，只做接纳和倾听，不做功能性推进。")
        elif alignment_score <= 5:
            lines.append("对齐状态较低：先修复理解和关系，不要直接推进新的建议或干预。")
    return "\n".join(lines)


def should_use_stateful_responses(store_enabled: bool, previous_response_id: str | None) -> bool:
    """判断当前是否应走 stateful Responses 模式。"""
    return bool(store_enabled and previous_response_id)


def build_runtime_input(
    *,
    effective_history: list[dict],
    user_message: str,
    alignment_score: int | None,
    turn_number: int,
    previous_response_id: str | None,
    store_enabled: bool,
    active_phase: str | None = None,
    active_skill: dict | None = None,
) -> tuple[list[dict], str | None]:
    """根据 store/previous_response_id 构造本轮 Responses 输入。"""
    if should_use_stateful_responses(store_enabled, previous_response_id):
        return [
            make_response_message(
                "assistant",
                build_working_contract_message(
                    alignment_score,
                    turn_number,
                    active_phase=active_phase,
                    active_skill=active_skill,
                ),
                phase="commentary",
            ),
            make_response_message("assistant", effective_history[0]["content"], phase="commentary"),
            make_response_message("user", user_message),
        ], previous_response_id

    return build_response_input(effective_history, user_message), None


def extend_stateless_input_with_tool_outputs(pending_input: list[dict], tool_outputs: list[dict]) -> list[dict]:
    """在 stateless 模式下把 tool output 累积进下一次请求输入。"""
    return [*pending_input, *tool_outputs]
