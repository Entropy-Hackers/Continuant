#!/usr/bin/env python3
# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""Control-Queue executor for a Continuant instance.

The one deliberate exception to "the dashboard never writes": a dashboard
may write `<instance-dir>/control/command.json` to request one of a small,
fixed set of actions. This script — host-side, run as root, triggered by a
systemd path unit watching that file — is the only thing that actually
executes those actions, via the instance's own `openclaw` CLI
(`docker compose --profile cli run --rm openclaw-cli ...`). The dashboard
container itself never gets `docker.sock`.

Allowed actions (anything else is rejected and logged as such):
  stop_channel    {"action": "stop_channel", "channel": "matrix"}
  resume_channel  {"action": "resume_channel", "channel": "matrix"}
  set_cron_enabled {"action": "set_cron_enabled", "job_id": "...", "enabled": true}

Every attempt (accepted or rejected) is appended to
`<instance-dir>/control/log.jsonl`. `command.json` is removed after
processing (successful or not) so the same request never re-triggers, and a
`.processing` lock file prevents a second concurrent run from racing it.

Usage:
    control_exec.py --instance-dir /opt/continuants/instances/CGR-55 \\
                     [--compose-dir <dir, default = instance-dir>]
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


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def run_cli(compose_dir: Path, args: list[str], timeout: int = 90) -> tuple[bool, str]:
    # -T: no pseudo-TTY (we're not interactive); some subcommands (channels
    # remove/add) still print a confirmation prompt regardless, so feed
    # "y\n" on stdin rather than relying on a --yes flag that doesn't exist.
    cmd = ["docker", "compose", "--profile", "cli", "run", "--rm", "-T", "openclaw-cli", *args]
    try:
        proc = subprocess.run(
            cmd, cwd=compose_dir, capture_output=True, text=True, timeout=timeout, input="y\n"
        )
    except subprocess.TimeoutExpired:
        return False, f"timeout running: {' '.join(args)}"
    ok = proc.returncode == 0
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    detail = out if ok else (err or out or f"exit {proc.returncode}")
    return ok, detail[-4000:]  # bounded: log stays a log, not a dump


ALLOWED_CHANNELS = {
    "telegram", "whatsapp", "discord", "irc", "googlechat", "slack", "signal",
    "imessage", "feishu", "nostr", "msteams", "mattermost", "nextcloud-talk",
    "matrix", "raft", "line", "zalo", "clickclack", "zalouser", "sms",
    "synology-chat", "tlon", "qa-channel", "qqbot", "twitch",
}


def do_stop_channel(compose_dir: Path, command: dict) -> tuple[bool, str]:
    channel = command.get("channel")
    if channel not in ALLOWED_CHANNELS:
        return False, f"refused: unknown channel {channel!r}"
    return run_cli(compose_dir, ["channels", "remove", "--channel", channel])


def do_resume_channel(compose_dir: Path, command: dict) -> tuple[bool, str]:
    channel = command.get("channel")
    if channel not in ALLOWED_CHANNELS:
        return False, f"refused: unknown channel {channel!r}"
    # `channels remove` (without --delete) only flips <channel>.enabled to
    # false; homeserver/userId/credentials stay in config untouched. So the
    # exact inverse is flipping it back — NOT `channels add`, which (at
    # least for Matrix) can silently switch the account into env-var-backed
    # credential mode and strip homeserver/userId from config if the
    # matching MATRIX_HOMESERVER/MATRIX_USER_ID env vars aren't already
    # present, breaking the account. Confirmed via manual test on CGR-55
    # 2026-07-21; see docs/adr/0004.
    return run_cli(compose_dir, ["config", "set", f"channels.{channel}.enabled", "true"])


def do_set_cron_enabled(compose_dir: Path, command: dict) -> tuple[bool, str]:
    job_id = command.get("job_id")
    enabled = command.get("enabled")
    if not job_id or not isinstance(job_id, str):
        return False, "refused: missing job_id"
    if not isinstance(enabled, bool):
        return False, "refused: enabled must be true/false"
    flag = "--enable" if enabled else "--disable"
    return run_cli(compose_dir, ["cron", "edit", job_id, flag])


ACTIONS = {
    "stop_channel": do_stop_channel,
    "resume_channel": do_resume_channel,
    "set_cron_enabled": do_set_cron_enabled,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance-dir", required=True, type=Path)
    parser.add_argument("--compose-dir", type=Path, default=None)
    args = parser.parse_args()

    instance_dir = args.instance_dir.resolve()
    compose_dir = (args.compose_dir or instance_dir).resolve()
    control_dir = instance_dir / "control"
    command_path = control_dir / "command.json"
    log_path = control_dir / "log.jsonl"
    lock_path = control_dir / ".processing"

    if not command_path.exists():
        return 0  # nothing to do; path unit fired on an unrelated touch

    if lock_path.exists():
        print("[control-exec] already processing, skipping", file=sys.stderr)
        return 0

    lock_path.write_text(now_iso(), encoding="utf-8")
    try:
        try:
            raw = command_path.read_text(encoding="utf-8")
            command: Any = json.loads(raw)
        except (OSError, json.JSONDecodeError) as e:
            append_jsonl(log_path, {
                "ts": now_iso(), "command": None, "accepted": False,
                "result": f"could not read/parse command.json: {e}",
            })
            command_path.unlink(missing_ok=True)
            return 1

        action = command.get("action") if isinstance(command, dict) else None
        handler = ACTIONS.get(action)
        if handler is None:
            ok, detail = False, f"refused: unknown action {action!r}"
        else:
            ok, detail = handler(compose_dir, command)

        append_jsonl(log_path, {
            "ts": now_iso(),
            "command": command,
            "accepted": ok,
            "result": detail,
        })
        print(f"[control-exec] {action}: {'ok' if ok else 'FAILED'} — {detail[:200]}")

        # Always remove: a rejected/failed command must not re-trigger on
        # the next unrelated write to the control/ directory.
        command_path.unlink(missing_ok=True)
        return 0 if ok else 1
    finally:
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
