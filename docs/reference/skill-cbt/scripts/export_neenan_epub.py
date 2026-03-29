#!/usr/bin/env python3
"""从 Neenan《Cognitive behaviour therapy: 100 key points》EPUB 导出文本。

- 按 EPUB 导航（TOC）逐条导出；若 href 含 #page_xx，则从对应锚点切段（同一 HTML 内多条要点）。
- 再导出所有「未被任何 TOC 链接引用过的」spine 文档全文，补全 TOC 未列出的要点。

用法（建议在 skill-cbt 目录下）:
  pip install -r scripts/requirements.txt
  python scripts/export_neenan_epub.py

输出: ./extracted/neenan_epub/  （父目录 extracted/ 已在 .gitignore）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "extracted" / "neenan_epub"


def _find_epub() -> Path:
    matches = sorted(ROOT.glob("Cognitive behaviour therapy*.epub"))
    if not matches:
        matches = sorted(ROOT.glob("*.epub"))
    if not matches:
        raise FileNotFoundError(f"在 {ROOT} 未找到 .epub")
    return matches[0]


def _slugify(title: str, max_len: int = 70) -> str:
    raw = re.sub(r'[<>:"/\\|?*]+', "", title)
    raw = raw.replace("\n", " ").strip()
    raw = re.sub(r"\s+", "_", raw)
    raw = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", raw, flags=re.UNICODE)
    raw = re.sub(r"_+", "_", raw).strip("_").lower()
    return (raw[:max_len] or "section").rstrip("_")


def _parse_href(href: str) -> tuple[str, str | None]:
    href = unquote(href.strip())
    if "#" in href:
        path, frag = href.split("#", 1)
        return Path(path).name, frag.strip() or None
    return Path(href).name, None


def _toc_basenames(book: epub.EpubBook) -> set[str]:
    out: set[str] = set()

    def walk(nodes):
        for node in nodes:
            if isinstance(node, epub.Link):
                base, _ = _parse_href(node.href)
                if base:
                    out.add(base)
            elif isinstance(node, tuple) and len(node) >= 2:
                href = node[1]
                if isinstance(href, str):
                    base, _ = _parse_href(href)
                    if base:
                        out.add(base)
                if len(node) > 2 and node[2]:
                    walk(node[2])

    walk(book.toc)
    return out


def _flatten_toc_links(book: epub.EpubBook) -> list[epub.Link]:
    links: list[epub.Link] = []

    def walk(nodes):
        for node in nodes:
            if isinstance(node, epub.Link):
                links.append(node)
            elif isinstance(node, tuple):
                if len(node) > 2 and node[2]:
                    walk(node[2])

    walk(book.toc)
    return links


def _html_by_basename(book: epub.EpubBook) -> dict[str, tuple[object, bytes]]:
    """basename -> (item, raw bytes)"""
    out: dict[str, tuple[object, bytes]] = {}
    for item in book.get_items():
        if item.get_type() != ITEM_DOCUMENT:
            continue
        name = item.get_name()
        base = Path(name).name
        out[base] = (item, item.get_content())
    return out


def _body_text(soup: BeautifulSoup) -> str:
    body = soup.find("body")
    root = body if body else soup
    for tag in root.find_all(["script", "style"]):
        tag.decompose()
    return root.get_text("\n", strip=True)


def _section_from_anchor(soup: BeautifulSoup, anchor: str) -> str:
    el = soup.find(id=anchor)
    if not el:
        return ""
    chunks: list[str] = [el.get_text("\n", strip=True)]
    for sib in el.find_next_siblings():
        if getattr(sib, "name", None) == "p" and (sib.get("id") or "").startswith("page_"):
            break
        if hasattr(sib, "get_text"):
            t = sib.get_text("\n", strip=True)
            if t:
                chunks.append(t)
    return "\n\n".join(chunks)


def _guess_xinque_role(title: str) -> str:
    t = title.strip()
    if t.startswith("Part ") or "Preface" in t:
        return "agent_guidance"
    if "WAYS OF DETECTING" in t.upper():
        return "formulation"
    m = re.match(r"^(\d+)\s", t)
    if m:
        n = int(m.group(1))
        if n <= 11:
            return "formulation"
        if n <= 21:
            return "psychoeducation"
        if n <= 31:
            return "session_structure"
        return "intervention"
    return "reference_only"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    epub_path = _find_epub()
    book = epub.read_epub(str(epub_path))
    html_map = _html_by_basename(book)
    toc_bases = _toc_basenames(book)
    links = _flatten_toc_links(book)

    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[str] = [
        f"source_epub: {epub_path.name}",
        "exports:",
    ]
    n = 0

    for i, link in enumerate(links):
        title = (link.title or "").strip() or f"toc_{i}"
        base, anchor = _parse_href(link.href)
        if not base or base not in html_map:
            manifest.append(f"  - skip: {title!r} missing {base}")
            continue
        _, raw = html_map[base]
        soup = BeautifulSoup(raw, "xml")
        if anchor:
            text = _section_from_anchor(soup, anchor)
            if len(text.strip()) < 80:
                text = _body_text(soup)
        else:
            text = _body_text(soup)
        if not text.strip():
            text = _body_text(soup)
        if len(text.strip()) < 30:
            manifest.append(f"  - skip_short: {title!r}")
            continue
        role = _guess_xinque_role(title)
        slug = _slugify(title)
        fname = f"toc_{i:03d}_{slug}.txt"
        header = (
            f"# {title}\n"
            f"# source: toc index {i}\n"
            f"# href: {link.href}\n"
            f"# xinque_role: {role}\n\n"
        )
        (out_dir / fname).write_text(header + text, encoding="utf-8")
        manifest.append(f"  - file: {fname}  title: {title[:80]!r}  role: {role}")
        n += 1

    # Spine orphans: document-level files never referenced by TOC basename
    spine_manifest: list[str] = ["spine_orphans:"]
    o = 0
    for idx, (item_id, _linear) in enumerate(book.spine):
        item = book.get_item_with_id(item_id)
        if not item or item.get_type() != ITEM_DOCUMENT:
            continue
        base = Path(item.get_name()).name
        if base in toc_bases:
            continue
        raw = item.get_content()
        soup = BeautifulSoup(raw, "xml")
        text = _body_text(soup)
        if len(text.strip()) < 80:
            spine_manifest.append(f"  - skip_short: {base}")
            continue
        fname = f"spine_{idx:03d}_{Path(base).stem}.txt"
        header = (
            f"# spine orphan: {base}\n"
            f"# spine_index: {idx}\n"
            f"# xinque_role: reference_only\n\n"
        )
        (out_dir / fname).write_text(header + text, encoding="utf-8")
        spine_manifest.append(f"  - file: {fname}  html: {base}")
        o += 1
        n += 1

    (out_dir / "_neenan_manifest.txt").write_text(
        "\n".join(manifest + ["", *spine_manifest, "", f"total_files: {n}"]) + "\n",
        encoding="utf-8",
    )
    print(f"EPUB: {epub_path.name}")
    print(f"TOC 导出: {len(links)} 条链接（已跳过过短/缺文件）→ 见 manifest")
    print(f"Spine 补全: {o} 个未在 TOC 出现的 HTML")
    print(f"输出目录: {out_dir}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
