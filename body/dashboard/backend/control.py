# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""The dashboard's one write path: `<instance-dir>/control/`.

The dashboard writes `command.json`; it never executes anything itself and
never touches `docker.sock`. A host-side root process (`tools/control-exec`,
outside this container) is the only thing that acts on the request — see
docs/adr/0004. This module also reads `control/phase.json` and
`control/log.jsonl`, which control-exec (and, for phase, this dashboard's
own PUT /api/phase handler) write.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_CHANNELS = {
    "telegram", "whatsapp", "discord", "irc", "googlechat", "slack", "signal",
    "imessage", "feishu", "nostr", "msteams", "mattermost", "nextcloud-talk",
    "matrix", "raft", "line", "zalo", "clickclack", "zalouser", "sms",
    "synology-chat", "tlon", "qa-channel", "qqbot", "twitch",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ControlQueueBusy(Exception):
    """A command is already queued and not yet picked up by control-exec."""


def write_command(control_dir: Path, command: dict) -> None:
    command_path = control_dir / "command.json"
    if command_path.exists():
        raise ControlQueueBusy(
            "a previous control command is still pending — wait for it to be processed"
        )
    control_dir.mkdir(parents=True, exist_ok=True)
    command_path.write_text(json.dumps(command, ensure_ascii=False), encoding="utf-8")


def request_stop_channel(control_dir: Path, channel: str, requested_by: str) -> None:
    if channel not in ALLOWED_CHANNELS:
        raise ValueError(f"unknown channel {channel!r}")
    write_command(control_dir, {
        "action": "stop_channel", "channel": channel,
        "requested_at": now_iso(), "requested_by": requested_by,
    })


def request_resume_channel(control_dir: Path, channel: str, requested_by: str) -> None:
    if channel not in ALLOWED_CHANNELS:
        raise ValueError(f"unknown channel {channel!r}")
    write_command(control_dir, {
        "action": "resume_channel", "channel": channel,
        "requested_at": now_iso(), "requested_by": requested_by,
    })


def request_set_cron_enabled(control_dir: Path, job_id: str, enabled: bool, requested_by: str) -> None:
    if not job_id:
        raise ValueError("missing job_id")
    write_command(control_dir, {
        "action": "set_cron_enabled", "job_id": job_id, "enabled": enabled,
        "requested_at": now_iso(), "requested_by": requested_by,
    })


def read_phase(control_dir: Path) -> dict | None:
    path = control_dir / "phase.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_phase(control_dir: Path, phase: str, notes: str) -> dict:
    """The dashboard is allowed to edit phase.json directly (unlike channel/
    cron actions, this touches no running process — it's a status label the
    Väterrat maintains, not an executor action), but every change is also
    recorded in dashboard.sqlite3's phase_history (see db.py) so there's an
    audit trail of who declared the instance mündig and when."""
    doc = {"phase": phase, "since": now_iso()[:10], "notes": notes}
    path = control_dir / "phase.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return doc


def tail_log(control_dir: Path, limit: int = 50) -> list[dict]:
    path = control_dir / "log.jsonl"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    out.reverse()  # newest first
    return out
