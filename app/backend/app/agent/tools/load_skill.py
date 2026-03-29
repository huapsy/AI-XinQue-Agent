"""load_skill — P4 工具：加载干预协议

加载指定 skill.md 的完整内容，供 LLM 按流程引导用户完成干预。
"""

import json
from pathlib import Path

import yaml

from app.skill_manifest import validate_skill_manifest
from app.skill_registry import load_skill_registry

TOOL_DEFINITION = {
    "type": "function",
    "name": "load_skill",
    "description": (
        "用户选择了干预方案后调用，加载 Skill 的完整内容。"
        "返回 Skill 的目标、引入话语、分步执行流程、卡片数据、注意事项等。"
        "加载后你按 Skill 的执行流程逐步引导用户完成干预。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": "Skill 名称，如 cognitive_restructuring、breathing_478、emotion_naming",
            },
        },
        "required": ["skill_name"],
    },
}

# Skill 文件根目录
SKILLS_DIR = Path(__file__).resolve().parents[4] / "skills"


def _find_skill_file(skill_name: str) -> Path | None:
    """按名称查找 skill 文件"""
    for md_file in SKILLS_DIR.rglob("*.skill.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            end = text.index("---", 3)
            frontmatter = yaml.safe_load(text[3:end])
            if frontmatter and frontmatter.get("name") == skill_name:
                return md_file
        except Exception:
            continue
    return None


def _parse_card_data(content: str) -> dict | None:
    """从 Skill 内容中提取卡片 JSON 数据"""
    # 查找 ```json ... ``` 代码块
    start = content.find("```json")
    if start == -1:
        return None
    start += len("```json")
    end = content.find("```", start)
    if end == -1:
        return None
    try:
        return json.loads(content[start:end].strip())
    except json.JSONDecodeError:
        return None


def _build_render_payload(frontmatter: dict, skill_name: str, card_data: dict | None) -> dict | None:
    """根据 Skill frontmatter 推断 render_card 输入。"""
    if not card_data:
        return None

    card_template = frontmatter.get("card_template")
    title = card_data.get("title") or frontmatter.get("display_name")
    description = card_data.get("description")

    if card_template == "journal":
        field_map = {
            "thought_record": ["触发情境", "自动思维", "情绪强度", "支持证据", "反对证据", "替代想法"],
            "gratitude_journal": ["今天值得感恩的事 1", "今天值得感恩的事 2", "今天值得感恩的事 3"],
        }
        return {
            "card_type": "journal",
            "title": title,
            "description": description,
            "fields": field_map.get(skill_name, ["记录 1", "记录 2", "记录 3"]),
        }

    if card_template == "checklist":
        return {
            "card_type": "checklist",
            "title": title,
            "description": description,
            "items": [step.get("instruction", "") for step in card_data.get("steps", [])],
        }

    return {
        "card_type": card_data.get("type", "guided_exercise"),
        "title": title,
        "description": description,
        "steps": card_data.get("steps", []),
        "resources": card_data.get("resources", []),
        "footer": card_data.get("footer"),
    }


async def execute(arguments: dict) -> str:
    """执行 load_skill，返回 Skill 完整内容"""
    skill_name = arguments.get("skill_name", "")
    if not skill_name:
        return json.dumps({
            "status": "error",
            "tool": "load_skill",
            "error": "skill_name is required",
        }, ensure_ascii=False)

    registry = load_skill_registry()
    entry = registry.get(skill_name)
    if entry is not None:
        manifest = entry["manifest"]
        protocol = entry["protocol"]
        card_data = _parse_card_data(protocol)
        result = {
            "status": "ok",
            "tool": "load_skill",
            "skill_name": manifest.get("name"),
            "display_name": manifest.get("display_name"),
            "category": manifest.get("category"),
            "manifest": manifest,
            "protocol": protocol,
            "follow_up_rules": manifest.get("follow_up_rules", []),
            "completion_signals": manifest.get("completion_signals", []),
        }
        if card_data:
            result["card_data"] = card_data
            result["render_payload"] = _build_render_payload(manifest, skill_name, card_data)
        return json.dumps(result, ensure_ascii=False)

    skill_file = _find_skill_file(skill_name)
    if skill_file is None:
        return json.dumps(
            {
                "status": "error",
                "tool": "load_skill",
                "error": f"Skill '{skill_name}' not found",
            },
            ensure_ascii=False,
        )

    text = skill_file.read_text(encoding="utf-8")

    # 分离 frontmatter 和正文
    end = text.index("---", 3)
    frontmatter = validate_skill_manifest(yaml.safe_load(text[3:end]) or {})
    body = text[end + 3:].strip()

    # 提取卡片数据
    card_data = _parse_card_data(body)

    result = {
        "status": "ok",
        "tool": "load_skill",
        "skill_name": frontmatter.get("name"),
        "display_name": frontmatter.get("display_name"),
        "category": frontmatter.get("category"),
        "manifest": frontmatter,
        "protocol": body,
        "follow_up_rules": frontmatter.get("follow_up_rules", []),
        "completion_signals": frontmatter.get("completion_signals", []),
    }

    if card_data:
        result["card_data"] = card_data
        result["render_payload"] = _build_render_payload(frontmatter, skill_name, card_data)

    return json.dumps(result, ensure_ascii=False)
