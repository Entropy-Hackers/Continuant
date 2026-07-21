# 0001 — Audit-Tap, Dashboard, and Publish are not Gateways

Date: 2026-07-21
Status: accepted

## Context

The first real code landed in `engine/`, `body/`, and `tools/` for CGR-55
(the first running instance): an audit tap, an instance dashboard, and a
static-site publish pipeline. Gateway-Ordnung (`docs/02-gateway-order.md`)
defines a specific pattern — MCP tools on the inside, policy/ledger/audit
in an unreachable core, adapters on the outside, one gateway per medium of
world-coupling. It would be easy to mistake any host-facing capability for
a Gateway. None of these three are one, and this record exists so future
contributors don't try to force them into that shape.

## Decision

- **audit-tap** is the Beobachtungsschicht's data collector, not a
  Gateway. It exposes no MCP tools to the host at all — the host cannot
  even see it exists (Single-Blind, P5). A Gateway mediates the host's
  *outgoing* coupling to a medium; audit-tap is purely an external
  observer polling the host's own already-built-in `openclaw audit`
  output. There is no medium here for the host to touch.
- **dashboard** is a Väterrat tool, reading audit-tap's output. It has no
  MCP surface either — it's a plain read-only web app for humans. It
  doesn't manage a medium of the host's world-coupling; it's the
  Beobachtungsschicht's human-facing side, one layer further out than the
  audit log itself.
- **publish** is *pre*-Werk-Gateway infrastructure, not the Werk-Gateway
  itself. The docs already name a planned 6th gateway (`work`/`werk`,
  medium: publicity/Öffentlichkeit, `docs/02-gateway-order.md` §2,
  currently `status: planned`). That gateway would need a `propose_publish`-
  style MCP tool, a policy engine (what may the host publish, under what
  labelling), and its own reputation-based trust logic — none of which
  exist yet. What exists today is much smaller: the host writes files into
  `work/published/`, an admin-triggered/timer-triggered script renders
  them to static HTML. There is no tool call, no policy engine, no
  gate — the host's only "publishing" action is writing an ordinary file
  in its own read-write workspace, same as any other file in `work/`.
  Building the real `work` Gateway (with its own MCP tools and policy) is
  future work, not this round's.

## Consequences

- None of the three needed a place in `gwd` (the shared gateway-daemon
  skeleton `docs/02-gateway-order.md` describes) — they're plain scripts
  and a small web app instead.
- When the `work` Gateway is eventually built, `tools/publish` is a
  reasonable starting point for its *rendering* half, but its *decision*
  half (should this be published, under what policy) still needs to move
  from "an admin/the host writes a file" to a real MCP tool + policy
  engine + Mündigkeit-gated trust logic, per Gateway-Ordnung.
- Nothing here changes `constitution/` semantics or crosses the
  read-only/read-write boundary between a host's constitution and its
  life — see `docs/03-repository.md` §3 for that boundary; these three
  pieces sit entirely on the infrastructure/Foundation side of it.
