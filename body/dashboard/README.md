# Continuant instance dashboard (v0)

Read-only status view for a single Continuant instance, meant for the
trusted circle ("Väter") — is the audit tap alive, last cron runs,
workspace activity. Runs **alongside** that one instance, not as a
cross-instance aggregator: an instance may live on a different server
from any other, so a "see everything" view is a separate, later concern
(would need each instance's dashboard to expose an API for a higher-level
view to pull from — not local bind mounts). Reads only this instance's own
`audit/` directory (produced by `tools/audit-tap`), mounted read-only.
Never touches `workspace/`, `config/`, `secrets/`, or `docker.sock`.

## Deploy (one per instance)

Real deployments are a sibling of the instance directory, e.g. for an
instance `CGR-55` at `/opt/continuants/instances/CGR-55/`:

```bash
mkdir -p /opt/continuants/instances/CGR-55/dashboard/secrets
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
  (`python3 -c "import bcrypt; print(bcrypt.hashpw(b'...', bcrypt.gensalt()).decode())"`)

Then, from the instance's `dashboard/` directory: `docker compose up -d --build`

## Expose over Tailscale (not public)

Same pattern already used for openclaw's own Control UI on this host —
HTTPS via `tailscale serve`, bound to loopback only. If more than one
instance's dashboard runs on the same host, give each its own path:

```bash
tailscale serve --bg --set-path /dashboard/CGR-55 http://127.0.0.1:8090
```

Reachable at `https://<host>.<tailnet>.ts.net/dashboard/CGR-55` within the
tailnet only. Do not bind `0.0.0.0`.

## v0 scope / non-goals

One shared admin password per instance (no per-Vater accounts yet), no
live `docker ps` polling, no history charts, no cross-instance/cross-server
aggregation — see `docs/adr/0001` and `docs/adr/0002` for the full
non-goals list.
