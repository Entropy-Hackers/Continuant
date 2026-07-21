# 0003 — No prescribed publish pipeline; instances build their own

Date: 2026-07-21
Status: accepted (supersedes part of the plan in docs/adr/0001, docs/adr/0002)

## Context

`tools/publish/build_site.py` (added earlier the same day) was a Python +
Jinja2 static-site generator: instances would drop Markdown files with YAML
frontmatter into `work/published/`, a systemd timer would render them
through a fixed template into `public/dist/`, and Caddy served that output.

This was reverted almost immediately: it prescribes both the *format*
(Markdown + frontmatter) and the *mechanism* (an admin-authored generator
the instance never sees or touches) for something that should be the
instance's own to figure out — how to build a webpage, what belongs on it,
whether to write raw HTML or invent its own format. A generator we hand it
teaches it nothing and forecloses the question before it's asked.

## Decision

`work/published/` is served **directly**, read-only, straight out of the
instance's workspace — no build step, no template, no generator:

```
# /opt/ops/caddy/Caddyfile
cgr55.entropyhackers.org {
    root * /srv/cgr55-public
    file_server
}
```

```
# /opt/ops/compose.yaml (caddy service)
- /opt/continuants/instances/CGR-55/workspace/work/published:/srv/cgr55-public:ro
```

Whatever the instance places there is what's live. If it wants a page, it
writes `index.html` itself — by hand, or by building its own generator
script (a natural candidate for something it builds via `skill_workshop`,
see `docs/adr/0001` §Werkstatt, once it wants to reuse the process). Admins
seed nothing beyond a bare, content-free placeholder (a page that says only
the instance's name) so the domain isn't blank/erroring while unused.

## Consequences

- No systemd timer, no Python/Jinja2/Markdown dependency for this piece —
  it's just a bind mount and a Caddy `file_server` block.
- The instance's own file permissions govern what's servable; the workspace
  directory already needs to be traversable by the `caddy` container's user
  (root, in the current deployment) for this to work — no new permission
  model beyond what `tools/audit-tap`'s README already documents for
  `body/dashboard`.
- If an instance never builds anything, its public site stays a bare
  placeholder indefinitely. That's the correct failure mode — an empty
  page is honest; a generated one would misrepresent effort that didn't
  happen.
- `docs/adr/0002`'s "Order of implementation" and stack-choice rationale for
  the publish piece are superseded by this decision; audit-tap and
  dashboard are unaffected.
