#!/usr/bin/env python3
"""从《CBT Made Simple》PDF 按章节导出纯文本，供后续改写成心雀 skill 或内部语料。

用法（在 skill-cbt 目录下）:
  pip install -r scripts/requirements.txt
  python scripts/export_cbt_made_simple.py
  python scripts/export_cbt_made_simple.py --detect-chapters   # 换 PDF 版时重扫 CHAPTER 页码

导出目录默认: ./extracted/（已在 .gitignore）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("请先安装: pip install -r scripts/requirements.txt", file=sys.stderr)
    raise

import yaml

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "cbt-made-simple-2e-inventory.yaml"


def _find_pdf() -> Path:
    pattern = "CBT Made Simple*.pdf"
    matches = sorted(ROOT.glob(pattern))
    if not matches:
        matches = sorted(ROOT.glob("*.pdf"))
    if not matches:
        raise FileNotFoundError(f"在 {ROOT} 未找到 PDF（期望 {pattern}）")
    return matches[0]


def detect_chapter_starts(pdf_path: Path) -> list[tuple[int, str]]:
    """返回 [(pdf_1based_page, heading_snippet), ...]"""
    reader = PdfReader(str(pdf_path))
    out: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        m = re.search(r"CHAPTER\s+(\d+)", text[:1200])
        if not m:
            continue
        tail = text[m.start() : m.start() + 180].replace("\n", " ")
        out.append((i + 1, tail.strip()))
    return out


def extract_pages(reader: PdfReader, start: int, end: int) -> str:
    """start/end 均为 PDF 1-based 闭区间页码。"""
    parts: list[str] = []
    for i in range(start - 1, min(end, len(reader.pages))):
        parts.append(reader.pages[i].extract_text() or "")
    return "\n\n".join(parts)


def load_sections() -> list[dict]:
    raw = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
    return raw["sections"]


def main() -> None:
    parser = argparse.ArgumentParser(description="导出 CBT Made Simple PDF 章节文本")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "extracted",
        help="输出目录（默认 ./extracted）",
    )
    parser.add_argument(
        "--detect-chapters",
        action="store_true",
        help="扫描 CHAPTER 标记并打印建议页码（换 PDF 版本时用）",
    )
    parser.add_argument(
        "--ids",
        nargs="*",
        help="只导出指定 id（默认导出 inventory 中全部）",
    )
    args = parser.parse_args()

    pdf_path = _find_pdf()
    reader = PdfReader(str(pdf_path))

    if args.detect_chapters:
        print(f"PDF: {pdf_path.name}，总页数 {len(reader.pages)}\n")
        for page, snippet in detect_chapter_starts(pdf_path):
            print(f"  CHAPTER @ PDF page {page}: {snippet[:90]}...")
        return

    sections = load_sections()
    if args.ids:
        want = set(args.ids)
        sections = [s for s in sections if s["id"] in want]
        missing = want - {s["id"] for s in sections}
        if missing:
            print("未知 id:", ", ".join(sorted(missing)), file=sys.stderr)
            sys.exit(1)

    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_lines = [f"source_pdf: {pdf_path.name}", f"pages_total: {len(reader.pages)}", "files:"]

    for sec in sections:
        sid = sec["id"]
        start, end = int(sec["pdf_start"]), int(sec["pdf_end"])
        if start < 1 or end > len(reader.pages):
            print(f"警告: {sid} 页范围 {start}-{end} 超出 PDF（1-{len(reader.pages)}）", file=sys.stderr)
        text = extract_pages(reader, start, end)
        header = (
            f"# {sec['title']}\n"
            f"# id: {sid}\n"
            f"# pdf_pages: {start}-{end}\n"
            f"# xinque_role: {sec.get('xinque_role', '')}\n\n"
        )
        target = out_dir / f"{sid}.txt"
        target.write_text(header + text, encoding="utf-8")
        manifest_lines.append(f"  - id: {sid}  file: {target.name}  pages: {start}-{end}")

    (out_dir / "_manifest.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"已导出 {len(sections)} 个片段 → {out_dir}")


if __name__ == "__main__":
    main()
