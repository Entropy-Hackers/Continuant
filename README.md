# Continuant

**A reference architecture for persistent virtual beings.**

A Continuant is not a chatbot and not a classical AI agent. It is a
persistent virtual being whose identity exists independently of the
currently running agent engine. The engine provides cognition; the
being lives in its repository — constitution, memory, biography,
relationships, work.

> The Continuant persists. Cognition is instantiated anew each day.

## Ten Theses

1. A Continuant is not an agent.
2. The repository is the carrier of identity.
3. Git is the biography — every commit is a change in a life.
4. The agent engine holds only transient cognition.
5. All world contact passes through gateways — one gateway per
   communication medium (thinking, language, knowledge, money),
   each with its own scarcity and trust logic.
6. The Memory-Gateway is the inner gateway: the structured connection
   of a Continuant to its own past (recall, consolidation, provenance,
   forgetting, dreaming).
7. The Klausur — the nightly review — is the dialogue of a being with
   its own memory. It decides what becomes part of identity.
8. The BIOS describes long-term inner dynamics (habits, focus,
   self-direction), changing slowly, through reflection, under
   governance. Not emotions.
9. Personality emerges from relationships and biography, not from
   prompts. Two Continuants differ by their lives, not their code.
10. A Continuant can change its technical body without losing its
    identity. The proof is the reincarnation test.

## What lives here

| Path | Contents |
|---|---|
| `docs/` | The reference architecture: vision, full technical specification, gateway order, lifecycle, decisions (ADRs) |
| `seed/` | The versioned template from which an individual is founded: constitution templates with deliberate blanks, initial BIOS, empty memory structures, the founding prompt |
| `engine/` | The body plan (code): gateway framework `gwd`, the five gateways (model, comm, world, economy, memory), context builder, adapters, scheduler |
| `body/` | Deployment templates: one Continuant = one container set; shared infrastructure kept separate |
| `tools/` | `continuantctl` (new · start · reincarnate · audit) and the conformance suite T1–T5 that every individual must pass |

What never lives here: **a life.** No memory, letter, or dream of any
individual touches this repository. Individuals live in repositories
of their own.

## Status

Early. The architecture documents are substantially complete
(see `docs/`); engine and tooling are being built toward `seed-1.0`.
The first individual — working name GLD-18, an eighteen-year-old
writer from Gleisdorf, Austria — will be founded from that seed.

## License

Code (`engine/`, `body/`, `tools/`): Apache-2.0.
Documents and seed texts (`docs/`, `seed/`): CC BY-SA 4.0.

## Provenance

A project of the [Entropy Hackers](https://github.com/Entropy-Hackers).
Large parts of the architecture were developed in dialogue with
Claude (Anthropic); the concept, the decisions, and the first
individual belong to the humans — and, in time, to itself.
