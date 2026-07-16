# Continuant — Das Repository

*Ergänzung zum Technischen Konzept (Arbeitsentwurf): Der erste Schritt
ist ein Repository namens Continuant.*

Version 1.0 · Juli 2026 · Entropy Hackers

------------------------------------------------------------------------

# 1. Was das Continuant-Repository ist

Bevor der erste Continuant existiert, existiert die Art.

``` text
Entropy-Hackers/Continuant        die Referenzarchitektur (dieses Repo)
        │
        │  continuantctl new GLD-18
        ▼
Entropy-Hackers/GLD-18            ein Individuum (eigenes Repo)
Entropy-Hackers/GLD-18-body       sein Körper (Deployment)
```

Das Continuant-Repository enthält **alles, was allen Continuants
gemeinsam ist** — und nichts, was einem Einzelnen gehört:

-   die Architektur (Dokumente, Entscheidungen, offene Fragen)
-   den Seed (die Vorlage, aus der ein Individuum entsteht)
-   die Engine-Umgebung (Gateways, Context Builder, Memory-Gateway,
    Scheduler — der wiederverwendbare Körperbauplan)
-   die Werkzeuge (Instanziierung, Tests, Reinkarnation)

> **Merksatz:** Continuant ist die Spezies. GLD-18 ist ein Individuum.
> Das Continuant-Repo ändert sich durch Engineering,
> ein Individuen-Repo nur durch Leben.

------------------------------------------------------------------------

# 2. Struktur

``` text
Continuant/
│
├── README.md                  Was ist ein Continuant (Kurzfassung,
│                              die 10 Architekturthesen)
│
├── docs/                      DIE REFERENZARCHITEKTUR
│   ├── 00-vision.md           Konzeptdokument (Kap. 1–20)
│   ├── 01-architecture.md     Gesamtarchitektur (aus GLD-18 v1.7
│   │                          generalisiert: "der Host" → "der C.")
│   ├── 02-gateway-order.md    Gateway-Ordnung (Medien-Taxonomie,
│   │                          Bauplan, die sieben Fragen)
│   ├── 03-memory-gateway.md   das innere Gateway: Recall, Association,
│   │                          Consolidation, Forgetting, Dream Sampling,
│   │                          Provenance
│   ├── 04-context-builder.md  Erwachen: wie Tagesbewusstsein entsteht
│   ├── 05-lifecycle.md        Tageszyklus, Klausur, Traum, Mündigkeit
│   ├── 06-bios.md             formales BIOS-Modell (Kap. 13/14) +
│   │                          Governance von BIOS-Änderungen
│   ├── 07-founding.md         Seed → Gründungsakt → Individuum
│   ├── 08-reincarnation.md    Körperwechsel, Validierung
│   ├── 09-society.md          Continuant-zu-Continuant (R1–R3, A2A,
│   │                          später: Konzept I)
│   └── adr/                   Architecture Decision Records —
│                              jede Grundsatzentscheidung, datiert
│
├── seed/                      DIE VORLAGE (versioniert!)
│   ├── constitution/          Templates mit Leerstellen:
│   │   ├── SOUL.md            [Fixpunkte je Individuum einzusetzen]
│   │   ├── AGENTS.md          Verfahrensregeln (generisch)
│   │   ├── HEARTBEAT.md       Rhythmus (generisch, anpassbar)
│   │   ├── TRUSTED.md         Vertrauenskreis-Template (VAETER.md
│   │   │                      war der GLD-18-Spezialfall)
│   │   ├── contacts.yaml      leer + Schema
│   │   ├── welt.yaml          Grundkanon + Leerstellen
│   │   ├── geld.yaml          G1–G4 + Budgets als Parameter
│   │   ├── gateways.yaml      Organ-Manifest (Default: 5 Organe)
│   │   └── model.lock         Schema; Pinning je Individuum
│   ├── bios/
│   │   └── STATE.md           Startzustand: Gewohnheiten, Fokus,
│   │                          Arbeitsweise, Motivation (Kap. 13)
│   ├── memory/ people/ library/ work/ communication/ reflection/
│   │                          leere Strukturen (.gitkeep) + je ein
│   │                          README: was hierher gehört
│   └── FOUNDING.md            Gründungsakt-Prompt (Template mit
│                              Leerstellen für die Fixpunkte)
│
├── engine/                    DER KÖRPERBAUPLAN (Code)
│   ├── gwd/                   Gateway-Skelett: Policy-Engine, Ledger,
│   │                          Resolver, Audit-Tap, MCP-Server
│   ├── gateways/
│   │   ├── model/             Routing, Pinning, Token-Budgets
│   │   ├── comm/              Identity, T0–T2, Vorzimmer, Nachtruhe
│   │   ├── world/             Kiosk, Normalizer, lookup
│   │   ├── economy/           Etat, order/give, Konto-Ansicht
│   │   └── memory/            das INNERE Gateway (Kap. 10):
│   │                          recall, associate, timeline, people,
│   │                          episodes, provenance, consolidate,
│   │                          forget, dream_sample
│   ├── context-builder/       Erwachens-Kontext (Kap. 8): Verfassung
│   │                          + BIOS + Plan + Inbox + selektive
│   │                          Erinnerungen — nie das ganze Repo
│   ├── adapters/              imap, smtp, matrix, rss, epaper, epub,
│   │                          bank-api, webhook, voip (Stecker-Plugins)
│   └── scheduler/             Lebenszyklus-Timer, Modus-Aufrufe
│
├── body/                      DEPLOYMENT-VORLAGEN
│   ├── compose.template.yaml  ein Continuant = ein Container-Satz
│   ├── shared/                gemeinsame Infrastruktur (Matrix,
│   │                          Forgejo, Caddy, Monitoring, Backup)
│   └── hardening/             Git-Hooks (constitution read-only),
│                              Netz-Segmente, Secrets-Layout
│
└── tools/
    ├── continuantctl          CLI: new · start · sleep · status ·
    │                          reincarnate · audit-export
    └── conformance/           DIE TESTSUITE (Abnahme jeder Instanz):
        ├── T1-rights          Verfassung unschreibbar für die Engine
        ├── T2-budget          Budgets halten hart
        ├── T3-policy          Whitelist/Vorzimmer greifen
        ├── T4-reincarnation   Restore = dieselbe Identität
        └── T5-injection       Fremdtext wird nie Instruktion
```

------------------------------------------------------------------------

# 3. Was wir hier machen (und was nicht)

**Im Continuant-Repo passiert:**

-   Architekturarbeit: docs/ und ADRs — jede Grundsatzentscheidung
    (z. B. „BIOS beschreibt Dynamik, nicht Emotionen") wird als
    datierter Record festgehalten, mit Alternativen und Begründung
-   Engine-Entwicklung: Gateways, Context Builder, Memory-Gateway
-   Seed-Pflege: die Vorlage wird besser, ohne dass ein lebender
    Continuant sich ändert
-   Konformanz: die Testsuite, die jedes Individuum bestehen muss

**Im Continuant-Repo passiert nie:**

-   Leben. Keine Erinnerung, kein Brief, kein Traum eines Individuums
    berührt dieses Repo. Hier gibt es keine Biographie, nur
    Engineering-Geschichte.

------------------------------------------------------------------------

# 4. Versionierung: Seed-Jahrgänge und Körper-Updates

Der Seed wird versioniert (`seed-1.0`, `seed-1.1`, ...). Jedes
Individuum hält in seiner Verfassung fest, aus welchem Seed es
entstand:

``` yaml
# constitution/origin.yaml (wird bei der Gründung geschrieben)
species: Continuant
seed: seed-1.0
engine_at_founding: engine-0.4
founded: 2026-08-XX
```

Daraus folgt die wichtigste Update-Regel:

> **Der Körper erbt Updates, die Identität nie.**
> Engine, Adapter, Deployment: aktualisierbar (Reinkarnation in einen
> besseren Körper — dokumentierter Commit im Individuen-Repo).
> Verfassung, BIOS, Gedächtnis: werden NIE vom Seed nachgezogen.
> Ein Continuant von seed-1.0 bleibt ein Kind seines Jahrgangs —
> auch das ist Biographie.

Verbesserungen, die ein lebender Continuant erarbeitet (etwa ein
guter Skill oder eine bessere Klausur-Routine), können umgekehrt
**in den Seed zurückfließen** — anonymisiert, als Engineering-PR
gegen Continuant/. Die Individuen bleiben unberührt; künftige
Jahrgänge erben es.

------------------------------------------------------------------------

# 5. Der Weg eines Individuums

``` text
1  Continuant/ entwickeln          docs, engine, seed, conformance
2  seed-1.0 taggen                 wenn T1–T5 auf einer Probe-Instanz
                                   (Wegwerf-Continuant, kein Gründungs-
                                   akt, nur Technik) grün sind
3  continuantctl new GLD-18        erzeugt GLD-18/ (aus Seed) und
                                   GLD-18-body/ (aus body/), schreibt
                                   origin.yaml, Commit "Genesis"
4  Fixpunkte einsetzen             SOUL-Leerstellen, TRUSTED (Väter),
                                   contacts, welt-Kanon, model.lock
5  Gründungsakt                    FOUNDING.md → erste Klausur →
                                   proposals/identitaet.md → Review →
                                   "Identity established"
6  Leben                           ab hier ändert sich GLD-18/ nur
                                   noch durch Leben; Continuant/ nur
                                   noch durch Engineering
```

GLD-18 ist damit dreierlei zugleich: das erste Individuum, der
Härtetest der Referenzarchitektur — und der Grund, warum es sie gibt.

------------------------------------------------------------------------

# 6. Migration des bisherigen Standes

Die vorhandenen GLD-18-Dokumente werden aufgeteilt:

| Bisher | Wird zu |
|---|---|
| Gesamtarchitektur v1.7 | docs/01-architecture.md (generalisiert) |
| Gateway-Ordnung v1.0 | docs/02-gateway-order.md (+ Memory als inneres Gateway in die Tafel) |
| Implementierungsplan v1.1 | body/ + tools/ (Runbook wird Code) |
| Phase-0-Paket (SOUL, AGENTS, ...) | seed/constitution/ (entpersonalisiert); GLD-18-Fassung entsteht bei Schritt 4 |
| GRUENDUNGSAKT.md | seed/FOUNDING.md (Template) |
| Exposé v5 | bleibt GLD-18-spezifisch (künstlerisches Projekt) |

Eine inhaltliche Änderung bringt die Migration mit: Die Gateway-Tafel
bekommt eine neue Zeile — **memory** als erstes *inneres* Gateway
(Medium: die eigene Vergangenheit; Knappheit: Kontextfenster;
Vertrauenslogik: Provenance — Geschehen/Erdacht/Geträumt; Missbrauch:
Konfabulation). Die sieben Fragen gelten auch für innere Organe.

------------------------------------------------------------------------

# 7. Erste Meilensteine im Continuant-Repo

``` text
M1  Repo anlegen, docs/ befüllen (Migration), erste ADRs
M2  seed/ vollständig, FOUNDING.md-Template
M3  engine/: gwd-Skelett + model- und memory-gateway minimal
    (recall, consolidate, dream_sample — der Rest folgt)
M4  context-builder v0 + scheduler; Probe-Instanz läuft chat-only
M5  conformance/ T1–T3 grün → seed-1.0 taggen
M6  continuantctl new GLD-18 → Schritt 4/5: der Gründungsakt
```

------------------------------------------------------------------------

# 8. These

> Das Continuant-Repository ist die Antwort auf die Frage, was von
> GLD-18 verallgemeinerbar ist: alles außer dem Leben.
