# audit-tap

Polls a running Continuant instance's own openclaw Gateway (via its CLI,
`docker compose --profile cli run --rm openclaw-cli ...`) and appends
normalized, metadata-only records to `<instance-dir>/audit/events.jsonl` —
a location that is **never** bind-mounted into the instance's own
`openclaw-gateway` container (Single-Blind: the observation layer must stay
unreadable to the host itself).

It does not invent a new event model. `openclaw audit --json` already
returns exactly the append-only, sequence-numbered, metadata-only log the
architecture docs describe as the audit-logger / Beobachtungsschicht
(`docs/de/01-architektur.md` §12, `docs/de/90-runbook-erste-instanz.md`
§10). This script's only job is to poll it — plus a few cheap status
snapshots — on a timer, and persist the result somewhere the agent can't
reach.

## What it captures per poll

| kind | source |
|---|---|
| `audit_event` | `openclaw audit --json` (paged back only as far as needed to catch up since the last poll) |
| `cron_snapshot` | `openclaw cron list --json --all` |
| `sessions_snapshot` | `openclaw sessions --json --all-agents` |
| `status_snapshot` | `openclaw status --json --usage` |
| `contacts_snapshot` | `openclaw config get channels --json` — the configured contact allowlists (e.g. `channels.matrix.dm.allowFrom`), no secrets |
| `workspace_stats` | host-side file counts/sizes/mtimes under `workspace/{work,library,reflection}` — read-only, from the observer side, never written back |

`message_activity` (per-window outbound send counts, for rate-based
auto-stop) is **not** captured: it would need `openclaw audit --kind
message` and `audit.messages` in `openclaw.json`, neither of which exist in
any openclaw version released as of 2026-07-21 (checked directly against
the newest published tag, `2026.7.1`, via `openclaw config schema` and
`openclaw audit --help` — the public docs describe this ahead of release).
See `docs/adr/0004`.

Cursor/dedup state lives in `<instance-dir>/audit/state/cursor.json`.

## Install for an instance

Requires Python 3 (stdlib only, no dependencies) and `docker compose` on the
host. Copy (or symlink) the two systemd template units and enable a timer
instance per Continuant, e.g. for an instance named `CGR-55` living at
`/opt/continuants/instances/CGR-55`:

```bash
sudo cp systemd/audit-tap@.service systemd/audit-tap@.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now audit-tap@CGR-55.timer
```

The `%i` instance name must match the instance's directory name under
`/opt/continuants/instances/`.

Run once manually to verify before enabling the timer:

```bash
python3 audit_tap.py --instance-dir /opt/continuants/instances/CGR-55
```

## Permissions

`<instance-dir>/audit/` should be created `root:root`, `chmod 700` before
first run — belt-and-suspenders on top of it never being mounted into the
instance's own container.

If this instance also gets a `body/dashboard/` deployment, see that
directory's README for the group-read permission steps it needs on both
this directory and `workspace/`.
