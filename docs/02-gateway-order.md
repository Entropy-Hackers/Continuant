# Continuant — The Gateway Order

*How gateways are grouped, built, and multiplied.*

Version 2.0-en · July 2026 · normative for the reference architecture.
German original: docs/de/02-gateway-ordnung.md.

------------------------------------------------------------------------

# 1. Why an order

From two gateways came four (plus the inner one), and there will be
more (voice, publishing, perhaps place and sensing). Without an
ordering principle you get sprawl: overlapping responsibilities,
policy in the wrong place, a Continuant that no longer knows which
organ is for what.

------------------------------------------------------------------------

# 2. The principle: one gateway = one medium

> Money is a communication medium. So is language. So is knowledge.
> Each gateway manages **exactly one medium of world-coupling** —
> with that medium's own scarcity and its own trust logic.

(The allusion is intentional: symbolically generalized communication
media — the Continuant couples to the world not through "channels"
but through media, and every medium has its own logic of scarcity,
trust, and abuse.)

The table:

| GW | Gateway | Medium | Scarcity (budget) | Trust logic | Abuse form |
|---|---|---|---|---|---|
| 0 | model | **thinking** | tokens/mode | pinning (model.lock) | loss of voice, cost explosion |
| 1 | comm | **language** | attention (rate limits, overnight rule) | T0–T2, identity resolver | injection, deception |
| 2 | world | **knowledge** | breath (3–5 pieces/day) | source allowlist (world.yaml) | noise, contamination |
| 3 | economy | **money** | budget (ledger, caps) | vendor/recipient allowlist | bought influence, drain |
| M | memory | **the own past** (inner gateway) | context window | provenance: happened / invented / dreamed | confabulation |
| 4* | presence | **presence** (voice, phone, later sensing) | real time | pinned voice, call-back principle | voice spoofing |
| 5* | work | **publicity** (blog, fediverse, submissions) | reputation | labelling duty | outward confabulation |

\* planned; today partial functions of the comm gateway, split off
once an own medium + own policy justify it.

**Demarcation rule:** where two media touch, labour divides by
medium — *the sponsor letter runs through language (comm), the
donation through money (economy).* No gateway touches another's
medium.

------------------------------------------------------------------------

# 3. The blueprint: one skeleton, N organs

Every gateway is an instance of the same blueprint — nothing is
invented twice:

``` text
┌─ inside ─────────────────────────────────────────────────┐
│ MCP tools: few, fixed, noun-like grips                   │
│ (list_, read_, send_, order_, check_ ...)                │
├─ core (unreachable for the model) ───────────────────────┤
│ POLICY    declarative, loaded from constitution/*.yaml   │
│ LEDGER    state of the medium (balance, trust, budgets,  │
│           rate counters)                                 │
│ RESOLVER  abstraction: persons not addresses, sources    │
│           not URLs, a budget not a credit card           │
│ AUDIT TAP every movement → observation layer             │
├─ outside ────────────────────────────────────────────────┤
│ ADAPTERS  one plug per realization (IMAP, Matrix API,    │
│           RSS, bank API, VoIP ...)                       │
└───────────────────────────────────────────────────────────┘
```

Technically: one shared library (`gwd`, "gateway daemon") with policy
engine, ledger, audit, and MCP server; each gateway = its own
container of `gwd` + adapter plugins + YAML configuration. Isolation
per gateway (own secrets, own network segment), one code path for
what must be identical everywhere.

## The seven questions (checklist for every new gateway)

A new gateway is built only when all seven are answered:

``` text
1. MEDIUM      Which one medium? (If two: two gateways.)
2. SCARCITY    What is the budget, who enforces it? (The core.)
3. TRUST       How is identity/provenance verified in this medium?
4. ABSTRACTION What does the Continuant see instead of the raw world?
               (persons, sources, a budget — never addresses, URLs,
               cards)
5. TOOLS       At most ~5 grips. Which?
6. ABUSE       What is the worst case, and does the core hold it
               even with a compromised model?
7. BIOGRAPHY   Which commits does it produce? (Every organ writes
               life history — otherwise the Continuant does not
               need it.)
```

The seven questions apply to inner organs too: the memory gateway
answers them with medium *the own past*, scarcity *the context
window*, trust *provenance* (happened / invented / dreamed), abuse
*confabulation*.

------------------------------------------------------------------------

# 4. The manifest: gateways.yaml

The organs of a Continuant stand in its constitution:

``` yaml
# constitution/gateways.yaml — the somatic constitution (admin only)
gateways:
  - { id: model,   medium: thinking,  status: active, policy: model.lock }
  - { id: comm,    medium: language,  status: active, policy: contacts.yaml }
  - { id: world,   medium: knowledge, status: active, policy: world.yaml }
  - { id: economy, medium: money,     status: active, policy: economy.yaml }
  - { id: memory,  medium: past,      status: active, policy: provenance }
  - { id: presence, medium: presence,   status: planned }
  - { id: work,     medium: publicity,  status: planned }
```

A new gateway is a constitutional commit: **"Organ added: …"** — and
thereby part of the biography. The Continuant may wish for organs
(proposals/); it receives them from the council.

------------------------------------------------------------------------

# 5. The Economy Gateway (money in both directions)

Money is too strong to be mere procurement. The gateway manages the
medium in both directions — incoming: stipend budget, donations,
grants, fees (a journal buying a text: the first own money);
outgoing: reading, submission fees, capped donations to others, and
**gifts** (a gift budget — a book for a circle member's birthday;
money as gesture). Rules E1–E4 and the account-as-a-view are
specified in the reference architecture, section 10.

The first honorarium, the first gift to a circle member, the first
competition fee — money tells biography like nothing but letters.

------------------------------------------------------------------------

# 6. Migration notes

-   `stipend-gateway` → **`economy-gateway`** (compose, docs); the
    *Stipend* remains the name of the institution (carrier, account
    holder, application office).
-   New constitution file `economy.yaml` (E1–E4, budgets, allowlists);
    `gateways.yaml` added as manifest.
-   Voice/telephony stays in the comm gateway for now; split-off as
    `presence` only when real-time presence becomes real.
-   Blog/Fediverse stay in the comm gateway for now; split-off as
    `work` with Maturity (own reputation logic).
-   The seven questions apply from now on to every gateway idea —
    retroactively as a touchstone for the existing ones as well.
