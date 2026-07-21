# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""Read-only helpers for an instance's own `audit/` and `workspace/` — ported
from the v0 Flask dashboard, unchanged in behavior. Never writes to either.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def read_text_safe(path: Path, max_chars: int = 20000) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    return text if len(text) <= max_chars else text[:max_chars] + "\n…(gekürzt)"


def read_memory_recent(workspace_dir: Path, limit: int = 5) -> list[dict]:
    """MEMORY.md is organized as `## YYYY-MM-DD` sections; return the last
    few, newest first."""
    text = read_text_safe(workspace_dir / "MEMORY.md")
    if not text:
        return []
    sections: list[dict] = []
    heading, body_lines = None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if heading is not None:
                sections.append({"heading": heading, "body": "\n".join(body_lines).strip()})
            heading, body_lines = line[3:].strip(), []
        elif heading is not None:
            body_lines.append(line)
    if heading is not None:
        sections.append({"heading": heading, "body": "\n".join(body_lines).strip()})
    return list(reversed(sections[-limit:]))


def read_recent_work(workspace_dir: Path, limit: int = 5) -> list[dict]:
    """Recent files directly under work/ (not work/published/, not its own
    README) — a preview of what she's actively writing, newest first."""
    work_dir = workspace_dir / "work"
    if not work_dir.exists():
        return []
    files = [
        p
        for p in work_dir.iterdir()
        if p.is_file() and p.suffix == ".md" and p.name.lower() != "readme.md"
    ]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for p in files[:limit]:
        text = read_text_safe(p, max_chars=1500) or ""
        out.append(
            {
                "name": p.name,
                "modified_iso": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
                "preview": text,
            }
        )
    return out


def read_named_notes(dir_path: Path, exclude: frozenset[str] = frozenset({"readme.md"})) -> list[dict]:
    """Generic reader for people/*.md-style small note collections."""
    if not dir_path.exists():
        return []
    notes = []
    for p in sorted(dir_path.glob("*.md")):
        if p.name.lower() in exclude:
            continue
        text = read_text_safe(p, max_chars=4000) or ""
        notes.append({"name": p.stem, "body": text})
    return notes


def read_instance_life(workspace_dir: Path) -> dict:
    return {
        "memory_recent": read_memory_recent(workspace_dir),
        "work_recent": read_recent_work(workspace_dir),
        "people": read_named_notes(workspace_dir / "people"),
        "library": read_text_safe(workspace_dir / "library" / "gelesen.md"),
        "journal": read_text_safe(workspace_dir / "reflection" / "journal.md"),
        "plan": read_text_safe(workspace_dir / "reflection" / "plan.md"),
    }


def read_instance_summary(audit_dir: Path, stale_after: timedelta) -> dict:
    """Single pass over events.jsonl: keep the latest snapshot of each
    non-audit_event kind, and count/timestamp audit_event lines."""
    events_path = audit_dir / "events.jsonl"
    cursor_path = audit_dir / "state" / "cursor.json"

    snapshots: dict[str, dict] = {}
    audit_event_count = 0
    last_audit_event_ts: str | None = None

    if events_path.exists():
        with events_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                kind = obj.get("kind")
                if kind == "audit_event":
                    audit_event_count += 1
                    last_audit_event_ts = obj.get("ts")
                elif kind:
                    snapshots[kind] = obj

    last_poll_at = None
    if cursor_path.exists():
        try:
            state = json.loads(cursor_path.read_text(encoding="utf-8"))
            last_poll_at = state.get("last_poll_at")
        except json.JSONDecodeError:
            pass

    last_poll_dt = parse_iso(last_poll_at)
    stale = last_poll_dt is None or (datetime.now(timezone.utc) - last_poll_dt) > stale_after

    cron_jobs = []
    cron_data = snapshots.get("cron_snapshot", {}).get("data")
    if isinstance(cron_data, dict):
        cron_jobs = cron_data.get("jobs", [])

    workspace_stats = snapshots.get("workspace_stats", {}).get("data", {})
    contacts = snapshots.get("contacts_snapshot", {}).get("data", {})

    return {
        "stale": stale,
        "last_poll_at": last_poll_at,
        "audit_event_count": audit_event_count,
        "last_audit_event_ts": last_audit_event_ts,
        "cron_jobs": cron_jobs,
        "workspace_stats": workspace_stats,
        "contacts": contacts,
    }
