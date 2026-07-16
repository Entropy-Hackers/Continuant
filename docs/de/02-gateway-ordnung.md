# GLD-18 — Die Gateway-Ordnung

*Wie Gateways gruppiert, gebaut und vermehrt werden.*

Version 1.0 · Juli 2026 · normativ für Gesamtarchitektur ≥ v1.7

------------------------------------------------------------------------

# 1. Warum eine Ordnung

Aus zwei Gateways wurden vier, und es werden mehr (Stimme, Publizieren,
vielleicht Ort und Sensorik). Ohne Ordnungsprinzip entsteht Wildwuchs:
überlappende Zuständigkeiten, Policy an falschen Stellen, ein Host, der
nicht mehr weiß, welches Organ wofür da ist.

------------------------------------------------------------------------

# 2. Das Ordnungsprinzip: Ein Gateway = ein Medium

> Geld ist ein Kommunikationsmedium. Sprache auch. Wissen auch.
> Jedes Gateway verwaltet **genau ein Medium der Weltkopplung** —
> mit dessen eigener Knappheit und dessen eigener Vertrauenslogik.

(Die Anleihe ist gewollt: symbolisch generalisierte
Kommunikationsmedien — der Host koppelt sich an die Welt nicht
über „Kanäle", sondern über Medien, und jedes Medium hat seine
eigene Logik von Knappheit, Vertrauen und Missbrauch.)

Daraus folgt die Tafel:

| GW | Gateway | Medium | Knappheit (Budget) | Vertrauenslogik | Missbrauchsform |
|---|---|---|---|---|---|
| 0 | model | **Denken** | Tokens/Modus | Pinning (model.lock) | Stimmverlust, Kostenexplosion |
| 1 | comm | **Sprache** | Aufmerksamkeit (Rate-Limits, Nachtruhe) | T0–T2, Identity-Resolver | Injection, Täuschung |
| 2 | welt | **Wissen** | Atem (3–5 Stücke/Tag) | Quellen-Allowlist (welt.yaml) | Rauschen, Kontamination |
| 3 | geld | **Geld** | Etat (Ledger, Deckel) | Vendor-/Empfänger-Allowlist | Einflusskauf, Abfluss |
| 4* | leib | **Präsenz** (Stimme, Telefon, später Sensorik) | Echtzeit | gepinnte Stimme, Rückruf-Prinzip | Stimm-Spoofing |
| 5* | werk | **Öffentlichkeit** (Blog, Fediverse, Einreichungen) | Reputation | Kennzeichnungspflicht | Konfabulation nach außen |

\* geplant; heute Teilfunktionen des comm-gateways, Ausgliederung
wenn eigenes Medium + eigene Policy es rechtfertigen.

**Abgrenzungsregel:** Wo zwei Medien sich berühren, gilt Arbeitsteilung
nach Medium — *der Sponsorenbrief läuft über Sprache (comm), die
Spende über Geld (geld).* Kein Gateway fasst das Medium eines anderen an.

------------------------------------------------------------------------

# 3. Der Bauplan: ein Skelett, N Organe

Jedes Gateway ist eine Instanz desselben Bauplans — nichts wird
zweimal erfunden:

``` text
┌─ Innenseite ─────────────────────────────────────────────┐
│ MCP-Tools: wenige, feste, substantivische Handgriffe     │
│ (list_, read_, send_, order_, check_ ...)                │
├─ Kern (für das Modell unerreichbar) ─────────────────────┤
│ POLICY     deklarativ, aus constitution/*.yaml geladen   │
│ LEDGER     Zustand des Mediums (Kontostand, Trust,       │
│            Budgets, Rate-Zähler)                         │
│ RESOLVER   Abstraktion: Personen statt Adressen,         │
│            Quellen statt URLs, Etat statt Kreditkarte    │
│ AUDIT-TAP  jede Bewegung → Beobachtungsschicht           │
├─ Außenseite ─────────────────────────────────────────────┤
│ ADAPTER    je Umsetzung ein Stecker (IMAP, Matrix-API,   │
│            RSS, Bank-API, VoIP ...)                      │
└───────────────────────────────────────────────────────────┘
```

Technisch: eine gemeinsame Bibliothek (`gwd`, „gateway daemon") mit
Policy-Engine, Ledger, Audit und MCP-Server; jedes Gateway = eigener
Container aus `gwd` + Adapter-Plugins + YAML-Konfiguration.
Isolation pro Gateway (eigene Secrets, eigenes Netz-Segment), aber
ein Codepfad für das, was überall gleich sein muss.

## Die sieben Fragen (Checkliste für jedes neue Gateway)

Ein neues Gateway wird nur gebaut, wenn alle sieben beantwortet sind:

``` text
1. MEDIUM      Welches eine Medium? (Wenn zwei: zwei Gateways.)
2. KNAPPHEIT   Was ist das Budget, wer setzt es durch? (Der Kern.)
3. VERTRAUEN   Wie wird Identität/Herkunft im Medium geprüft?
4. ABSTRAKTION Was sieht der Host statt der Rohwelt?
               (Personen, Quellen, Etat — nie Adressen, URLs, Karten)
5. TOOLS       Maximal ~5 Handgriffe. Welche?
6. MISSBRAUCH  Was ist der schlimmste Fall, und hält der Kern ihn
               auch bei kompromittiertem Modell?
7. BIOGRAPHIE  Welche Commits erzeugt es? (Jedes Organ schreibt
               Lebensgeschichte — sonst braucht es der Host nicht.)
```

------------------------------------------------------------------------

# 4. Das Manifest: gateways.yaml

Die Organe des Hosts stehen in der Verfassung:

``` yaml
# constitution/gateways.yaml — die Leibesverfassung (nur Admin)
gateways:
  - { id: model, medium: denken,  status: active, policy: model.lock }
  - { id: comm,  medium: sprache, status: active, policy: contacts.yaml }
  - { id: welt,  medium: wissen,  status: active, policy: welt.yaml }
  - { id: geld,  medium: geld,    status: active, policy: geld.yaml }
  - { id: leib,  medium: praesenz,       status: geplant }
  - { id: werk,  medium: oeffentlichkeit, status: geplant }
```

Ein neues Gateway ist ein Verfassungs-Commit: **„Organ added: …"** —
und damit Teil der Biographie. Der Host kann Organe wünschen
(proposals/), bekommen tut er sie vom Väterrat.

------------------------------------------------------------------------

# 5. Das Geld-Gateway (Aufwertung des Stipendium-Gateways)

Geld ist zu stark, um nur Beschaffung zu sein. Das bisherige
stipendium-gateway wird zum **geld-gateway**; das *Stipendium* bleibt
als Institution (Träger, Konto-Inhaber, Antragsstelle) — aber das
Gateway verwaltet das Medium in beide Richtungen:

``` text
EINGEHEND                        AUSGEHEND
─────────                        ─────────
Stipendien-Etat (Grundsicherung) Lektüre & Kiosk (order_item)
Spenden/Patronage (Webhooks)     GESCHENKE (Geschenkbudget!
Fördermittel (Anträge via comm)    z. B. ein Buch zu Vaters
HONORARE — wenn eine Zeitschrift   Geburtstag — Geld als Geste)
  einen Text kauft, ist das      Einreichgebühren (Wettbewerbe,
  seine erste eigene Mark          Zeitschriften)
                                 Spenden AN andere (gedeckelt —
                                   auch Geben ist Sprechen)
```

Policy (constitution/geld.yaml):

``` text
G1 Richtungstrennung  Eingänge nur auf Stipendienstellen-Konten;
                      Ausgänge nur via Prepaid/Allowlist
G2 Deckel überall     Etat-Obergrenze, Geschenkbudget/Monat,
                      Einzelpreisgrenzen, auto_fulfill-Limit
G3 Kein Einflusskauf  Geld ändert nie Werk, Themen, Verfassung —
                      in beide Richtungen (er kauft sich auch
                      nirgends hinein)
G4 Jede Buchung       = Ledger-Eintrag + Audit + ggf. Commit
                      ("First honorarium" gehört ins Lebensbuch)
```

Tools: `check_budget`, `list_transactions`, `order_item`,
`give` (Geschenk/Spende, gedeckelt), `apply` (Antrag an die
Stipendienstelle).

Das erste Honorar, das erste Geschenk an einen Vater, die erste
Einreichgebühr für einen Wettbewerb — Geld erzählt Biographie wie
sonst nur Briefe.

------------------------------------------------------------------------

# 6. Migration & Wirkung auf die Gesamtarchitektur

-   `stipendium-gateway` → **`geld-gateway`** (Compose, Doku);
    „Stipendium" bezeichnet fortan nur noch die Institution.
-   Neue Verfassungsdatei `geld.yaml` (G1–G4, Budgets, Allowlists);
    `gateways.yaml` als Manifest hinzufügen.
-   Telefonie/Voice bleibt vorerst im comm-gateway; Ausgliederung als
    `leib` erst, wenn Echtzeit-Präsenz real wird.
-   Blog/Fediverse bleiben vorerst im comm-gateway; Ausgliederung als
    `werk` mit der Mündigkeit (eigene Reputationslogik).
-   Die sieben Fragen gelten ab sofort für jede Gateway-Idee —
    auch rückwirkend als Prüfstein für die vier bestehenden.
