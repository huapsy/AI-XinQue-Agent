"""load_skill — P4 工具：加载干预协议

加载指定 skill.md 的完整内容，供 LLM 按流程引导用户完成干预。
"""

import json
from pathlib import Path

import yaml

TOOL_DEFINITION = {
    "type": "function",
    "function": {
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


async def execute(arguments: dict) -> str:
    """执行 load_skill，返回 Skill 完整内容"""
    skill_name = arguments.get("skill_name", "")
    if not skill_name:
        return json.dumps({"error": "skill_name is required"}, ensure_ascii=False)

    skill_file = _find_skill_file(skill_name)
    if skill_file is None:
        return json.dumps(
            {"error": f"Skill '{skill_name}' not found"},
            ensure_ascii=False,
        )

    text = skill_file.read_text(encoding="utf-8")

    # 分离 frontmatter 和正文
    end = text.index("---", 3)
    frontmatter = yaml.safe_load(text[3:end])
    body = text[end + 3:].strip()

    # 提取卡片数据
    card_data = _parse_card_data(body)

    result = {
        "skill_name": frontmatter.get("name"),
        "display_name": frontmatter.get("display_name"),
        "category": frontmatter.get("category"),
        "output_type": frontmatter.get("output_type"),
        "content": body,
    }

    if card_data:
        result["card_data"] = card_data

    return json.dumps(result, ensure_ascii=False)
