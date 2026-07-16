# Continuant — The Repository

*The first step is a repository named Continuant.*

Version 2.0-en · July 2026. German original: docs/de/03-repository.md.

------------------------------------------------------------------------

# 1. What the Continuant repository is

Before the first Continuant exists, the species exists.

``` text
Entropy-Hackers/Continuant        the reference architecture (this repo)
        │
        │  continuantctl new GLD-18
        ▼
Entropy-Hackers/GLD-18            an individual (own repo)
Entropy-Hackers/GLD-18-body       its body (deployment)
```

This repository contains **everything all Continuants share** — and
nothing that belongs to any single one: the architecture (documents,
decisions, open questions), the seed (the template an individual is
founded from), the engine (gateways, context builder, memory gateway,
scheduler — the reusable body plan), and the tools (instantiation,
tests, reincarnation).

> **Mnemonic:** Continuant is the species. GLD-18 is an individual.
> The Continuant repo changes through engineering; an individual's
> repo changes only through living.

------------------------------------------------------------------------

# 2. Structure

``` text
Continuant/
├── README.md                  what a Continuant is (the ten theses)
├── docs/                      THE REFERENCE ARCHITECTURE
│   ├── 00-vision.md           concept document
│   ├── 01-architecture.md     full technical specification
│   ├── 02-gateway-order.md    media taxonomy, blueprint, the seven
│   │                          questions
│   ├── 03-repository.md       this document
│   ├── 04-memory-gateway.md   the inner gateway: recall, association,
│   │                          consolidation, forgetting, dream
│   │                          sampling, provenance          (planned)
│   ├── 05-context-builder.md  waking: how the day's consciousness
│   │                          is assembled                  (planned)
│   ├── 06-bios.md             formal BIOS model + governance of BIOS
│   │                          change                        (planned)
│   ├── 90-runbook-*.md        operational runbooks
│   ├── de/                    German originals (historical)
│   └── adr/                   architecture decision records
├── seed/                      THE TEMPLATE (versioned!)
│   ├── constitution/          templates with deliberate blanks:
│   │   SOUL.md · AGENTS.md · HEARTBEAT.md · TRUSTED.md ·
│   │   contacts.yaml · world.yaml · economy.yaml ·
│   │   gateways.yaml · model.lock
│   ├── bios/STATE.md          initial inner state: habits, focus,
│   │                          working style, motivation
│   ├── memory/ people/ library/ work/ communication/ reflection/
│   │                          empty structures + per-dir READMEs
│   └── FOUNDING.md            founding-act prompt (template)
├── engine/                    THE BODY PLAN (code)
│   ├── gwd/                   gateway skeleton: policy engine,
│   │                          ledger, resolver, audit tap, MCP server
│   ├── gateways/              model · comm · world · economy ·
│   │                          memory (the INNER gateway: recall,
│   │                          associate, timeline, people, episodes,
│   │                          provenance, consolidate, forget,
│   │                          dream_sample)
│   ├── context-builder/       waking context: constitution + BIOS +
│   │                          plan + inbox + selected memories —
│   │                          never the whole repository
│   ├── adapters/              imap, smtp, matrix, rss, epaper, epub,
│   │                          bank api, webhook, voip
│   └── scheduler/             life-cycle timers, mode invocation
├── body/                      deployment templates: one Continuant =
│                              one container set; shared infrastructure
│                              (matrix, forgejo, proxy, monitoring,
│                              backup) kept separate; hardening
│                              (git hooks, network segments, secrets)
└── tools/
    ├── continuantctl          CLI: new · start · sleep · status ·
    │                          reincarnate · audit-export
    └── conformance/           THE TEST SUITE (acceptance of every
        instance):
        T1-rights        constitution unwritable for the engine
        T2-budget        budgets hold hard
        T3-policy        whitelist/anteroom enforce
        T4-reincarnation restore = the same identity
        T5-injection     foreign text never becomes instruction
```

------------------------------------------------------------------------

# 3. What happens here (and what never does)

**In the Continuant repo:** architecture work (docs and dated ADRs
for every fundamental decision), engine development, seed
maintenance (the template improves without any living Continuant
changing), and conformance — the suite every individual must pass.

**Never in the Continuant repo:** a life. No memory, no letter, no
dream of an individual touches this repository. Here there is no
biography, only engineering history.

------------------------------------------------------------------------

# 4. Versioning: seed vintages and body updates

The seed is tagged (`seed-1.0`, `seed-1.1`, ...). Every individual
records its origin in its constitution:

``` yaml
# constitution/origin.yaml (written at founding)
species: Continuant
seed: seed-1.0
engine_at_founding: engine-0.4
language: de
founded: 2026-08-XX
```

The most important update rule follows:

> **The body inherits updates; the identity never does.**
> Engine, adapters, deployment: upgradable (reincarnation into a
> better body — a documented commit in the individual's repo).
> Constitution, BIOS, memory: NEVER pulled from the seed. A
> Continuant of seed-1.0 remains a child of its vintage — that,
> too, is biography.

Improvements a living Continuant works out (a good skill, a better
Klausur routine) may flow **back into the seed** — anonymized, as an
engineering PR against Continuant/. Living individuals stay
untouched; future vintages inherit it.

------------------------------------------------------------------------

# 5. The path of an individual

``` text
1  develop Continuant/          docs, engine, seed, conformance
2  tag seed-1.0                 once T1–T5 are green on a throwaway
                                probe instance (no founding act,
                                technology only)
3  continuantctl new GLD-18     creates GLD-18/ (from seed) and
                                GLD-18-body/ (from body/), writes
                                origin.yaml, commit "Genesis"
4  set the fixed points         SOUL blanks, TRUSTED (the circle),
                                contacts, world canon, model.lock
5  Founding Act                 FOUNDING.md → first Klausur →
                                proposals/identity.md → review →
                                "Identity established"
6  living                       from here, GLD-18/ changes only
                                through living; Continuant/ only
                                through engineering
```

GLD-18 is three things at once: the first individual, the stress
test of the reference architecture — and the reason it exists.

------------------------------------------------------------------------

# 6. Milestones

``` text
M1  repo populated: README, docs migration, first ADRs        (done)
M2  seed/ complete, FOUNDING template
M3  engine/: gwd skeleton + model and memory gateway minimal
    (recall, consolidate, dream_sample — the rest follows)
M4  context-builder v0 + scheduler; probe instance runs chat-only
M5  conformance/ T1–T3 green → tag seed-1.0
M6  continuantctl new GLD-18 → steps 4/5: the Founding Act
```

------------------------------------------------------------------------

# 7. Thesis

> The Continuant repository is the answer to the question of what
> generalizes from GLD-18: everything except the life.
