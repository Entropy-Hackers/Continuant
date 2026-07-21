# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""Continuant instance dashboard (v0).

Runs ALONGSIDE a single Continuant instance — one dashboard deployment per
instance, colocated with it (not a cross-instance/multi-server aggregator;
an individual instance may live on a different server from any other, so
a "see everything" view would need to pull from each instance's own
dashboard over a network API, not local bind mounts — deliberately out of
scope for this round, see docs/adr/0002).

Reads this instance's own `audit/` directory (produced by
`tools/audit-tap`) and, read-only, its `workspace/` — so the Väterrat sees
not just uptime/cron metrics but MEMORY.md, recent work/, people/,
library/, and reflection/ too. Never writes to either, and never touches
`config/`, `secrets/`, or `docker.sock`.

Single shared admin credential for v0 (no per-Vater accounts yet) — see
docs' Non-Goals for this round.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

import bcrypt
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ["DASHBOARD_SECRET_KEY"]
app.permanent_session_lifetime = timedelta(days=7)

INSTANCE_NAME = os.environ["DASHBOARD_INSTANCE_NAME"]
AUDIT_DIR = Path(os.environ.get("DASHBOARD_AUDIT_DIR", "/data/audit"))
WORKSPACE_DIR = Path(os.environ.get("DASHBOARD_WORKSPACE_DIR", "/data/workspace"))
ADMIN_PASSWORD_HASH = os.environ["DASHBOARD_ADMIN_PASSWORD_HASH"].encode("utf-8")
POLL_INTERVAL_MINUTES = int(os.environ.get("DASHBOARD_POLL_INTERVAL_MINUTES", "5"))
STALE_AFTER = timedelta(minutes=POLL_INTERVAL_MINUTES * 2)


@app.template_filter("ms_to_local")
def ms_to_local(ms: int | None) -> str:
    if not ms:
        return "—"
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


@app.template_filter("iso_to_local")
def iso_to_local(ts: str | None) -> str:
    dt = _parse_iso(ts)
    return dt.strftime("%Y-%m-%d %H:%M UTC") if dt else "—"


@app.template_filter("fmt_bytes")
def fmt_bytes(n: int | None) -> str:
    if not n:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)

    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        pw = request.form.get("password", "").encode("utf-8")
        if bcrypt.checkpw(pw, ADMIN_PASSWORD_HASH):
            session["authenticated"] = True
            session.permanent = True
            return redirect(request.args.get("next") or url_for("index"))
        error = "Falsches Passwort."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def read_instance_summary(audit_dir: Path) -> dict:
    """Single pass over events.jsonl: keep the latest snapshot of each
    non-audit_event kind, and count/timestamp audit_event lines. The file
    is small enough today to read in full per request; if that stops being
    true, this is the place to switch to a reverse/tail read."""
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

    last_poll_dt = _parse_iso(last_poll_at)
    stale = last_poll_dt is None or (datetime.now(timezone.utc) - last_poll_dt) > STALE_AFTER

    cron_jobs = []
    cron_data = snapshots.get("cron_snapshot", {}).get("data")
    if isinstance(cron_data, dict):
        cron_jobs = cron_data.get("jobs", [])

    workspace_stats = snapshots.get("workspace_stats", {}).get("data", {})

    return {
        "stale": stale,
        "last_poll_at": last_poll_at,
        "audit_event_count": audit_event_count,
        "last_audit_event_ts": last_audit_event_ts,
        "cron_jobs": cron_jobs,
        "workspace_stats": workspace_stats,
    }


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


def read_named_notes(dir_path: Path, exclude: set[str] = frozenset({"readme.md"})) -> list[dict]:
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


@app.route("/")
@login_required
def index():
    instance = {
        "name": INSTANCE_NAME,
        **read_instance_summary(AUDIT_DIR),
        **read_instance_life(WORKSPACE_DIR),
    }
    return render_template("index.html", instance=instance)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8090)
