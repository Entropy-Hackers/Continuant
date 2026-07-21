# Continuant instance dashboard (v0)

Status and life view for a single Continuant instance, meant for the
trusted circle ("Väter"): audit-tap health, cron runs, workspace size —
plus the more human side, read-only from `workspace/`: recent `MEMORY.md`
entries, what's being written in `work/`, `people/` notes, the reading
list, and reflection journal/plan.

Runs **alongside** that one instance, not as a cross-instance aggregator:
an instance may live on a different server from any other, so a "see
everything" view is a separate, later concern (would need each instance's
dashboard to expose an API for a higher-level view to pull from — not
local bind mounts). Reads this instance's own `audit/` and `workspace/`
directories, both mounted read-only. Never writes to either, and never
touches `config/`, `secrets/`, or `docker.sock`.

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
  (`python3 -c "import bcrypt; print(bcrypt.hashpw(b'...', bcrypt.gensalt()).decode())"`).
  **Escape every literal `$` as `$$`** — `docker compose` interpolates
  `$VAR` inside `env_file` values, and a bcrypt hash is almost entirely
  `$`-delimited fields; an unescaped hash gets silently corrupted and
  login fails with `ValueError: Invalid salt`.

### Permissions

Both `audit/` (created `root:root chmod 700` by `tools/audit-tap`) and
`workspace/` (owned by the instance's container UID, usually `1000:1000`)
default to blocking every other user, including the dashboard's fixed
non-root UID/GID (`10001`, set in this directory's `Dockerfile`). Grant
group access narrowly instead of loosening either for everyone:

```bash
chown root:10001 /opt/continuants/instances/<NAME>/audit
chmod 750 /opt/continuants/instances/<NAME>/audit
chown <owner-uid>:10001 /opt/continuants/instances/<NAME>/workspace
chmod 750 /opt/continuants/instances/<NAME>/workspace
```

(`<owner-uid>` is whatever already owns `workspace/` — changing the
*group* only, never the owner, keeps the instance's own container's
read-write access untouched.)

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
harder to brute-force later, add rate-limiting to `/login` (not present
in v0).

## v0 scope / non-goals

One shared admin password per instance (no per-Vater accounts yet), no
login rate-limiting, no live `docker ps` polling, no history charts, no
cross-instance/cross-server aggregation — see `docs/adr/0001` and
`docs/adr/0002` for the full non-goals list.
