#!/usr/bin/env python3
# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""Static site generator for a Continuant instance's published work.

Reads Markdown files with YAML frontmatter from
`<instance-dir>/workspace/work/published/*.md` and renders them to plain
static HTML in `<instance-dir>/public/dist/` — an index page plus one page
per piece. Only files explicitly placed in `published/` by an admin (or,
once Mündigkeit/the Werk-Gateway exist, the instance itself) are ever
included; nothing else under `work/` is read or exposed.

Requires: python3-markdown, python3-jinja2, python3-yaml (all available as
Debian/Ubuntu apt packages — no pip/venv needed).

Usage:
    build_site.py --instance-dir /opt/continuants/instances/CGR-55 \\
                   [--instance-name <name>] [--out <dir>]

Intended to run via a daily systemd timer (idempotent — a no-op rebuild
when published/ is unchanged) or manually after opting a new piece in.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?(.*)$", re.DOTALL)


@dataclass
class Piece:
    title: str
    date: str
    slug: str
    summary: str
    html: str
    source_name: str


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw_fm, body = m.groups()
    try:
        meta = yaml.safe_load(raw_fm) or {}
    except yaml.YAMLError as e:
        print(f"[publish] warning: could not parse frontmatter: {e}", file=sys.stderr)
        meta = {}
    if not isinstance(meta, dict):
        meta = {}
    return meta, body


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "untitled"


def load_pieces(published_dir: Path) -> list[Piece]:
    pieces: list[Piece] = []
    for path in sorted(published_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        title = str(meta.get("title") or path.stem)
        date = str(meta.get("date") or "")
        slug = str(meta.get("slug") or slugify(title))
        summary = str(meta.get("summary") or "")
        html = markdown.markdown(body, extensions=["extra", "smarty"])
        pieces.append(
            Piece(title=title, date=date, slug=slug, summary=summary, html=html, source_name=path.name)
        )
    # Newest first when `date` is an ISO-ish sortable string; ties keep filename order.
    pieces.sort(key=lambda p: p.date, reverse=True)
    return pieces


def render_site(pieces: list[Piece], instance_name: str, out_dir: Path, template_dir: Path) -> None:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
    )

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    index_tmpl = env.get_template("index.html")
    (out_dir / "index.html").write_text(
        index_tmpl.render(instance_name=instance_name, pieces=pieces), encoding="utf-8"
    )

    piece_tmpl = env.get_template("piece.html")
    for piece in pieces:
        (out_dir / f"{piece.slug}.html").write_text(
            piece_tmpl.render(instance_name=instance_name, piece=piece), encoding="utf-8"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance-dir", required=True, type=Path)
    parser.add_argument("--instance-name", default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    instance_dir = args.instance_dir.resolve()
    instance_name = args.instance_name or instance_dir.name
    published_dir = instance_dir / "workspace" / "work" / "published"
    out_dir = (args.out or instance_dir / "public" / "dist").resolve()
    template_dir = Path(__file__).parent / "templates"

    if not published_dir.exists():
        print(f"[publish] no published/ directory at {published_dir}, nothing to do")
        return 0

    pieces = load_pieces(published_dir)
    render_site(pieces, instance_name, out_dir, template_dir)
    print(f"[publish] {instance_name}: rendered {len(pieces)} piece(s) to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
