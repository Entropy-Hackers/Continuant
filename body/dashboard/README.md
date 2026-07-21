# Continuant instance dashboard (v2)

Control center for a single Continuant instance, meant for the trusted
circle ("Väter"): audit-tap health, cron runs, workspace size, the
Mündigkeits-Phase, the currently allowed contact list — plus the more
human side, read-only from `workspace/`: recent `MEMORY.md` entries,
what's being written in `work/`, `people/` notes, the reading list, and
reflection journal/plan.

v0 was a read-only Flask/Jinja2 app. v2 is a **FastAPI backend + Vue 3
frontend + SQLite**, and adds one deliberate write path — the Control-
Queue — so this can act as a real security gateway: stop a channel live,
pause a cron job, or record a Mündigkeits-phase change, without ever
holding `docker.sock`. See `docs/adr/0004`.

Runs **alongside** that one instance, not as a cross-instance aggregator:
an instance may live on a different server from any other, so a "see
everything" view is a separate, later concern (would need each instance's
dashboard to expose an API for a higher-level view to pull from — not
local bind mounts).

## What it reads / writes

| path | mode | source |
|---|---|---|
| `audit/` | ro | `tools/audit-tap` |
| `workspace/` | ro | the instance's own container |
| `control/command.json` | **write** (the one exception) | consumed by `tools/control-exec`, never executed by this container itself |
| `control/phase.json` | read + write | this is the one file the dashboard edits directly (see below) |
| `control/log.jsonl` | ro | written by `tools/control-exec` |
| `db/dashboard.sqlite3` | read + write | private to this container; phase-change history only |

Never touches `config/`, `secrets/`, or `docker.sock`. `phase.json` is the
one config-like file the dashboard writes directly rather than going
through the Control-Queue — it's a status label the Väterrat maintains,
not an action against a running process, so there's no executor step to
route through. Every write is still mirrored into `db/dashboard.sqlite3`'s
`phase_history` table so there's a durable "who declared her mündig, and
when" trail (Exposé A.9).

## Architecture

```
backend/    FastAPI — reading.py (audit/workspace), control.py (Control-
            Queue writer + phase.json), db.py (SQLite phase history),
            auth.py (bcrypt + signed cookie), main.py (routes, serves the
            built frontend as static files)
frontend/   Vue 3 + Pinia, plain CSS (no Tailwind — kept the Docker build
            simpler; four tabs: Übersicht, Kontakte, Leben, Einstellungen)
Dockerfile  multi-stage: node:22-slim builds frontend/dist/, then a
            python:3.12-slim image serves both /api/* and that dist/ —
            no Node runtime in the final image
```

## Deploy (one per instance)

Real deployments are a sibling of the instance directory, e.g. for an
instance `CGR-55` at `/opt/continuants/instances/CGR-55/`:

```bash
mkdir -p /opt/continuants/instances/CGR-55/dashboard/secrets
mkdir -p /opt/continuants/instances/CGR-55/dashboard/db
cp compose.yaml /opt/continuants/instances/CGR-55/dashboard/
cp secrets/.env.example /opt/continuants/instances/CGR-55/dashboard/secrets/.env
```

In the copied `compose.yaml`: set `build:` to this repo directory's
absolute path, replace `INSTANCE_NAME` with the real instance name, and
pick a host port (127.0.0.1 only) if running dashboards for more than one
instance on the same host.

In `secrets/.env`, fill in:
- `DASHBOARD_SECRET_KEY`: `openssl rand -hex 32`
- `DASHBOARD_ADMIN_PASSWORD_HASH`: bcrypt hash of a chosen admin password
  (`python3 -c "import bcrypt; print(bcrypt.hashpw(b'...', bcrypt.gensalt()).decode())"`).
  **Escape every literal `$` as `$$`** — `docker compose` interpolates
  `$VAR` inside `env_file` values, and a bcrypt hash is almost entirely
  `$`-delimited fields; an unescaped hash gets silently corrupted and
  login fails with `ValueError: Invalid salt`.

### Permissions

`audit/` (created `root:root chmod 700` by `tools/audit-tap`),
`workspace/` (owned by the instance's container UID, usually `1000:1000`),
and `control/` (created `root:10001 chmod 770` — see
`tools/control-exec/README.md`) all default to blocking every other user,
including the dashboard's fixed non-root UID/GID (`10001`, set in this
directory's `Dockerfile`). Grant group access narrowly instead of
loosening any of them for everyone:

```bash
chown root:10001 /opt/continuants/instances/<NAME>/audit
chmod 750 /opt/continuants/instances/<NAME>/audit
chown <owner-uid>:10001 /opt/continuants/instances/<NAME>/workspace
chmod 750 /opt/continuants/instances/<NAME>/workspace
chown root:10001 /opt/continuants/instances/<NAME>/control
chmod 770 /opt/continuants/instances/<NAME>/control
chown -R 10001:10001 /opt/continuants/instances/<NAME>/dashboard/db
```

(`<owner-uid>` is whatever already owns `workspace/` — changing the
*group* only, never the owner, keeps the instance's own container's
read-write access untouched. `control/` and `dashboard/db/` are the two
exceptions where the dashboard's UID genuinely needs write access.)

Then, from the instance's `dashboard/` directory: `docker compose up -d --build`

## Exposing it

Two patterns, both proven against CGR-55; use either or both.

### Tailscale-only (stricter)

Same mechanism already used for openclaw's own Control UI on this host —
HTTPS via `tailscale serve`, bound to loopback only. Give the dashboard
its **own port**, not a path under the same origin as another app: a
path-based split (`--set-path /dashboard`) was tried first and broke,
apparently because the other app's frontend claims the whole origin
(service-worker-style route capture is the leading suspect, unconfirmed)
— every path under that origin landed back on the other app's UI.

```bash
tailscale serve --bg --https=8443 http://127.0.0.1:8090
```

Reachable at `https://<host>.<tailnet>.ts.net:8443/` within the tailnet
only.

### Public, password-gated (simpler URL)

If a normal domain is available (e.g. the same one a Continuant's public
site lives under), join the instance's shared `ops_net` (see
`compose.yaml`'s network block — declare `ops_net: { external: true }`)
so an already-running Caddy can `reverse_proxy` to the dashboard
container by name, and add one vhost block plus a DNS record. Network
placement isn't the access control here — the dashboard's own password
is. Reasonable for a small trusted-circle tool; if this needs to be
harder to brute-force later, add rate-limiting to `/api/login` (not
present in v2 either).

## v2 scope / non-goals

One shared admin password per instance (no per-Vater accounts yet), no
login rate-limiting, no live `docker ps` polling, no cross-instance/
cross-server aggregation (see `docs/adr/0001` and `docs/adr/0002`).
**No automatic rate-based auto-stop**: it would need per-message send
audit data, and neither `openclaw audit --kind message` nor the
`audit.messages` config key exist in any openclaw version released as of
2026-07-21 (checked against the newest published tag, `2026.7.1`) — the
public docs describe this ahead of release. The manual STOP button (via
the Control-Queue) works today regardless; automatic rate detection is
deferred until openclaw ships that data. See `docs/adr/0004`.
