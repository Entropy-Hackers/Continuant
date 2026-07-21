# publish

Static site generator for a Continuant instance's published work. Reads
`workspace/work/published/*.md` (Markdown + YAML frontmatter) and renders
plain static HTML to `<instance-dir>/public/dist/` — never mounted into
the instance's own `openclaw-gateway` container.

Only files an admin (or, once Mündigkeit/the Werk-Gateway exist, the
instance itself) explicitly places in `published/` are ever included —
see `workspace/work/published/README.md` (created per-instance) for the
frontmatter convention.

## Requirements

Debian/Ubuntu apt packages, no pip/venv:

```bash
apt-get install -y python3-markdown python3-jinja2 python3-yaml
```

## Run

```bash
python3 build_site.py --instance-dir /opt/continuants/instances/CGR-55
```

Idempotent — safe to rerun; output directory is rebuilt from scratch each
time from whatever's currently in `published/`.

## Install a daily timer for an instance

```bash
sudo cp systemd/publish@.service systemd/publish@.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now publish@CGR-55.timer
```

Runs daily at 06:00 (±10min jitter) and is a no-op rebuild when
`published/` hasn't changed. Trigger manually right after opting a new
piece in: `sudo systemctl start publish@CGR-55.service`.

## Serving

`public/dist/` is plain static files — see the shared `/opt/ops` Caddy
config for how CGR-55's build gets served publicly (a read-only mount +
one vhost block; DNS for the chosen subdomain is an external, manual
dependency).
