# 0004 — Control-Queue pattern and dashboard v2 stack (FastAPI + Vue 3 + SQLite)

Date: 2026-07-21
Status: accepted

## Context

The Exposé "Achtzehn" v5 (§A.9, "Die Mündigkeit") describes a defined
transition from "nur Väterkreis" to "selbstständige Kommunikation," with
criteria, a request procedure, and the ability to revoke it after an
incident. Until this round that was purely implicit in
`channels.matrix.dm.allowFrom` — invisible anywhere, not reversible with a
button. The v0 dashboard (`docs/adr/0001`, `docs/adr/0002`) was read-only
by design; it could show that an instance existed but could not act on it.

This round's brief: make the dashboard a real control center — a visible
Mündigkeits-status, a visible contact list, and a security gateway able to
stop the agent (e.g. if it started sending hundreds of messages) — without
compromising the "dashboard never gets `docker.sock`" posture `docs/adr/0001`
already established.

## Decision 1: the Control-Queue pattern

The dashboard container gets exactly **one** write path, and it is not
`docker.sock`:

```
<instance-dir>/control/
  command.json   # written by the dashboard: {action, ...params, requested_at, requested_by}
  log.jsonl      # append-only, written by the executor: every attempt, accepted or not
  phase.json     # the one file the dashboard also writes directly (see below)
```

A host-side systemd **path unit** (`control-exec@<instance>.path`) watches
`command.json` via inotify (`PathExists=`, so it fires on the
nonexistent→existent transition) and triggers
`control-exec@<instance>.service`, which runs `tools/control-exec/control_exec.py`
as root. That script validates the request against a fixed, three-action
allow-list (`stop_channel`, `resume_channel`, `set_cron_enabled`), executes
it through the instance's own `openclaw` CLI exactly the way a human admin
would (`docker compose --profile cli run --rm openclaw-cli ...`), logs the
outcome, and deletes `command.json` — accepted or refused, so a bad or
stale request can never re-trigger.

This mirrors `tools/audit-tap`'s existing posture (host-side, root, never
mounted into any instance container) but adds the one thing audit-tap
deliberately doesn't have: the ability to act. The dashboard itself stays
exactly as unprivileged as v0 — it can request, never execute.

`phase.json` (the Mündigkeits-status) is the one exception routed
*outside* the queue: the dashboard writes it directly. Unlike the other
three actions, changing it doesn't touch any running process — it's a
status label the Väterrat maintains, not an executor action — so there's
no privilege boundary to cross. Every change is still mirrored into the
dashboard's own SQLite (`phase_history` table) for a durable "who declared
her mündig, and when" trail, matching the Exposé's framing of Mündigkeit
as a deliberate, recorded act rather than a quiet config edit.

### Implementation gotchas worth recording

- `channels remove`/`channels add` print an interactive confirmation
  prompt (`Disable Matrix account "default"? Yes/No`) regardless of TTY
  allocation, and there is no `--yes`/`--force` flag. `control_exec.py`
  disables pseudo-TTY (`docker compose run -T`) and unconditionally feeds
  `"y\n"` on stdin — harmless for calls that don't prompt.
- **`resume_channel` is `config set channels.<x>.enabled true`, not
  `channels add`.** `channels remove` (without `--delete`) only flips
  `enabled` to `false` and leaves `homeserver`/`userId`/credentials in
  config untouched — so the exact inverse is flipping it back. `channels
  add --channel matrix` looked like the obvious "re-add" call and was
  tried first; in testing against the live CGR-55 gateway it silently
  switched the account to env-var-backed credential mode and **stripped
  `homeserver`/`userId` from config**, because the required
  `MATRIX_HOMESERVER`/`MATRIX_USER_ID` env vars weren't present in the
  gateway's own `secrets/.env` (only `MATRIX_PASSWORD` was) — breaking the
  account until those two fields were restored by hand with `config set`.
  `config set channels.<x>.enabled true` touches exactly one field, hot-
  reloads without a gateway restart, and relies on the credentials already
  cached in openclaw's shared `state/openclaw.sqlite` rather than
  re-supplying them.

## Decision 2: dashboard v2 stack — FastAPI + Vue 3 + SQLite

v0 was Flask + Jinja2, server-rendered, read-only — appropriate for "a
handful of tables," as `docs/adr/0002` put it. A security gateway with
live actions and a phase-history record outgrew that: FastAPI (JSON API +
free `/docs`), Vue 3 + Pinia (a proper client for actions/state, not just
tables), SQLite (the one piece of dashboard-owned state — phase history —
that doesn't belong in `audit/events.jsonl`, which is audit-tap's, or in
`openclaw.json`, which is the instance's own).

**Deviation from the original plan: hand-written CSS instead of
Tailwind.** The plan suggested Tailwind for "zügiges, konsistentes
Design." Given the whole frontend is four views, adding the PostCSS/
Tailwind build toolchain would have meant more that could break in the
multi-stage Docker build for proportionally little gain over a single
~100-line stylesheet. Revisit if the frontend grows enough that ad-hoc CSS
stops being consistent on its own.

Build: a two-stage Dockerfile (`node:22-slim` builds `frontend/dist/`,
then `python:3.12-slim` serves both `/api/*` and that `dist/` via
`StaticFiles`) — no Node runtime in the final image, same "no new
always-on dependency beyond what's necessary" reasoning as `docs/adr/0002`.

Auth is unchanged from v0 in spirit (one shared bcrypt-hashed admin
password, see Non-Goals) but the mechanism changed to fit a stateless
JSON API: a signed, timestamped cookie (`itsdangerous`) instead of Flask's
server-side session — no session table needed for a single-operator tool.

## Decision 3 (a non-decision): automatic rate-based auto-stop is deferred

The plan called for detecting >20 outbound messages/5min and
auto-triggering `stop_channel`. Building this needs per-message send data.
Investigation before implementation found:

- `audit.messages` (the config key that would enable message-level audit
  records) and `openclaw audit --kind message` (the CLI to read them) do
  **not exist in any openclaw version released as of 2026-07-21** —
  confirmed directly against `openclaw config schema` and `openclaw audit
  --help` on `2026.7.1`, the newest tag actually published on
  `ghcr.io/openclaw/openclaw` at that date. The public docs
  (`docs.openclaw.ai`) describe this feature ahead of its release —
  attempting to enable it (`{"audit": {"messages": "all"}}`) crashed
  CGR-55's gateway (`Unrecognized key: "messages"`) and briefly tripped
  its restart-loop breaker before being reverted.
- Ordinary chat replies also aren't visible through the audit kind that
  *is* enabled by default (`tool_action`): sampling CGR-55's own audit
  history found only explicit tool calls (`read`, `edit`, `exec`,
  `web_search`, `web_fetch`, `memory_get/search`, `session_status`,
  `write`) — a normal conversational reply is not a tool call and leaves
  no trace there either.

So there is currently no data source inside openclaw to build automatic
rate detection on top of, in any version that actually ships. Rather than
build a fragile workaround (e.g. scraping the Gateway's own log file,
which has no stability contract), this is deferred: the **manual** STOP
button (via the Control-Queue's `stop_channel`, which works today,
independent of any audit data) ships now; automatic detection is revisited
once openclaw actually releases message-level audit data.

### Second-order finding, fixed opportunistically: `ghcr.io/openclaw/openclaw:latest` was stale

While chasing the above, pulling the `latest` tag to check for a newer
release that might already have `audit.messages` returned **2026.6.33** —
older than what was already running (`2026.7.1`). A `docker compose pull`
run at the wrong moment would have silently downgraded the gateway.
`compose.yaml` for CGR-55's `openclaw-gateway`/`openclaw-cli` services now
pins the explicit tag (`2026.7.1`) instead of `latest`; upgrading requires
checking `ghcr.io` for a newer explicit tag and editing that pin, not a
bare `pull`.

## Consequences

- Total new persistent processes: none beyond the dashboard container
  itself, which already existed (v0 → v2 is a rebuild, not an addition).
  `control-exec` is a systemd path-unit-triggered oneshot, same zero-idle-
  footprint shape as `audit-tap`.
- The dashboard's blast radius for a compromised/buggy frontend or backend
  is now larger than v0's (it can request channel stops/cron changes,
  not just read), but strictly bounded by `control-exec`'s fixed
  three-action allow-list — it cannot be made to run arbitrary commands
  short of a bug in `control_exec.py` itself.
- `control/`, unlike `audit/` and `workspace/`, is the one instance
  directory where the dashboard's UID (`10001`) needs actual write
  access — `root:10001 chmod 770`, documented in
  `tools/control-exec/README.md` and `body/dashboard/README.md`.
- Rate-based auto-stop remains an open item, blocked on an upstream
  openclaw release, not on anything in this repo — revisit by checking
  `openclaw config schema | grep -A3 '"audit"'` against whatever the
  current tag is.
