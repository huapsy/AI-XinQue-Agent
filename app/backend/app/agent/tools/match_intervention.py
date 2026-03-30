"""match_intervention — P3 主力工具：匹配干预方案

基于当前 formulation + 用户画像，从 Skill 库中匹配最合适的 1-2 个干预方案。
"""

import json
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import CaseFormulation, Intervention, UserProfile
from app.skill_registry import load_skill_registry

TOOL_DEFINITION = {
    "type": "function",
    "name": "match_intervention",
    "description": (
        "当 formulation 的 readiness 为 sufficient 或 solid 时调用。"
        "基于当前个案概念化和用户画像，匹配 1-2 个最合适的干预方案。"
        "返回方案列表，每个包含 skill_name、rationale 和 user_friendly_intro，"
        "供你向用户自然地介绍方案。"
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

def _load_skill_metadata() -> list[dict]:
    """加载所有 skill manifest 元数据。"""
    return [entry["manifest"] for entry in load_skill_registry().values()]


def _match_skills(
    formulation: CaseFormulation | None,
    profile: UserProfile | None,
    skills: list[dict],
    recent_interventions: list[Intervention] | None = None,
) -> list[dict]:
    """根据 formulation 和用户偏好匹配 skill"""
    if not formulation:
        return []

    # 收集认知扭曲类型
    distortion_types = set()
    for cp in (formulation.cognitive_patterns or []):
        if cp.get("type"):
            distortion_types.add(cp["type"])

    # 收集情绪关键词
    emotion_names = set()
    for em in (formulation.emotional_state or []):
        if em.get("name"):
            emotion_names.add(em["name"].lower())

    # 用户偏好
    preferred = set()
    disliked = set()
    if profile and profile.preferences:
        preferred = set(profile.preferences.get("preferred_techniques", []))
        disliked = set(profile.preferences.get("disliked_techniques", []))

    recent_interventions = recent_interventions or []
    scored: list[tuple[int, dict]] = []
    candidate_names = {skill.get("name", "") for skill in skills}
    candidate_categories = {skill.get("category", "") for skill in skills if skill.get("category")}

    for skill in skills:
        name = skill.get("name", "")
        category = skill.get("category", "")

        # 排除用户不喜欢的技术
        if category in disliked or name in disliked:
            continue

        # 排除危机禁忌
        contras = skill.get("contraindications", [])
        if any(c.get("risk_category") == "crisis" for c in contras):
            if profile and profile.risk_level == "crisis":
                continue

        score = 0

        # 认知扭曲 → CBT 认知重构
        if distortion_types and category == "cbt":
            score += 10

        # 反刍/融合思维 → ACT 认知解离
        rumination_keywords = {"反刍", "控制不住", "停不下来", "一直想", "赶不走"}
        cognition_contents = set()
        for cp in (formulation.cognitive_patterns or []):
            if cp.get("content"):
                cognition_contents.add(cp["content"])
        # 检查认知内容中是否有反刍特征
        has_rumination = any(
            kw in content for content in cognition_contents for kw in rumination_keywords
        )
        if has_rumination and name == "defusion":
            score += 9

        # 焦虑相关情绪 → 呼吸/正念
        anxiety_keywords = {"焦虑", "紧张", "压力", "anxiety", "不安", "烦躁"}
        if emotion_names & anxiety_keywords and category == "mindfulness":
            score += 8

        # 躯体化 → 身体扫描
        somatic_keywords = {"胸闷", "肩膀紧", "头疼", "胃", "失眠", "身体"}
        if emotion_names & somatic_keywords and name == "body_scan":
            score += 8

        # 消极过滤/低落 → 感恩日记
        if "negative_filtering" in distortion_types and name == "gratitude_journal":
            score += 7
        low_mood_keywords = {"低落", "沮丧", "绝望", "消沉", "没意思"}
        if emotion_names & low_mood_keywords and name == "gratitude_journal":
            score += 6

        # 恐慌/高焦虑 → 接地练习
        panic_keywords = {"恐慌", "panic", "发作", "心跳", "喘不上气", "头晕", "害怕"}
        if emotion_names & panic_keywords and name == "grounding_54321":
            score += 9

        # 模糊情绪 → 情绪命名
        vague_keywords = {"不好", "不舒服", "难受", "烦", "不太好"}
        if emotion_names & vague_keywords and name == "emotion_naming":
            score += 7
        if emotion_names & anxiety_keywords and name == "emotion_naming":
            score += 3

        # 低落 + 非严重 → 三件好事
        if emotion_names & low_mood_keywords and name == "three_good_things":
            score += 5

        # 用户偏好加分
        if category in preferred:
            score += 3

        score += _freshness_adjustment(skill, recent_interventions)

        if score > 0:
            scored.append((score, skill))

    # 按分数降序，取前 2
    scored.sort(key=lambda x: -x[0])
    selected = [dict(item[1]) for item in scored[:2]]
    for skill in selected:
        reasons = _selection_cooling_reasons(skill, recent_interventions, candidate_names, candidate_categories)
        skill["cooling_applied"] = bool(reasons)
        skill["cooling_reasons"] = reasons
        skill["continuity_reason"] = (
            "alternative_due_to_recent_cooling"
            if reasons and all(getattr(intervention, "skill_name", None) != skill.get("name") for intervention in recent_interventions)
            else "direct_match"
        )
    return selected


def _freshness_adjustment(skill: dict, recent_interventions: list["Intervention"]) -> int:
    """对刚做过/刚推荐过的 skill 做最小冷却降权。"""
    current = datetime.now().astimezone()
    name = skill.get("name", "")
    category = skill.get("category", "")
    cooldown_hours = int(skill.get("cooldown_hours", 48) or 48)
    adjustment = 0

    for intervention in recent_interventions:
        started_at = getattr(intervention, "started_at", None)
        if started_at is None:
            continue
        if current - started_at > timedelta(hours=cooldown_hours):
            continue

        if getattr(intervention, "skill_name", None) == name:
            adjustment -= 6
        elif category and _skill_name_category(intervention.skill_name) == category:
            adjustment -= 2
        if getattr(intervention, "user_feedback", None) == "unhelpful":
            if getattr(intervention, "skill_name", None) == name:
                adjustment -= 6
            elif category and _skill_name_category(intervention.skill_name) == category:
                adjustment -= 8

    return adjustment


def _selection_cooling_reasons(
    selected_skill: dict,
    recent_interventions: list["Intervention"],
    candidate_names: set[str],
    candidate_categories: set[str],
) -> list[str]:
    """返回当前入选 skill 的最小冷却解释。"""
    current = datetime.now().astimezone()
    selected_name = selected_skill.get("name", "")
    reasons: list[str] = []

    for intervention in recent_interventions:
        started_at = getattr(intervention, "started_at", None)
        if started_at is None:
            continue
        cooldown_hours = int(selected_skill.get("cooldown_hours", 48) or 48)
        if current - started_at > timedelta(hours=cooldown_hours):
            continue

        recent_name = getattr(intervention, "skill_name", None)
        recent_category = _skill_name_category(recent_name)

        if recent_name in candidate_names and "same_skill_recent" not in reasons:
            if recent_name != selected_name:
                reasons.append("same_skill_recent")

        if recent_category and recent_category in candidate_categories and "same_category_recent" not in reasons:
            if recent_category == selected_skill.get("category"):
                reasons.append("same_category_recent")

        if getattr(intervention, "user_feedback", None) == "unhelpful" and "recent_unhelpful_feedback" not in reasons:
            reasons.append("recent_unhelpful_feedback")

    return reasons


def _skill_name_category(skill_name: str | None) -> str | None:
    if not skill_name:
        return None
    entry = load_skill_registry().get(skill_name)
    if not entry:
        return None
    return entry["manifest"].get("category")


def _build_plan(skill: dict, formulation: CaseFormulation | None) -> dict:
    """构建单个方案的输出"""
    name = skill.get("name", "")
    display = skill.get("display_name", name)
    category = skill.get("category", "")
    output_type = skill.get("output_type", "dialogue")

    # 根据 skill 特点生成 rationale 和 intro
    rationale = ""
    intro = ""

    if name == "cognitive_restructuring":
        distortions = []
        if formulation and formulation.cognitive_patterns:
            distortions = [cp.get("type", "") for cp in formulation.cognitive_patterns]
        target = " + ".join(distortions[:2]) if distortions else "认知扭曲"
        rationale = f"用户存在{target}，认知重构直接针对思维模式"
        intro = "我们一起看看那些自动冒出来的想法，检验一下它们是不是完全符合事实"
    elif name == "breathing_478":
        rationale = "用户焦虑程度较高，呼吸练习提供即时的躯体放松，降低唤醒水平"
        intro = "一个简单的呼吸练习，只需要几分钟，帮你在压力大的时候让身体先放松下来"
    elif name == "emotion_naming":
        rationale = "用户情绪表达较模糊，命名情绪有助于提升觉察和降低情绪强度"
        intro = "我们一起来看看你现在的感觉到底是什么，给它一个具体的名字"
    elif name == "defusion":
        rationale = "用户存在反刍思维，认知解离帮助用户与想法保持距离而非被想法控制"
        intro = "有一个方法不是要赶走那个反复出现的想法，而是学会和它保持一点距离"
    elif name == "body_scan":
        rationale = "用户有躯体化的焦虑表现，身体扫描帮助放松身体、增强身体觉察"
        intro = "一个简单的身体扫描练习，帮你放松身体里那些紧绷的地方"
    elif name == "gratitude_journal":
        rationale = "用户存在消极过滤，感恩日记帮助扩展积极情绪体验、打破消极注意偏向"
        intro = "一个很简单的练习，帮你找回那些被'滤掉'的好事"
    elif name == "thought_record":
        rationale = "用户存在多个自动化思维，想法记录帮助系统性地记录和检验想法"
        intro = "把那些让你难受的想法写下来，理清楚它们，然后看看有没有另一种看法"
    elif name == "grounding_54321":
        rationale = "用户正在经历高度焦虑或恐慌，接地练习帮助快速回到当下"
        intro = "一个只需要几分钟的练习，用你的五个感官帮你回到这里"
    elif name == "three_good_things":
        rationale = "用户情绪低落，三件好事练习帮助培养积极注意偏向"
        intro = "每天找出三件好事，听起来简单，但坚持下来效果出乎意料"
    else:
        rationale = f"基于当前评估，{display}可能对用户有帮助"
        intro = f"我们可以试试{display}"

    result = {
        "skill_name": name,
        "display_name": display,
        "rationale": rationale,
        "approach": output_type,
        "user_friendly_intro": intro,
    }

    duration = skill.get("estimated_duration")
    turns = skill.get("estimated_turns")
    if duration:
        result["estimated_duration"] = duration
    if turns:
        result["estimated_turns"] = turns
    result["cooldown_hours"] = skill.get("cooldown_hours")
    result["follow_up_rules"] = skill.get("follow_up_rules", [])
    result["completion_signals"] = skill.get("completion_signals", [])

    return result


async def execute(
    session_id: str,
    user_id: str,
    db: AsyncSession,
) -> str:
    """执行 match_intervention，返回 JSON 字符串"""

    # 读取当前 formulation
    result = await db.execute(
        select(CaseFormulation).where(CaseFormulation.session_id == session_id)
    )
    formulation = result.scalar_one_or_none()

    # 读取用户画像
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    result = await db.execute(
        select(Intervention)
        .where(Intervention.user_id == user_id)
        .order_by(Intervention.started_at.desc())
        .limit(5)
    )
    recent_interventions = result.scalars().all()

    # 加载 skill 元数据并匹配
    all_skills = _load_skill_metadata()
    matched = _match_skills(formulation, profile, all_skills, recent_interventions=recent_interventions)

    if not matched:
        return json.dumps({
            "plans": [],
            "message": "当前没有匹配的干预方案，建议继续探索"
        }, ensure_ascii=False)

    plans = [_build_plan(s, formulation) for s in matched]

    return json.dumps({"plans": plans}, ensure_ascii=False)
