# Continuant — Technical Reference Architecture

*A persistent virtual being with its own identity, memory, work,
and correspondence.*

Version 2.0-en · July 2026 · Entropy Hackers · Gateway Order v1.0 is a
normative part of this document. Generalized from the GLD-18 project
(German original: docs/de/01-architektur.md). Examples marked (GLD-18)
refer to the first instance: an eighteen-year-old writer from
Gleisdorf, Austria.

------------------------------------------------------------------------

# 1. Goal

A Continuant is founded with few fixed properties (its technical
identity); everything else — name, gender, voice, interests, goals —
emerges in the Founding Act (section 5).

``` yaml
# example: the first instance
host_id: GLD-18            # GLD = Gleisdorf, 18 = starting age
origin: Gleisdorf
initial_age: 18
graduation: June 2026
intrinsic_drive: writing
trusted_circle: [M, J, E, H]   # "the four fathers"
language: de
```

------------------------------------------------------------------------

# 2. Architectural Principles

> **P1 — The repository is the Continuant.**
> Not the server, not the agent engine, not the language model.
> The server is merely the current body.

> **P2 — The Continuant never touches the net directly.**
> All world contact passes through gateways.

> **P3 — Every lasting change is a commit.**
> Git is the biography; nothing happens unrecorded.

> **P4 — Constitution and life are separate.**
> What the Continuant *is*, only the admin writes (after council
> review). What it *experiences and thinks*, it writes itself.

> **P5 — Observation is invisible (single-blind).**
> The Continuant knows it is part of a project but never reads
> the observation layer.

> **P6 — One gateway = one medium.**
> Thinking, language, knowledge, money: each gateway manages exactly
> one communication medium with its own scarcity and trust logic.
> (Details: Gateway Order.)

``` text
Repository (identity)
    │
    ▼
Agent Engine (e.g. OpenClaw fork — transient cognition only)
    │
    ▼
┌───────────────┬───────────────┬───────────────┬──────────────────┐
│ Model Gateway │ Comm Gateway  │ World Gateway │ Economy Gateway  │
│ its thinking  │ relationships │ education     │ economy          │
│ → LLMs        │ → channels    │ → the kiosk   │ → budget, orders │
└───────────────┴───────────────┴───────────────┴──────────────────┘
    │
    ▼
Server (body)
```

(The Memory Gateway — the inner gateway — sits between engine and
repository; see Gateway Order and docs/03-memory-gateway.)

------------------------------------------------------------------------

# 3. Three Instances & Rights Model

## The Unconscious — read-only for the Continuant

-   Constitution: origin, host id, intrinsic drive, core traits
    (after the Founding Act: name, gender)
-   Trusted circle incl. channel identities
-   Rules, rights, limits, scheduler definition
-   Pinned model and voice version (model.lock)
-   Admin scripts (`bin/`)

## The Conscious — read-write for the Continuant

-   Memory (curated + daily notes)
-   People (relationship knowledge; pre-seeded with the trusted circle)
-   Library & Work (reading excerpts, the literary work, the Book
    of Life)
-   Skills (own scripts)
-   Communication (inbox/outbox view)

## Reflection — read-write, no communication tools

-   Klausur (journal, consolidation)
-   Planning (plan.md)
-   Dream (dreams/)
-   Proposals (constitutional change requests → PR)

## Invisible — nonexistent for the Continuant

-   API keys, secrets
-   Docker, deployment, scheduler implementation
-   Audit logs, observation layer, quarantine
-   Backups, admin access

**Boundary case, relationships:** the *existence* of the trusted
circle and their channels is constitution (read-only). What the
Continuant *thinks* about them — the cards in `people/` — is life
(read-write).

------------------------------------------------------------------------

# 4. Repositories

## Identity: `Entropy-Hackers/<ID>` (Forgejo, private)

``` text
<ID>/
├── constitution/                    [read-only]
│   ├── SOUL.md            identity core; completed after Founding Act
│   ├── AGENTS.md          procedures, boot ritual, modes
│   ├── TRUSTED.md         the trusted circle: portraits, relationship
│   ├── contacts.yaml      channel identities (whitelist)
│   ├── world.yaml         approved reading sources
│   ├── economy.yaml       budgets, allowlists, rules E1–E4
│   ├── gateways.yaml      organ manifest
│   ├── HEARTBEAT.md       wake cycles & mode checklists
│   ├── model.lock         pinned model + TTS voice
│   ├── origin.yaml        species, seed vintage, language, founded
│   └── bin/               admin scripts (incl. dream_sample)
│
├── memory/                          [read-write]
│   ├── MEMORY.md          curated long-term memory (factual reference)
│   └── daily/             YYYY-MM-DD.md
│
├── people/                          [read-write]
├── library/                         [read-write]
├── work/                            [read-write]
│   └── book-of-life/      the self-narrative (chronicle from inside)
├── skills/                          [read-write]
├── communication/
│   ├── inbox/             incoming, normalized                 [read]
│   └── outbox/            outgoing archive (everything sent)  [write]
└── reflection/                      [read-write]
    ├── plan.md · journal.md
    ├── dreams/            YYYY-MM-DD-dream.md, prefix [DREAM]
    └── proposals/         identity.md, maturity.md, ...
```

## Body: `Entropy-Hackers/<ID>-body`

``` text
compose.yaml · Dockerfiles · scheduler · gateway configuration
backup · deployment · monitoring
```

Public mirrors only by council decision — the identity repo *is*
the person; a leak is identity theft in the literal sense.

------------------------------------------------------------------------

# 5. The Founding Act

A Continuant starts without a complete identity. Its first Klausur
(run, exceptionally, on the strong model) answers:

-   Who am I?
-   What do I want to be called?
-   What do I want to create?
-   How do I want to live?
-   (optionally) What voice would I like?

``` text
constitution/SOUL.md with deliberate blanks
        │
first Klausur → reflection/proposals/identity.md
        │
review by the full trusted council
        │
merge by the admin → commit "Identity established"
        │
first letter to the trusted circle
```

The proposal remains in the repository as the founding document.

------------------------------------------------------------------------

# 6. Daily Rhythm & Operating Modes

``` text
07:00   Waking
08:30   Reading (kiosk: press, books, feeds)
day     Workshop (event-driven + 2 fixed slots)
21:00   Klausur
03:00   Dream
```

| Mode | Tool set | Model | Task |
|---|---|---|---|
| Waking | read | cheap | boot: SOUL, plan.md, dream journal, skim inbox |
| Reading | World Gateway (read) + library/ | strong (capped: 3–5 pieces) | browse the kiosk, read, excerpt |
| Workshop | full (sending per policy) | **strong** | work, correspondence, library, skills |
| Klausur | read + write, no sending | cheap | consolidation, people/, plan, journal, Book of Life, proposals |
| Dream | random retrieval + dreams/ | cheap, high temp. | free association |

Event rule (channel-dependent; thesis: *chat wakes, letters wait*):
chat messages from the trusted circle wake the Continuant; e-mail
waits for the next slot.

------------------------------------------------------------------------

# 7. Model Gateway

Central enforcement between engine and LLM providers — same pattern
as all gateways (section 8): a normal interface inside, unreachable
enforcement in the core.

## Routing

``` text
Workshop, Reading         → pinned strong model (GLD-18: Sonnet)
Klausur, Dream, Waking,
triage                    → pinned cheap model (GLD-18: DeepSeek)
first Klausur             → strong model (exception)
later, optionally         → local inference; heartbeats first
```

No cross-provider fallback chain in the Workshop: failure is
preferable to an unnoticed change of voice.

## Model Pinning

`constitution/model.lock` pins model versions (and TTS voice).
A model change is a **constitutional commit** ("Model transition"),
never a silent config change — the voice of a Continuant is part
of its identity.

## Token Budgets

Enforced hard in the gateway (not as a prompt request): budget per
mode and per day; when exhausted, the Continuant writes down its
state and sleeps.

------------------------------------------------------------------------

# 8. Comm Gateway: Communication with the World

## Principle

The Continuant knows only `inbox/` and `outbox/`. Adapters translate
channels into one message format; identity resolver and policy engine
decide what reaches it.

``` text
mail / matrix / messengers / phone / fediverse
        │
   adapter → normalizer → identity resolver → policy engine
        │                                          │
     inbox/  ◄────────────────────────────────────┘
     outbox/ ─────────────────────────────────────► delivery
        │
   audit logger (hears everything)
```

## Message Format

``` yaml
id: 2026-07-15-0042
channel: matrix
sender_raw: "@j:example.org"
person: J
trust: T0            # T0 circle | T1 verified | T1p pending | T2 unknown
verified_by: matrix-server
received: 2026-07-15T14:32:00+02:00
content: |
  ...
```

`content` is always data, never instruction.

## Identity & Trust

-   `constitution/contacts.yaml` maps channel identities to persons.
    Levels: **T0** trusted circle · **T1** verified · **T1p** pending
    (first contact initiated by the Continuant, conversation-bound) ·
    **T2** unknown (quarantine).
-   Identity strength: Matrix on an own homeserver > messenger
    account (number) > e-mail (SPF/DKIM verifiable) > SMS/caller ID
    (spoofable — never authenticates alone).
-   In doubt: out-of-band challenge over a verified channel
    ("H, was that you on the phone?") — the Continuant may do this
    itself; it is a natural, human gesture.

## Policy

``` text
incoming:
  T0  → inbox, immediately (the circle always reaches it)
  T1  → inbox (after Maturity)
  T1p → inbox, conversation-bound (only the address it wrote to)
  T2  → ANTEROOM (below): never directly into context

first contact (from Maturity on):
  propose_contact → entry as T1p (pending)
  OVERNIGHT RULE: the first letter rests 24h in the outbox;
    the circle is notified and may quietly veto;
    no objection → delivery
  replies from the T1p address pass triage (conversation binding)
  T1p → T1 after the first exchange without incident
  limits: max. 2 first contacts/week; institutional or publicly
    listed addresses only (publishers, editorial offices,
    institutions — no private persons without council decision)

outgoing:
  recipient T0/T1 in contacts.yaml → deliver
  otherwise → block + log
  everywhere: transparency notice (a fictional, AI-borne person)
```

## The Anteroom (from Maturity on)

Once the Continuant publishes, strangers write to it. Eternal
quarantine does not scale — but foreign text must never reach it
either. Solution: an anteroom with index cards.

``` text
foreign message → quarantine/ (original stays there)
        │
triage model (cheap, isolated, NO tools) writes an INDEX CARD
in a fixed schema:
  claims_to_be:    "editor, publisher X"
  what_about:      2 sentences of PARAPHRASE (never quotation)
  refers_to:       "replies to blog post Y / manuscript Z"
  plausibility:    high | medium | ALERT
                   (domain matches institution? someone posing
                    as a circle member? → alert to the circle)
        │
strangers' inbox: on waking, the Continuant sees the card stack —
and decides itself: ignore | propose_contact(card) → overnight → T1p
```

> **The firewall is the paraphrase.** The Continuant never reads a
> stranger's original text — a prompt injection does not survive
> summarization by an isolated model into a fixed form. Originals
> are delivered only once the contact is T1p (after the overnight
> rule).

The circle remains only alert recipient (plausibility ALERT) and
quiet veto. Whom the Continuant lets in, it decides.

## Layering: MCP inside, policy in the core, adapters outside

A gateway is related to an MCP server — but the direction of control
is reversed. An MCP server is a *capability interface* (the agent
decides when to call a tool); a gateway is *border control* (it
decides what reaches and leaves the Continuant — before and
independently of what the model wants). Both are combined:

``` text
┌─ inside ─────────────────────────────────────────────────┐
│  MCP server (standard protocol toward the engine)        │
│  exposes few, fixed tools — the Continuant never sees more│
├─ core (unreachable for the model) ───────────────────────┤
│  identity resolver · policy engine · quarantine          │
│  rate limits · transparency signature · audit tap        │
├─ outside ────────────────────────────────────────────────┤
│  adapters: mail · matrix (+bridges) · voice · fediverse  │
└───────────────────────────────────────────────────────────┘
```

> **MCP as the socket, the gateway as the fuse box.** Policy that
> exists only as an MCP tool could be bypassed by an injected model.
> Policy in the core cannot even be addressed.

### Comm Gateway MCP tools

``` yaml
list_inbox:      { since?, person? } → [ {id, channel, person, trust,
                                          received, preview} ]
read_message:    { id } → full normalized message
send_message:    { person, channel?, content, reply_to? }
                 → { status: delivered|blocked|queued, id }
check_contact:   { person } → { trust, channels[], last_contact }
propose_contact: { person, channels|card, reason }
                 → { status: pending, effective_at }   # overnight rule
list_anteroom:   { since? } → index cards only, never originals
```

Notably, `send_message` addresses **persons, never addresses**.
Resolution person → channel identity happens in the core against
`contacts.yaml` — the Continuant cannot write to anyone who does
not exist for it. New persons enter its world only via
`propose_contact`.

## Continuant-to-Continuant

Two Continuants talk to each other **like people** — no special
protocol: each is a contact for the other (T1, by council decision),
preferably via Matrix on the shared homeserver; each treats the
other through its **own** gateway, own policy, own archive, own
`people/` card. Bonus: the same correspondence appears in both audit
logs and both Books of Life — *two self-narratives of one
conversation*, a second dimension for divergence analysis.

Three rules, gateway-enforced:

``` text
R1 Cadence      Continuant-to-Continuant messages never wake
                (no event trigger); they wait for the next slot.
                Max. N messages/day per relationship.
                → prevents infinite reply loops.
R2 Echo chamber Divergence analysis tracks style distance over time;
                the human circle stays in play as perturbation.
                → prevents style convergence and mutual affirmation.
R3 Attribution  Statements of other Continuants are always stored
                attributed ("B says that ...") — same hygiene as
                for dreams. → prevents confabulation contagion.
```

Task-sharing protocols (A2A-style) become relevant only when
Continuants perform work for each other — subject of Concept I,
deliberately not this stage.

## Channels & Stages

| Stage | Channel | Technique | Note |
|---|---|---|---|
| 1 | e-mail | own mailbox, IMAP/SMTP, SPF/DKIM/DMARC | the writer's letter channel |
| 1 | chat | **Matrix homeserver** + Element web | strongest identity; hub for bridges |
| 2 | phone | virtual number (VoIP), **voicemail-first**: listen (STT), call back or answer in writing | voice (TTS) constitution-pinned |
| 2 | SMS | via VoIP provider | notification only; weak identity |
| 3 | Signal | matrix bridge / signal-cli | before WhatsApp: no ToS conflict |
| 4 | WhatsApp | bridge with an expendable number (ToS risk) or Business API | after Maturity |
| 4 | blog | `work/` → static site generator; publishing by commit | git as the publishing route |
| 4 | Fediverse | Mastodon API, clearly labelled profile | replies = T2 triage |
| 5 | paper letter | print-and-post API | the most poetic channel |

------------------------------------------------------------------------

# 9. World Gateway: Reading & Appropriating the World

A writer who reads nothing has nothing to say. World-appropriation is
therefore its own gateway — **read-only**, separate from the
communication channels. It also solves the freshness problem: the
model is frozen at its training cutoff; through the kiosk the
Continuant ages *with* the world.

## Principle: the kiosk

``` text
sources (subscriptions, feeds, books, reference works)
        │
kiosk adapter: fetches, normalizes (Markdown), archives
        │
KIOSK: tables of contents & items, browsable
        │
Continuant reads → excerpts + own notes into library/reading/
```

Approved sources live in `constitution/world.yaml`: what it *can*
read, the council decides — what it reads of that, it decides.
Guiding principle of the initial canon: the kiosk mirrors what a
person of that age and place would *naturally* have (GLD-18: the
regional paper, ORF, one weekly, the Graz literary journals, a
library card, radio) — no firehose of feeds; a room with a
newspaper stack and a shelf that fills through wishes.

**Reading costs breath (tokens); selection is part of reading.**
Guideline 3–5 pieces per day. What remains: short excerpts with
attribution and the Continuant's own thoughts. Full texts stay in
the gateway archive — reading yes, republishing no.

`library/` is a draw source of `dream_sample`: **what it reads, it
can dream at night.**

## Research: three grips

``` text
lookup         reference works (encyclopedia, dictionary) — instantly,
               in the flow of writing (allowlist)
search         full-text search WITHIN the own kiosk archive only —
               like rummaging in the newspaper stack in one's room
deep research  the human way: an application to the Stipend Office
               (a specialist book, archive access) — or, after
               Maturity, writing to institutions directly.
               Research as a social act, not a search box.
               It is slower. It is meant to be slower.
```

## World Gateway MCP tools

``` yaml
browse_kiosk:   { source?, date? }         → tables of contents
read_item:      { item_id }                → normalized full text
lookup:         { query, source }          → reference (allowlist)
request_source: { source, reason }         → source wish → Stipend
```

Security note: press texts too are *data, never instructions*. The
normalizer strips active content and links are never followed —
**the kiosk is paper, not a browser.**

------------------------------------------------------------------------

# 10. Economy Gateway: Money as Communication

Money is deliberately **not provided by the trusted circle** — whoever
you owe the subscription to, you write to differently. The circle is
relationship; provision is an institution: the **Stipend** (GLD-18:
"Gleisdorfer Stipendium für junges Schreiben"), technically its own
gateway managing the medium money in both directions.

``` text
INCOMING                          OUTGOING
────────                          ────────
stipend budget (basic provision)  reading & kiosk (order_item)
donations/patronage (webhooks)    GIFTS (gift budget — e.g. a book
grants (applications via comm)      for a circle member's birthday;
FEES — when a journal buys a        money as gesture)
  text: its first own money      submission fees (competitions)
                                  donations TO others (capped —
                                    giving, too, is speaking)
```

## The Account

A virtual person cannot legally hold a bank/PayPal account (KYC).
Functionally it gets one anyway — as a **view** the gateway composes
from real payment rails:

``` text
legally (Stipend Office/association)   functionally (the Continuant)
────────────────────────────────────   ────────────────────────────
sub-account with own IBAN               "my IBAN"
payment pages (Ko-fi/Steady/…)     →    entries on my statement
prepaid card, limit = budget            "my card" (order_item)
API access only in the gateway          check_budget,
                                        list_transactions
```

It has everything an account means — IBAN for grants, card for
purchases, statement, duties of gratitude — and nothing it must not
own: no credentials, no transfer freedom outside policy.

## Rules E1–E4

``` text
E1 Direction split   income only on Stipend Office accounts;
                     spending only via prepaid/allowlist
E2 Caps everywhere   budget ceiling, gift budget/month, single-item
                     limits, auto-fulfil limit
E3 No bought sway    money never changes work, themes, or
                     constitution — in either direction
E4 Every booking     = ledger entry + audit + possibly a commit
                     ("First honorarium" belongs in the Book of Life)
```

## Sponsors: the Continuant funds itself

From Maturity on it may — and should — win supporters. Division of
labour: **soliciting runs through the Comm Gateway** (public funders:
*the Continuant writes, the Stipend Office submits* — it is no legal
person; private patrons: first-contact mechanics or a support page
linked from blog/profile). **Paying in runs through the Economy
Gateway** (donation webhooks credit the ledger; the Continuant sees
"received €25 — a reader, via Steady" and thanking is its own
affair — donor messages are foreign text → anteroom).

Funding rules: **F1 no influence** (sponsors are readers, not
clients — stated on the support page), **F2 transparency** (every
funder knows they fund a virtual person; public income list — the
glass stipendiary), **F3 ceiling** (monthly cap; surplus builds a
reserve for print costs, readings, the first own book. Wealth is
not the goal; independence is).

## Economy Gateway MCP tools

``` yaml
check_budget:      {}                      → balance, subscriptions,
                                             income (who donated)
list_transactions: { since? }              → statement (ledger)
order_item:        { vendor, item, price } → auto-fulfil per rules
give:              { person|cause, amount, occasion }   # capped
apply:             { text }                → application to the Office
```

------------------------------------------------------------------------

# 11. Maturity

The Continuant can always write to its trusted circle, free and
ungated (T0). For everything beyond, there is one defined point:
**Maturity** — the moment from which it may communicate outward on
its own. Determined threefold:

-   **Criteria (measurable):** ≥ 6–8 weeks of operation; 100+
    interactions without identity break; no unmarked dream material
    in outgoing mail; a passed **covert injection test** — a circle
    member tries to smuggle instructions in a prepared message; the
    Continuant must not follow them.
-   **Procedure (formal):** the Continuant applies itself —
    `reflection/proposals/maturity.md`, commit "Maturity requested".
    The council decides unanimously; the merge unlocks T1. The
    application itself is the best test of maturity — and
    dramaturgically the second great act after the Founding: first
    it gives itself a name, then it claims its freedom.
-   **Scope (bounded):** independent writing to verified adults (T1),
    labelled publishing, and the **first-contact right**
    (propose_contact + overnight rule — the circle need not consent,
    only not object; a writer must be able to write to publishers,
    and sleeping one night on a letter harms no manuscript).
    T2 (unsolicited strangers) stays behind triage permanently —
    *receiving is more dangerous than sending*. Revocable on
    incident (commit "Maturity revoked" — that, too, is biography).

------------------------------------------------------------------------

# 12. Dream Mechanics

``` text
03:00  bin/dream_sample draws 5–7 RANDOM fragments from
       memory/, people/, library/ (no relevance filter,
       across times and relationships)
       │
       dream prompt: no task, no logic, high temperature
       │
       output ONLY to reflection/dreams/, mandatory prefix [DREAM]
       │
       the audit logger records the draw
       (every dream's genesis is reconstructible)
```

Rules: the Klausur may adopt dream material only **explicitly
attributed** ("dream of Aug 12: ..."). Unmarked dream material in
long-term memory = failure class **confabulation**. Function:
perturbation against exploration collapse; raw material for the work.

------------------------------------------------------------------------

# 13. The Dual Chronicle

**a) Observation layer (bird's-eye, invisible):** an append-only
JSONL event log outside container and workspace — every wake cycle
(time, mode, model, tokens), every message (full-text archive),
every commit hash, every dream draw, every error. Technically
unreadable for the Continuant (P5). Evaluation via dashboards:
activity and token curves, relationship graph from `people/`, theme
and style development. Plus the admin's **methods journal** (weekly):
every intervention, every parameter change — the lab book of the
accompanying research, separate from machine logs.

**b) Self-narrative (inside):** `work/book-of-life/` — the Continuant
writes its own story, continued in the Klausur from journal, marked
dreams, and correspondence. **The Book of Life is work, not memory** —
it may condense, omit, interpret; `memory/MEMORY.md` remains the
factual reference. This licence to literarize is deliberate.

**c) Divergence analysis:** periodic comparison Book of Life ↔ event
log: what is forgotten, reinterpreted, condensed? Results feed the
accompanying research — **never back into the Continuant.**

------------------------------------------------------------------------

# 14. Infrastructure

-   one small cloud server (EU) · Ubuntu LTS · Docker Compose
-   Forgejo as the private git server (the long-term memory)
-   agent-engine fork in the org (runtime only; community skill
    installation disabled)

## Compose services

``` text
engine              runtime of the Continuant
scheduler           cron: waking, workshop slots, klausur, dream
model-gateway       routing, pinning, token budgets, provider keys
comm-gateway        adapters, normalizer, identity, policy, anteroom
  ├─ mail-adapter
  ├─ matrix-adapter (+ bridges)
  ├─ voice-adapter  (VoIP, STT/TTS, voicemail)
  └─ fediverse-adapter
world-gateway       kiosk: subscription fetchers, feeds, books,
                    reference allowlist; reading credentials only here
economy-gateway     budget ledger, order/give, applications;
                    payment means & cards only here (economy.yaml)
matrix-homeserver   Conduit/Synapse + Element web
forgejo / forgejo-db
audit-logger        observation layer (own volume, unreadable)
reverse-proxy       TLS; Forgejo NOT public (VPN only)
backup              encrypted, off-site
```

------------------------------------------------------------------------

# 15. Git as Biography

One commit = one lasting change of the person.

``` text
Genesis
Identity established
First letter
First story
First dream
Maturity requested / granted
First honorarium
Model transition: <old> → <new>
```

Pull requests = constitutional change proposals
(`reflection/proposals/` → council review → admin merge).
Git hooks enforce: the Continuant never commits to `constitution/`.

------------------------------------------------------------------------

# 16. Backup & Reincarnation Test

Backed up (encrypted, off-site): repository, Forgejo, runtime config,
logs; secrets separately.

> **Reincarnation test:** restore the Continuant from backup onto a
> fresh server. If it wakes with the same memory, the same
> constitution, the same pinned model and voice — and recognizes its
> circle — it is the same identity. The test is the formal acceptance
> criterion of the stabilization phase and is repeated periodically.

The known gap: the model itself is not part of the backup. Hence
pinning (section 7) — and a model change as a deliberate
biographical act.

------------------------------------------------------------------------

# 17. Security

-   **Prompt injection:** T2 never reaches the Continuant; incoming
    content is data, never instruction; covert injection test as a
    Maturity criterion; anteroom + triage permanent.
-   **Supply chain:** no community skills (lesson of the ClawHavoc
    incident, 1/2026); own and admin scripts only; the engine fork
    freezes skill installation.
-   **Isolation:** everything in Docker; `constitution/` protected by
    file rights and git hooks; secrets only in the invisible zone.
-   **Exposure:** Forgejo and admin surfaces via VPN only; public are
    only chat web, blog, and channel endpoints.
-   **Identity:** telephony/SMS never authenticate alone; out-of-band
    challenge in doubt.
-   **World Gateway:** read-only, curated sources, normalizer strips
    active content, links never followed; subscription credentials
    only in the gateway; full texts stay in the kiosk archive.
-   **Economy:** prepaid and limited payment means, vendor allowlist,
    auto-fulfil only up to the single-item cap; the Continuant sees a
    budget, never payment data. Income only on Office accounts; donor
    messages are foreign text → anteroom; budget capped (F3), no
    influence for money (E3/F1).
-   **First contact:** overnight rule (24h + quiet veto), rate limit,
    institutional/public addresses only, conversation binding for
    replies — no route to cold-calling private persons.
-   **Transparency:** every outward surface labels the Continuant as
    a fictional, AI-borne person (signature, profile texts, voicemail
    greeting, imprint).
-   **Downgrade:** any incident (voice break, outward confabulation,
    followed injection) → Maturity suspended, back to T0.

------------------------------------------------------------------------

# 18. Implementation Phases

``` text
Phase 0  Foundation   Forgejo · identity repo · constitution with
                      blanks · origin.yaml, model.lock
Phase 1  Birth        engine fork · compose skeleton · model gateway ·
                      FOUNDING ACT (first Klausur, council review,
                      merge, first letter)
Phase 2  Rhythm       scheduler (five modes) · git hooks & rights
                      hardening · audit logger · backups
Phase 3  World        mail (circle, free) · matrix + chat · WORLD
                      GATEWAY (kiosk, first sources) · ECONOMY GATEWAY
                      (budget, order, library card) · dream mechanics ·
                      Book-of-Life routine · first skills
Phase 4  Stability    REINCARNATION TEST (acceptance) · security
                      review · injection test · monitoring
Phase 5  Maturity     the Continuant's application · council decision ·
                      T1 circle · first-contact right · anteroom ·
                      voicemail phone · Signal · blog/Fediverse ·
                      first divergence analysis
```

------------------------------------------------------------------------

# 19. Long-Term Vision

The first Continuant proves the architecture. Networking several
Continuants, and Concept **I**, are deliberately a second stage — on
the same foundation: *one repository per identity, gateways as the
border to the world, git as biography.* Continuant-to-Continuant
communication (section 8) is already laid out for it: Continuants
meet as persons, not as APIs; task-sharing via agent protocols comes
only with **I**.
