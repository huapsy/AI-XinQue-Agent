"""Skill registry: 统一加载与索引 skill manifest / protocol。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from app.skill_manifest import validate_skill_manifest


SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"


def _split_skill_document(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("skill document missing frontmatter")
    end = text.index("---", 3)
    frontmatter = yaml.safe_load(text[3:end]) or {}
    body = text[end + 3:].strip()
    return frontmatter, body


def build_skill_registry() -> dict[str, dict]:
    """扫描 skill 文件并构建标准化 registry。"""
    registry: dict[str, dict] = {}
    for skill_file in SKILLS_DIR.rglob("*.skill.md"):
        text = skill_file.read_text(encoding="utf-8")
        frontmatter, body = _split_skill_document(text)
        manifest = validate_skill_manifest(frontmatter)
        registry[manifest["name"]] = {
            "manifest": manifest,
            "protocol": body,
            "raw_text": text,
            "path": str(skill_file),
        }
    return registry


@lru_cache(maxsize=1)
def load_skill_registry() -> dict[str, dict]:
    """缓存加载 skill registry。"""
    return build_skill_registry()
