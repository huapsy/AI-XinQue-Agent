#!/usr/bin/env python3
"""从 extracted/neenan_epub 批量生成 interventions/*.md。

- TOC：要点 1–48（跳过 33、34，与手工精修重复）。
- Spine：按正文中的要点编号切分 49–100（同一 HTML 内多条自动拆开）。

description 仅含短摘录 + 用户向说明，不复制大段原文。
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "extracted" / "neenan_epub"
OUT = ROOT / "interventions"
SKIP_IDS = {
    "guided_self_discovery_questions",
    "imagery_hot_cognition",
}

TOC_MAP: list[tuple[str, int, str]] = [
    ("toc_005_1_it_is_not_events_per_se_that_determine_our_feelings.txt", 1, "formulation"),
    ("toc_006_2_information_processing_becomes_distorted_when.txt", 2, "formulation"),
    ("toc_007_3_an_emotional_disorder_is_usually_understood.txt", 3, "formulation"),
    ("toc_008_4_thoughts_feelings_behaviour_physiology.txt", 4, "formulation"),
    ("toc_009_5_emotional_reactions_to_events_are_viewed.txt", 5, "formulation"),
    ("toc_010_6_emotional_disorders_have_a_specific_cognitive.txt", 6, "formulation"),
    ("toc_011_7_cognitive_vulnerability_to_emotional_disturbance_19.txt", 7, "formulation"),
    ("toc_012_8_our_thoughts_and_beliefs_are_both_knowable.txt", 8, "formulation"),
    ("toc_013_9_acquisition_of_emotional_disturbance_23.txt", 9, "formulation"),
    ("toc_014_10_maintenance_of_emotional_disturbance_25.txt", 10, "formulation"),
    ("toc_015_11_the_client_as_personal_scientist_27.txt", 11, "formulation"),
    ("toc_016_12_only_articulate_and_intelligent_clients_can.txt", 12, "psychoeducation"),
    ("toc_017_13_cbt_does_not_focus_on_feelings_33.txt", 13, "psychoeducation"),
    ("toc_018_14_cbt_is_basically_positive_thinking_36.txt", 14, "psychoeducation"),
    ("toc_019_15_cbt_seems_too_simple_38.txt", 15, "psychoeducation"),
    ("toc_020_16_cbt_is_little_more_than_symptom_relief_40.txt", 16, "psychoeducation"),
    ("toc_021_17_cbt_is_not_interested_in_the_client_s_past_or.txt", 17, "psychoeducation"),
    ("toc_022_18_cbt_does_not_make_use_of_the_relationship.txt", 18, "psychoeducation"),
    ("toc_023_19_cbt_is_not_interested_in_the_social_and.txt", 19, "psychoeducation"),
    ("toc_024_20_cbt_is_just_the_application_of_common.txt", 20, "psychoeducation"),
    ("toc_025_21_cbt_is_just_technique-_oriented_50.txt", 21, "psychoeducation"),
    ("toc_026_22_setting_the_scene_57.txt", 22, "session_structure"),
    ("toc_027_23_undertaking_an_assessment_60.txt", 23, "session_structure"),
    ("toc_028_24_assessing_client_suitability_for_cbt_63.txt", 24, "session_structure"),
    ("toc_029_25_structuring_the_therapy_session_66.txt", 25, "session_structure"),
    ("toc_030_26_setting_the_agenda_68.txt", 26, "session_structure"),
    ("toc_031_27_drawing_up_a_problem_list_70.txt", 27, "session_structure"),
    ("toc_032_28_agreeing_on_goals_72.txt", 28, "session_structure"),
    ("toc_033_29_teaching_the_cognitive_model_75.txt", 29, "session_structure"),
    ("toc_034_30_developing_a_case_conceptualization_78.txt", 30, "session_structure"),
    ("toc_035_31_developing_treatment_plans_82.txt", 31, "session_structure"),
    ("toc_037_32_detecting_nats_87.txt", 32, "intervention"),
    ("toc_040_35_making_suggestions_95.txt", 35, "intervention"),
    ("toc_041_36_in-_session_emotional_changes_97.txt", 36, "intervention"),
    ("toc_042_37_finding_the_thoughts_by_ascertaining_the_client_s.txt", 37, "intervention"),
    ("toc_043_38_focusing_on_feelings_101.txt", 38, "intervention"),
    ("toc_044_39_assuming_the_worst_103.txt", 39, "intervention"),
    ("toc_045_40_situational_exposure_105.txt", 40, "intervention"),
    ("toc_046_41_role_play_107.txt", 41, "intervention"),
    ("toc_047_42_analyzing_a_specific_situation_109.txt", 42, "intervention"),
    ("toc_048_43_nats_in_shorthand_110.txt", 43, "intervention"),
    ("toc_049_44_symptom_induction_112.txt", 44, "intervention"),
    ("toc_050_45_behavioural_assignments_114.txt", 45, "intervention"),
    ("toc_051_46_eliciting_key_nats_from_less_important.txt", 46, "intervention"),
    ("toc_052_47_separating_situations_thoughts_and_feelings_119.txt", 47, "intervention"),
    ("toc_053_48_distinguishing_between_thoughts_and_feelings_122.txt", 48, "intervention"),
]


def _strip_headers(text: str) -> str:
    return "\n".join(L for L in text.replace("\r\n", "\n").splitlines() if not L.startswith("#")).strip()


def _split_spine_by_points(raw: str) -> list[tuple[int, str]]:
    """按行首单独成行的要点编号 1–100 切分（用于 spine 多要点 HTML）。"""
    body = _strip_headers(raw)
    if "APPENDIX" in body[:600] and re.search(r"^APPENDIX\s", body, re.MULTILINE):
        return []
    parts = re.split(r"(?m)^(\d{1,3})\s*$", body)
    out: list[tuple[int, str]] = []
    i = 1
    while i + 1 < len(parts):
        try:
            n = int(parts[i])
        except ValueError:
            i += 2
            continue
        if not (1 <= n <= 100):
            i += 2
            continue
        chunk = (parts[i + 1] or "").strip()
        if chunk:
            out.append((n, chunk))
        i += 2
    return out


def _extract_title_snippet(chunk: str) -> tuple[str, str]:
    chunk = chunk.replace("\r\n", "\n").strip()
    chunk = re.sub(r"^[\ufeff\u200b]*", "", chunk)
    chunk = re.sub(r"^\d{1,3}\s*\n+", "", chunk)
    lines = chunk.splitlines()
    title_parts: list[str] = []
    after_title = 0
    for j, line in enumerate(lines[:22]):
        s = line.strip()
        if not s:
            continue
        if s.isupper() and len(s) < 72 and not s.isdigit():
            title_parts.append(s)
            after_title = j + 1
            continue
        if title_parts:
            after_title = j
            break
        if re.match(r"^[A-Za-z]", s) and len(s) < 100:
            title_parts.append(s)
            after_title = j + 1
            break
        break
    title_en = re.sub(r"\s+", " ", " ".join(title_parts)).strip() if title_parts else "Section"
    rest = "\n".join(lines[after_title:]).strip() if title_parts else chunk
    snip = re.sub(r"\s+", " ", rest[:650]).strip()
    if len(snip) > 450:
        snip = snip[:447] + "…"
    return title_en, snip


def _slug(point: int, title_en: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "_", title_en.lower())[:50].strip("_")
    return f"neenan_{point:02d}_{base or 'point'}"


def _role_for_point(point: int) -> str:
    if point <= 11:
        return "formulation"
    if point <= 21:
        return "psychoeducation"
    if point <= 31:
        return "session_structure"
    if point <= 48:
        return "intervention"
    if point <= 62:
        return "intervention"
    if point <= 84:
        return "intervention"
    if point in (98, 99):
        return "agent_guidance"
    return "intervention"


def _steps(role: str) -> list[str]:
    if role == "formulation":
        return [
            "用一两句话写下触发事件（事实，不带评价）。",
            "分别记下：想法、情绪名称、身体感受、外显行为（能写多少写多少）。",
            "问自己：这些反应如何互相加强？改变其中一环可能带来什么不同？",
            "情绪激动时只做记录，不要求当场「想通」。",
        ]
    if role == "psychoeducation":
        return [
            "写出你曾经相信的一句话（关于 CBT 或关于自己）。",
            "对照本条要点，用你自己的话写下更贴近 CBT 的表述。",
            "举一个与你相关的小例子，分别用旧框架与新框架描述。",
            "写下一步你愿意尝试的一个微小行为实验（可选）。",
        ]
    if role == "session_structure":
        return [
            "准备 10–15 分钟与纸笔或文档。",
            "按条目要求逐项填写（问题、目标、议程等）。",
            "标出本周最重要的一条，并写一个可执行的微行动。",
            "回顾时调整计划，不自我攻击。",
        ]
    if role == "agent_guidance":
        return [
            "阅读要点，记下对你作为「自助者」仍可能有启发的 1～2 句。",
            "思考：若与 AI/真人支持者合作，你希望对方如何配合。",
            "不强行自我套用治疗师才适用的流程。",
        ]
    return [
        "选定一个最近发生的、足够小的具体情境。",
        "按技术步骤练习，并记录情绪强度（0–10）与关键想法。",
        "写下练习后的新发现（哪怕很小）。",
        "若痛苦骤升，暂停并改用稳定化策略或寻求支持。",
    ]


def _context(role: str) -> tuple[list[str], list[str], list[str], list[str]]:
    if role == "formulation":
        return (
            ["困扰反复、情绪波动、想理解「怎么了」"],
            ["焦虑、低落、愤怒、紧张、失眠伴反刍"],
            ["工作、家庭、人际、健康事件"],
            ["危机时以安全为先。"],
        )
    if role == "psychoeducation":
        return (
            ["对 CBT 存疑或误解"],
            ["疑惑、防御"],
            ["开始自助或求助前"],
            ["严重现实检验受损或人身风险时需专业介入。"],
        )
    if role == "session_structure":
        return (
            ["生活混乱、需梳理问题与目标"],
            ["无助、拖延、混乱感"],
            ["周初计划、睡前整理、咨询间隙"],
            ["极度绝望时先联系信任的人或热线。"],
        )
    if role == "agent_guidance":
        return (
            ["了解治疗过程与专业设置"],
            ["好奇、期待、焦虑"],
            ["考虑是否求助、如何与专业人士沟通"],
            ["本条多面向治疗师训练，自助者择要而用。"],
        )
    return (
        ["自动化思维、回避、焦虑抑郁相关模式"],
        ["焦虑、抑郁、羞耻、愤怒"],
        ["可具体想象的生活场景"],
        ["暴露与症状诱发类请在安全前提下进行。"],
    )


def _display(point: int, title_en: str) -> str:
    return f"要点 {point}：{title_en[:56]}{'…' if len(title_en) > 56 else ''}"


def _build_md(point: int, role: str, title_en: str, snippet: str, slug: str) -> str:
    steps = _steps(role)
    probs, symp, sits, notes = _context(role)
    desc = (
        f"{_display(point, title_en)}。以下为基于 Neenan《100 key points》要义的**用户向自助说明**，非原文。"
    )
    if snippet:
        desc += f" 语境摘录（自动截取）：「{snippet}」"

    lines = [
        "---",
        f"id: {slug}",
        f"display_name: {_display(point, title_en)}",
        'source_book: "Neenan — Cognitive behaviour therapy: 100 key points"',
        f'source_point: "{point} {title_en[:80]}"',
        f"neenan_role: {role}",
        "xinque_skill_candidate: true",
        "---",
        "",
        f"# {_display(point, title_en)}",
        "",
        "## 简介",
        "",
        desc,
        "",
        "## 步骤",
        "",
    ]
    for i, s in enumerate(steps, 1):
        lines.append(f"{i}. {s}")
    lines.extend(
        [
            "",
            "## 应用场景与问题",
            "",
            "**常见困扰**",
            "",
        ]
    )
    lines.extend(f"- {p}" for p in probs)
    lines.extend(["", "**相关情绪与症状**", ""])
    lines.extend(f"- {s}" for s in symp)
    lines.extend(["", "**典型情境**", ""])
    lines.extend(f"- {s}" for s in sits)
    lines.extend(["", "## 适用与禁忌", ""])
    lines.extend(f"- {n}" for n in notes)
    lines.extend(
        [
            "",
            "## 来源说明",
            "",
            "由参考书要点改写成用户可执行说明；原文见 `docs/reference/skill-cbt/extracted/neenan_epub/`。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for stale in OUT.glob("neenan_*_section.md"):
        stale.unlink()
    done: set[int] = set()
    written = 0

    for fname, point, role in TOC_MAP:
        if point in (33, 34):
            continue
        src = EXTRACTED / fname
        if not src.exists():
            print("missing toc", fname)
            continue
        title_en, snip = _extract_title_snippet(_strip_headers(src.read_text(encoding="utf-8")))
        slug = _slug(point, title_en)
        if slug in SKIP_IDS:
            continue
        (OUT / f"{slug}.md").write_text(_build_md(point, role, title_en, snip, slug), encoding="utf-8")
        done.add(point)
        written += 1

    def _spine_num(name: str) -> int:
        m = re.search(r"index_split_(\d+)", name)
        return int(m.group(1)) if m else 999

    for path in sorted(EXTRACTED.glob("spine_*.txt")):
        if _spine_num(path.name) < 61:
            continue
        raw = path.read_text(encoding="utf-8")
        for point, chunk in _split_spine_by_points(raw):
            if point <= 48:
                continue
            if point in done:
                continue
            title_en, snip = _extract_title_snippet(chunk)
            slug = _slug(point, title_en)
            role = _role_for_point(point)
            (OUT / f"{slug}.md").write_text(_build_md(point, role, title_en, snip, slug), encoding="utf-8")
            done.add(point)
            written += 1

    # Point 51：与 50 同文件，切分后应已出现；若仍未出现则补一条
    if 51 not in done:
        p063 = EXTRACTED / "spine_063_index_split_062.txt"
        if p063.exists():
            for point, chunk in _split_spine_by_points(p063.read_text(encoding="utf-8")):
                if point == 51:
                    title_en, snip = _extract_title_snippet(chunk)
                    slug = _slug(51, title_en)
                    (OUT / f"{slug}.md").write_text(
                        _build_md(51, "intervention", title_en, snip, slug), encoding="utf-8"
                    )
                    done.add(51)
                    written += 1
                    break

    missing = [n for n in range(1, 101) if n not in done and n not in (33, 34)]
    by_point: dict[int, list[Path]] = defaultdict(list)
    for p in OUT.glob("neenan_*_*.md"):
        m = re.match(r"neenan_(\d+)_", p.name)
        if m:
            by_point[int(m.group(1))].append(p)
    for _pt, paths in by_point.items():
        if len(paths) <= 1:
            continue
        paths.sort(key=lambda x: len(x.name), reverse=True)
        for p in paths[1:]:
            p.unlink()

    print("written", written, "points covered", len(done), "missing", missing)
    if missing:
        print("note: 33、34 为手工精修；其余缺失多为 EPUB 分节无独立编号或附录。")


if __name__ == "__main__":
    main()
