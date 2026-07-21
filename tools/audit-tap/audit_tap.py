#!/usr/bin/env python3
# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""Audit tap for a Continuant instance.

Polls a running openclaw Gateway through its own CLI (`docker compose
--profile cli run --rm openclaw-cli ...`) and appends normalized,
metadata-only records to an append-only JSONL file OUTSIDE the instance's
own container/workspace — never mounted into openclaw-gateway.

This does not invent a new event model: `openclaw audit --json` already
returns the append-only, sequence-numbered, metadata-only event log the
Continuant docs describe as the "audit-logger" / Beobachtungsschicht. This
script's only job is to poll it (and a few status snapshots) on a timer and
persist the results where the agent itself can never read them.

Usage:
    audit_tap.py --instance-dir /opt/continuants/instances/CGR-55 \\
                  [--compose-dir <dir, default = instance-dir>] \\
                  [--instance-name <name, default = instance-dir basename>]

Intended to run via a systemd timer (see systemd/audit-tap@.service and
.timer in this directory), not as a long-running daemon.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cli(compose_dir: Path, args: list[str], timeout: int = 90) -> Any | None:
    """Run an openclaw CLI subcommand via the instance's own compose file and
    parse its JSON output. `docker compose run` prints status lines
    ("Container ... Running" etc.) before the actual command output, so we
    scan for the first line that looks like the start of a JSON value."""
    cmd = ["docker", "compose", "--profile", "cli", "run", "--rm", "openclaw-cli", *args]
    try:
        proc = subprocess.run(
            cmd, cwd=compose_dir, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        print(f"[audit-tap] timeout running: {' '.join(args)}", file=sys.stderr)
        return None
    if proc.returncode != 0:
        print(
            f"[audit-tap] exit {proc.returncode} running: {' '.join(args)}\n{proc.stderr.strip()}",
            file=sys.stderr,
        )
        return None
    lines = proc.stdout.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("{") or s.startswith("["):
            candidate = "\n".join(lines[i:])
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    print(f"[audit-tap] no JSON found in output of: {' '.join(args)}", file=sys.stderr)
    return None


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_state(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def poll_audit_events(compose_dir: Path, events_path: Path, instance: str, state: dict) -> int:
    """`openclaw audit --json` pages BACKWARD from the newest event
    (nextCursor continues further into the past). We fetch the newest page,
    then keep paging back only as far as needed to reach the highest
    sequence number we've already recorded, so nothing is missed and
    nothing is duplicated between polls."""
    last_seen = state.get("audit_last_seen_sequence")
    cursor: int | None = None
    collected: list[dict] = []
    max_seq_this_poll: int | None = None

    while True:
        args = ["audit", "--json", "--limit", "500"]
        if cursor is not None:
            args += ["--cursor", str(cursor)]
        page = run_cli(compose_dir, args)
        if not page:
            break
        events = page.get("events") or []
        if not events:
            break
        if max_seq_this_poll is None:
            max_seq_this_poll = events[0]["sequence"]

        reached_known = False
        for ev in events:
            if last_seen is not None and ev["sequence"] <= last_seen:
                reached_known = True
                break
            collected.append(ev)
        if reached_known:
            break

        next_cursor = page.get("nextCursor")
        if next_cursor is None or next_cursor == cursor:
            break
        cursor = next_cursor

    # collected is newest-first; write oldest-first for a naturally ordered log.
    for ev in reversed(collected):
        append_jsonl(
            events_path,
            {"ts": now_iso(), "instance": instance, "kind": "audit_event", "data": ev},
        )
    if max_seq_this_poll is not None:
        state["audit_last_seen_sequence"] = max_seq_this_poll
    return len(collected)


def poll_snapshot(
    compose_dir: Path, events_path: Path, instance: str, kind: str, cli_args: list[str]
) -> bool:
    data = run_cli(compose_dir, cli_args)
    if data is None:
        return False
    append_jsonl(events_path, {"ts": now_iso(), "instance": instance, "kind": kind, "data": data})
    return True


def poll_workspace_stats(instance_dir: Path, events_path: Path, instance: str) -> None:
    """Reads workspace/ from the HOST side, purely for size/activity
    metadata. This is the observer looking in, not the agent looking at
    its own audit trail — it never writes anything back."""
    workspace = instance_dir / "workspace"
    stats: dict[str, dict] = {}
    for sub in ("work", "library", "reflection"):
        d = workspace / sub
        if not d.exists():
            continue
        files = [p for p in d.rglob("*") if p.is_file()]
        stats[sub] = {
            "file_count": len(files),
            "total_bytes": sum(p.stat().st_size for p in files),
            "last_modified_iso": (
                datetime.fromtimestamp(
                    max(p.stat().st_mtime for p in files), tz=timezone.utc
                ).isoformat()
                if files
                else None
            ),
        }
    append_jsonl(
        events_path,
        {"ts": now_iso(), "instance": instance, "kind": "workspace_stats", "data": stats},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance-dir", required=True, type=Path)
    parser.add_argument("--compose-dir", type=Path, default=None)
    parser.add_argument("--instance-name", default=None)
    args = parser.parse_args()

    instance_dir = args.instance_dir.resolve()
    compose_dir = (args.compose_dir or instance_dir).resolve()
    instance = args.instance_name or instance_dir.name

    audit_dir = instance_dir / "audit"
    events_path = audit_dir / "events.jsonl"
    state_path = audit_dir / "state" / "cursor.json"

    state = load_state(state_path)

    n_events = poll_audit_events(compose_dir, events_path, instance, state)
    poll_snapshot(compose_dir, events_path, instance, "cron_snapshot", ["cron", "list", "--json", "--all"])
    poll_snapshot(compose_dir, events_path, instance, "sessions_snapshot", ["sessions", "--json", "--all-agents"])
    poll_snapshot(compose_dir, events_path, instance, "status_snapshot", ["status", "--json", "--usage"])
    poll_workspace_stats(instance_dir, events_path, instance)

    state["last_poll_at"] = now_iso()
    save_state(state_path, state)

    print(f"[audit-tap] {instance}: {n_events} new audit event(s), poll complete at {state['last_poll_at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
