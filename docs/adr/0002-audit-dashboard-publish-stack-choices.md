# 0002 — Stack and deployment-topology choices for audit-tap, dashboard, publish

Date: 2026-07-21
Status: accepted

## Context

CGR-55 runs on a shared 2 vCPU / 4 GB Virtuozzo/OpenVZ vServer alongside
`/opt/ops` (Caddy, Forgejo, Conduit — three already-running containers)
and openclaw's own gateway container. Whatever these three pieces need
must fit that budget and must not put CGR-55's already-working setup at
risk.

## Decisions

### audit-tap: Python 3 stdlib + systemd timer, not a daemon

No new dependencies (`json`/`subprocess`/`pathlib`/`datetime` only), no
persistent process, no Docker container, no `docker.sock` access — it
shells out to `docker compose --profile cli run --rm openclaw-cli ...`
exactly the way a human admin already does. Matches the host's existing
systemd-timer idiom (there is no `cron` installed) and avoids adding a
fourth always-on container to an already-tight host.

`openclaw audit --json --cursor <n>` already returns an append-only,
sequence-numbered, metadata-only event log — this *is* the
Beobachtungsschicht primitive the docs describe. The tap's only job is to
page through it (newest-first pagination, so the tap pages backward only
as far as needed to catch up since the last poll) and persist results
outside the instance's own container.

### dashboard: Flask + Jinja2 in Docker, one deployment per instance

**Revision during this round:** the first draft of this ADR (and the
first working deployment) put one dashboard under
`/opt/continuants/foundation/dashboard/`, bind-mounting *every* known
instance's `audit/` directory to show a cross-instance overview. This was
wrong and was corrected before shipping: a Continuant instance is not
guaranteed to live on the same server as any other — GLD-18, when it
exists, may run on entirely different hardware. A design that assumes
same-host bind-mount access to "all instances" breaks the moment that
stops being true.

The corrected shape: **one dashboard container per instance, deployed as
that instance's own sibling** (`/opt/continuants/instances/CGR-55/dashboard/`),
mounting only that instance's own `audit/` directory. A future
cross-instance/cross-server overview is a distinct, later concern that
would need each instance's dashboard to expose a small API for a
higher-level view to pull from — not local bind mounts. Deliberately not
built this round.

Server-rendered HTML (no JS build step) because the whole app is a
handful of read-only tables — a build pipeline would be pure overhead
here. Docker (unlike the tap) because it's a persistent process and
benefits from Docker's restart/isolation semantics the host already
relies on for every other service.

Data access is least-privilege: a single read-only bind mount of that
one instance's `audit/` directory, nothing else. No `docker.sock` — the
dashboard infers instance liveness from audit-tap output freshness
(`state/cursor.json` mtime), not from live `docker ps`, so it never needs
container-management privileges at all.

Auth v0 is one shared bcrypt-hashed admin password per instance (no
per-Vater accounts) — see Non-Goals. Exposed only via `tailscale serve`
on the host, on its own HTTPS port rather than a path under the same
origin as openclaw's own Control UI: a path-based split
(`/dashboard/CGR-55`) was tried first and broke, apparently because
openclaw's own frontend claims the whole origin (service-worker-style
route capture is the leading suspect, unconfirmed) — every path under
`https://<host>.<tailnet>.ts.net/` landed back on openclaw's UI. Moving
the dashboard to its own port (`https://<host>.<tailnet>.ts.net:8443/`)
gives it a genuinely separate browser origin and sidesteps the issue
entirely, at the cost of one extra port per instance dashboard on a
shared host.

**Operational gotcha worth recording:** `docker compose`'s `env_file:`
loading interpolates `$VAR`/`${VAR}` inside values. A bcrypt hash
(`$2b$12$...`) is made almost entirely of `$`-delimited fields, so an
unescaped hash in `secrets/.env` gets silently corrupted (undefined
`$variableName`-looking segments substituted with empty string) — the
app then fails with `ValueError: Invalid salt` at login, not at startup.
Every literal `$` in that value must be doubled (`$$`). Documented at the
point of use in `body/dashboard/secrets/.env.example` and
`body/dashboard/README.md`, not just here.

**Second gotcha:** the dashboard container runs as a fixed non-root
UID/GID (`10001`, set in `body/dashboard/Dockerfile`) as defense in
depth, but the instance's `audit/` directory is created `root:root,
chmod 700` by `tools/audit-tap`'s own convention. The two defaults
conflict by design (neither should default to being readable by
"other"), so deploying a dashboard for an instance requires an explicit
`chown root:10001 .../audit && chmod 750 .../audit` step — documented in
`tools/audit-tap/README.md`'s Permissions section.

### publish: Python + `markdown` + `jinja2` + `pyyaml`, systemd timer, static output

All three dependencies are ordinary Debian/Ubuntu apt packages
(`python3-markdown`, `python3-jinja2`, `python3-yaml`) — no pip, no venv,
no container needed for the generator itself, matching the audit-tap
choice for the same reasons. Output is plain static HTML; serving it is
one read-only bind mount plus one Caddyfile vhost block in the *already
running* `/opt/ops` Caddy — no new service, no new container.

A daily systemd timer (not a git-push hook) because CGR-55 deliberately
has no Forgejo/host-repo yet (explicit instance-level decision, unrelated
to this ADR) — there is no push event to hook into. The build is
idempotent, so a fixed daily cadence is cheap; an admin can also trigger
it immediately (`systemctl start publish@<NAME>.service`) right after
opting a new piece in.

## Consequences

- Total new persistent processes on the host: one (the dashboard
  container) per instance. audit-tap and publish are both timer-fired
  one-shots with zero idle footprint.
- The dashboard's per-instance, per-port topology means N instances on
  one host need N ports reserved (documented starting point: 8090, 8091,
  ... — not yet formalized as a registry; revisit if/when this host runs
  more than two or three instances).
- Any future cross-instance aggregation view must be designed against a
  network API each instance's dashboard exposes, never against direct
  filesystem access to other instances' `audit/` directories.
