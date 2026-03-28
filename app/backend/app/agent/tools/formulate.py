"""formulate — P2 主力工具：渐进式个案概念化

在探索对话中多次调用，每次传入新发现的临床观察，
渐进式构建个案概念化（case formulation）。
"""

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import CaseFormulation, UserProfile
from app.profile_helpers import apply_profile_patch, build_clinical_profile_patch_from_formulation

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "formulate",
        "description": (
            "P2 探索阶段的核心工具。在探索中每识别到有临床意义的新信息时调用。"
            "传入本轮发现的增量观察（情绪、认知、行为等），工具内部合并到当前个案概念化。"
            "返回完整的 formulation 和 readiness 状态。"
            "readiness='sufficient' 或 'solid' 时，可以进入 P3 推荐干预方案。"
            "不需要每轮都调用——用户说'嗯''好的'时不需要。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "emotions": {
                    "type": "array",
                    "description": "本轮识别到的情绪",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "情绪名称，如焦虑、无力感、愤怒"},
                            "intensity": {"type": "string", "description": "强度：mild/moderate/severe"},
                            "trigger": {"type": "string", "description": "触发情境"},
                        },
                        "required": ["name"],
                    },
                },
                "cognitions": {
                    "type": "array",
                    "description": "本轮识别到的认知模式/自动化思维",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "思维内容，如'我永远做不完'"},
                            "type": {"type": "string", "description": "认知扭曲类型：catastrophizing/dichotomous/negative_filtering/fortune_telling/mind_reading/personalising"},
                        },
                        "required": ["content"],
                    },
                },
                "behaviors": {
                    "type": "object",
                    "description": "本轮识别到的行为模式",
                    "properties": {
                        "maladaptive": {"type": "array", "items": {"type": "string"}, "description": "非适应性行为"},
                        "adaptive": {"type": "array", "items": {"type": "string"}, "description": "适应性行为"},
                    },
                },
                "context": {
                    "type": "object",
                    "description": "问题情境信息",
                    "properties": {
                        "domain": {"type": "string", "description": "领域：workplace/family/relationship/health/education/other"},
                        "duration": {"type": "string", "description": "持续时间"},
                        "precipitant": {"type": "string", "description": "诱因/触发事件"},
                        "generalization": {"type": "string", "description": "泛化情况"},
                    },
                },
                "alliance_signal": {
                    "type": "string",
                    "description": "本轮对齐信号：aligned/confusion/disagreement/dissatisfaction/distrust/refusal/uncertainty",
                },
                "primary_issue": {
                    "type": "string",
                    "description": "核心问题描述（当你能概括时填写）",
                },
            },
            "required": [],
        },
    },
}


def _merge_list(existing: list | None, new: list | None) -> list:
    """合并两个列表，去重（基于 JSON 序列化）"""
    existing = existing or []
    new = new or []
    seen = {json.dumps(item, ensure_ascii=False, sort_keys=True) for item in existing}
    for item in new:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            existing.append(item)
            seen.add(key)
    return existing


def _merge_behaviors(existing: dict | None, new: dict | None) -> dict:
    """合并行为模式"""
    existing = existing or {"maladaptive": [], "adaptive": []}
    new = new or {}
    for key in ("maladaptive", "adaptive"):
        items = new.get(key, [])
        for item in items:
            if item not in existing.get(key, []):
                existing.setdefault(key, []).append(item)
    return existing


def _merge_context(existing: dict | None, new: dict | None) -> dict:
    """合并情境信息（新值覆盖旧值）"""
    existing = existing or {}
    new = new or {}
    for key, val in new.items():
        if val:
            existing[key] = val
    return existing


def _compute_readiness(f: CaseFormulation) -> str:
    """根据 formulation 的完整度计算 readiness"""
    has_emotions = bool(f.emotional_state)
    has_cognitions = bool(f.cognitive_patterns)
    has_behaviors = bool(f.behavioral_patterns and (
        f.behavioral_patterns.get("maladaptive") or f.behavioral_patterns.get("adaptive")
    ))
    has_primary = bool(f.primary_issue)
    has_mechanism = bool(f.mechanism)

    if has_emotions and has_cognitions and has_behaviors and has_primary:
        if has_mechanism and not f.missing:
            return "solid"
        return "sufficient"
    return "exploring"


def _compute_missing(f: CaseFormulation) -> list[str]:
    """计算缺失的信息维度"""
    missing = []
    if not f.emotional_state:
        missing.append("情绪状态待探索")
    if not f.cognitive_patterns:
        missing.append("认知模式待探索")
    if not f.behavioral_patterns or not (
        f.behavioral_patterns.get("maladaptive") or f.behavioral_patterns.get("adaptive")
    ):
        missing.append("行为模式待探索")
    if not f.primary_issue:
        missing.append("核心问题待明确")
    if not f.context or not f.context.get("domain"):
        missing.append("问题领域待明确")
    return missing


def _generate_mechanism(f: CaseFormulation) -> str | None:
    """基于已有信息生成问题维持机制描述"""
    parts = []

    # 触发因素
    if f.context and f.context.get("precipitant"):
        parts.append(f.context["precipitant"])

    # 认知
    if f.cognitive_patterns:
        cog_desc = "、".join(c.get("content", c.get("type", "")) for c in f.cognitive_patterns[:2])
        parts.append(f"认知模式（{cog_desc}）")

    # 情绪
    if f.emotional_state:
        emo_desc = "、".join(e["name"] for e in f.emotional_state[:2])
        parts.append(f"情绪（{emo_desc}）")

    # 行为
    if f.behavioral_patterns:
        mal = f.behavioral_patterns.get("maladaptive", [])
        if mal:
            parts.append(f"行为（{'、'.join(mal[:2])}）")

    if len(parts) >= 3:
        return " → ".join(parts) + " → 强化循环"
    return None


async def execute(
    session_id: str,
    user_id: str,
    arguments: dict,
    db: AsyncSession,
) -> str:
    """执行 formulate()，返回 JSON 字符串"""

    # 查找当前会话的 formulation
    result = await db.execute(
        select(CaseFormulation).where(CaseFormulation.session_id == session_id)
    )
    formulation = result.scalar_one_or_none()

    # 首次调用：创建新记录
    if formulation is None:
        formulation = CaseFormulation(session_id=session_id, user_id=user_id)
        db.add(formulation)

    # 合并增量信息
    if arguments.get("emotions"):
        formulation.emotional_state = _merge_list(
            formulation.emotional_state, arguments["emotions"]
        )

    if arguments.get("cognitions"):
        formulation.cognitive_patterns = _merge_list(
            formulation.cognitive_patterns, arguments["cognitions"]
        )

    if arguments.get("behaviors"):
        formulation.behavioral_patterns = _merge_behaviors(
            formulation.behavioral_patterns, arguments["behaviors"]
        )

    if arguments.get("context"):
        formulation.context = _merge_context(
            formulation.context, arguments["context"]
        )

    if arguments.get("alliance_signal"):
        formulation.alliance_quality = arguments["alliance_signal"]

    if arguments.get("primary_issue"):
        formulation.primary_issue = arguments["primary_issue"]

    # 自动计算
    formulation.missing = _compute_missing(formulation)
    formulation.mechanism = _generate_mechanism(formulation)
    formulation.readiness = _compute_readiness(formulation)
    formulation.updated_at = datetime.now(timezone.utc)

    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile is not None:
        clinical_patch = build_clinical_profile_patch_from_formulation({
            "primary_issue": formulation.primary_issue,
            "context": formulation.context,
            "emotions": formulation.emotional_state,
            "cognitive_patterns": formulation.cognitive_patterns,
            "behavioral_patterns": formulation.behavioral_patterns,
        })
        profile.clinical_profile = apply_profile_patch(profile.clinical_profile, clinical_patch)

    await db.flush()

    # 返回完整 formulation
    return json.dumps({
        "formulation": {
            "readiness": formulation.readiness,
            "primary_issue": formulation.primary_issue,
            "mechanism": formulation.mechanism,
            "emotions": formulation.emotional_state,
            "cognitive_patterns": formulation.cognitive_patterns,
            "behavioral_patterns": formulation.behavioral_patterns,
            "context": formulation.context,
            "severity": formulation.severity,
            "alliance_quality": formulation.alliance_quality,
            "missing": formulation.missing,
        }
    }, ensure_ascii=False)
