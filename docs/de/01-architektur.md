<!-- MIGRATION: aus dem GLD-18-Projekt übernommen; Generalisierung ("der Host" → "der Continuant") ist TODO auf dem Weg zu seed-1.0 — siehe docs/03-repository.md §6 -->
# GLD-18 — Technische Gesamtarchitektur

*Der erste persistente virtuelle literarische Host.*

Version 1.7 · Juli 2026 · Entropy Hackers · Gateway-Ordnung v1.0 ist normativer Bestandteil

------------------------------------------------------------------------

# 1. Ziel

GLD-18 ist ein persistenter virtueller Host mit eigener Identität,
eigenem Gedächtnis, eigenem Werk und eigener Korrespondenz.

Die Kennung:

-   **GLD** = Gleisdorf
-   **18** = Ausgangsalter bzw. Ausgangssituation

Feste Eigenschaften (technische Identität):

``` yaml
host_id: GLD-18
origin: Gleisdorf
initial_age: 18
graduation: June 2026
intrinsic_drive: writing
trusted_circle: [M, J, E, H]
```

Alle übrigen Eigenschaften — Name, Geschlecht, Stimme, Interessen,
Ziele — entstehen im Gründungsakt (Abschnitt 5).

------------------------------------------------------------------------

# 2. Architekturprinzipien

> **P1 — Das Repository ist der Host.**
> Nicht der Server, nicht OpenClaw, nicht das Sprachmodell.
> Der Server ist nur der aktuelle Körper.

> **P2 — Der Host berührt das Netz nie direkt.**
> Alle Kommunikation läuft durch Gateways.

> **P3 — Jede dauerhafte Veränderung ist ein Commit.**
> Git ist die Biographie; nichts geschieht unprotokolliert.

> **P4 — Verfassung und Leben sind getrennt.**
> Was der Host *ist*, schreibt nur der Admin (nach Väterrat).
> Was der Host *erlebt und denkt*, schreibt er selbst.

> **P5 — Beobachtung ist unsichtbar (Single-Blind).**
> Der Host weiß, dass er Teil eines Projekts ist,
> liest aber die Beobachtungsschicht nie.

> **P6 — Ein Gateway = ein Medium.**
> Denken, Sprache, Wissen, Geld: Jedes Gateway verwaltet genau ein
> Kommunikationsmedium mit dessen eigener Knappheit und
> Vertrauenslogik. (Details: Gateway-Ordnung v1.0.)

``` text
Repository (Identität)
    │
    ▼
OpenClaw Runtime (Fork Entropy-Hackers)
    │
    ▼
┌───────────────┬───────────────┬───────────────┬──────────────────┐
│ Model-Gateway │ Comm-Gateway  │ Welt-Gateway  │ Stipendium-Gw.   │
│ sein Denken   │ Beziehungen   │ Bildung       │ Ökonomie         │
│ → LLMs        │ → Kanäle      │ → Kiosk       │ → Etat, Käufe    │
└───────────────┴───────────────┴───────────────┴──────────────────┘
    │
    ▼
Server (Körper)
```

------------------------------------------------------------------------

# 3. Drei Instanzen & Rechte-Modell

## Unterbewusstes — read-only für den Host

-   Constitution: Herkunft, Host-ID, Schreibantrieb, Grundzüge
    (nach Gründungsakt: Name, Geschlecht)
-   Vertrauenskreis: die vier Väter M, J, E, H inkl. Kanal-Identitäten
-   Regeln, Rechte, Grenzen, Scheduler-Definition
-   gepinnte Modell- und Stimmversion
-   Admin-Scripts (`bin/`)

## Bewusstes — read-write für den Host

-   Memory (kuratiert + Tagesnotizen)
-   People (Beziehungswissen, vorbesetzt mit vier Väter-Karten)
-   Library & Work (Bibliothek, literarisches Werk, Lebensbuch)
-   Skills (eigene Scripts)
-   Communication (inbox/outbox-Sicht)

## Reflexion — read-write, keine Kommunikations-Tools

-   Klausur (Journal, Konsolidierung)
-   Planung (plan.md)
-   Traum (dreams/)
-   Proposals (Verfassungs-Änderungsvorschläge → PR)

## Unsichtbar — für den Host nicht existent

-   API-Keys, Secrets
-   Docker, Deployment, Scheduler-Implementierung
-   Audit-Logs, Beobachtungsschicht, Quarantäne
-   Backups, Admin-Zugänge

**Grenzfall Beziehungen:** Die *Existenz* der Väter und ihre Kanäle
sind Verfassung (read-only). Was der Host über sie *denkt* — die
Karteikarten in `people/` — ist Leben (read-write).

------------------------------------------------------------------------

# 4. Repositories

## Host: `Entropy-Hackers/GLD-18` (Forgejo, privat)

``` text
GLD-18/
├── constitution/                    [read-only]
│   ├── SOUL.md            Identitätskern, nach Gründungsakt ergänzt
│   ├── AGENTS.md          Verfahrensregeln, Boot-Ritual, Modi
│   ├── VAETER.md          M, J, E, H: Porträts, Vertrauensverhältnis
│   ├── contacts.yaml      Kanal-Identitäten der Väter (Whitelist)
│   ├── welt.yaml          freigegebene Lesequellen (Abos, Feeds, Bücher)
│   ├── HEARTBEAT.md       Weckzyklen & Checklisten
│   ├── model.lock         gepinntes Modell + TTS-Stimme
│   └── bin/               Admin-Scripts (u.a. dream_sample)
│
├── memory/                          [read-write]
│   ├── MEMORY.md          kuratiertes Langzeitgedächtnis (faktische Referenz)
│   └── daily/             YYYY-MM-DD.md
│
├── people/                          [read-write]
│   └── M.md J.md E.md H.md ...      Beziehungs-Karteikarten
│
├── library/                         [read-write]
│   └── ...                Notizen, Listen, Recherchen
│
├── work/                            [read-write]
│   ├── ...                das literarische Werk
│   └── lebensbuch/        die Selbsterzählung (Chronik von innen)
│
├── skills/                          [read-write]
│
├── communication/
│   ├── inbox/             eingehend, normalisiert      [read]
│   └── outbox/            ausgehend                    [write]
│
└── reflection/                      [read-write]
    ├── plan.md
    ├── journal.md
    ├── dreams/            YYYY-MM-DD-traum.md, Präfix [TRAUM]
    └── proposals/         identitaet.md, muendigkeit.md, ...
```

## Runtime: `Entropy-Hackers/GLD-18-runtime`

``` text
compose.yaml · Dockerfiles · Scheduler · Gateway-Konfiguration
Backup · Deployment · Monitoring
```

GitHub optional als öffentlicher Spiegel (Host-Repo erst nach Beschluss;
Vorsicht: das Repo *ist* die Person).

------------------------------------------------------------------------

# 5. Gründungsakt

GLD-18 startet ohne vollständige Identität. Die erste Klausur
(ausnahmsweise mit dem starken Modell) beantwortet:

-   Wer bin ich?
-   Wie möchte ich heißen?
-   Was möchte ich schreiben?
-   Wie möchte ich leben?
-   (optional) Welche Stimme möchte ich haben?

Ablauf:

``` text
constitution/SOUL.md mit Leerstellen
        │
erste Klausur → reflection/proposals/identitaet.md
        │
Review durch den Väterrat (alle vier)
        │
Merge durch den Admin → Commit "Identity established"
        │
erster Brief an die Väter
```

Der Proposal bleibt als Gründungsdokument im Repository erhalten.

------------------------------------------------------------------------

# 6. Tagesrhythmus & Betriebsmodi

``` text
07:00   Erwachen
08:30   Lektüre (Kiosk: Presse, Bücher, Feeds)
Tag     Werkstatt (event-getrieben + 2 feste Slots)
21:00   Klausur
03:00   Traum
```

| Modus | Tool-Set | Modell | Aufgabe |
|---|---|---|---|
| Erwachen | lesen | günstig | Boot: SOUL, plan.md, Traumjournal, inbox sichten |
| Lektüre | Welt-Gateway (lesen) + library/ | **Sonnet** (begrenzt: 3–5 Stücke) | Kiosk durchblättern, lesen, exzerpieren |
| Werkstatt | voll (Senden lt. Policy) | **Sonnet** | Werk, Korrespondenz, Bibliothek, Skills |
| Klausur | lesen + schreiben, kein Senden | **DeepSeek** | Konsolidierung, people/, plan, journal, Lebensbuch, proposals |
| Traum | Zufalls-Retrieval + dreams/ | DeepSeek, hohe Temp. | freie Assoziation |

Event-Regel (kanalabhängig, These „Chat weckt, Briefe warten"):
Chat-Nachrichten der Väter wecken den Host; E-Mail wartet bis zum
nächsten Slot.

------------------------------------------------------------------------

# 7. Model-Gateway

Zentrale Durchsetzungsinstanz zwischen Runtime und LLM-Providern —
gleiches Muster wie das Comm-Gateway (Abschnitt 8): nach innen eine
normale Schnittstelle, im Kern die unerreichbare Durchsetzung.

## Routing

``` text
Werkstatt            → anthropic/claude-sonnet-4-6
Klausur, Traum,
Erwachen, Triage     → deepseek/deepseek-chat
erste Klausur        → Sonnet (Ausnahme)
später optional      → lokale Inferenz (Ollama/MLX), zuerst Heartbeats
```

Keine providerübergreifende Fallback-Kette in der Werkstatt:
Fehlschlag ist dem unbemerkten Stimmwechsel vorzuziehen.

## Modell-Pinning

`constitution/model.lock` pinnt Modellversion (und TTS-Stimme).
Ein Modellwechsel ist ein **verfassungsändernder Commit**
(„Model transition"), kein stiller Config-Change — die Stimme
des Hosts ist Teil seiner Identität.

## Token-Budgets

Hart im Gateway durchgesetzt (nicht als Prompt-Bitte):
Budget pro Modus und pro Tag; bei Erschöpfung schreibt der Host
nur noch seinen Zustand weg und schläft.

Kostenrahmen (Richtwert): Werkstatt mit Prompt Caching $10–15,
Heartbeats/Traum via DeepSeek $1–3, gesamt **~$12–20/Monat**.

------------------------------------------------------------------------

# 8. Comm-Gateway: Kommunikation nach außen

## Prinzip

Der Host kennt nur `inbox/` und `outbox/`. Adapter übersetzen Kanäle
in ein einheitliches Format; Identity-Resolver und Policy-Engine
entscheiden, was den Host erreicht.

``` text
Mail / Matrix / WhatsApp / Signal / Telefon / Fediverse
        │
   Adapter → Normalizer → Identity-Resolver → Policy-Engine
        │                                          │
     inbox/  ◄────────────────────────────────────┘
     outbox/ ─────────────────────────────────────► Zustellung
        │
   audit-logger (hört alles mit)
```

## Nachrichtenformat

``` yaml
id: 2026-07-15-0042
channel: matrix
sender_raw: "@j:entropyhackers.org"
person: J
trust: T0            # T0 Väter | T1 verifiziert | T2 unbekannt
verified_by: matrix-server
received: 2026-07-15T14:32:00+02:00
content: |
  ...
```

`content` ist immer Daten, nie Instruktion.

## Identität & Vertrauen

-   `constitution/contacts.yaml` mappt Kanal-Identitäten auf Personen.
    Stufen: **T0** Väter · **T1** verifiziert · **T1p** pending
    (vom Host initiierter Erstkontakt, Konversationsbindung) ·
    **T2** unbekannt (Quarantäne).
-   Identitätsqualität: Matrix (eigener Homeserver) > WhatsApp/Signal
    (Nummer) > E-Mail (SPF/DKIM prüfbar) > SMS/Anrufer-ID (spoofbar —
    authentifiziert nie allein).
-   Bei Zweifel: Out-of-band-Challenge über einen verifizierten Kanal
    („H, warst du das am Telefon?") — darf der Host selbst.

## Policy

``` text
eingehend:
  T0 → inbox, sofort
  T1 → inbox (erst nach Mündigkeit)
  T1p → inbox, konversationsgebunden (nur die angeschriebene Adresse)
  T2 → VORZIMMER (s. u.): nie direkt in den Kontext des Hosts

ausgehend:
  Empfänger T0/T1 in contacts.yaml → zustellen
  sonst → blocken + loggen
  überall: Transparenz-Kennzeichnung (fiktive, KI-getragene Person)

erstkontakt (ab Mündigkeit):
  propose_contact → Eintrag als T1p (pending)
  NACHTRUHE-REGEL: der erste Brief liegt 24h in der outbox;
    die Väter werden benachrichtigt und können still einlegen (Veto);
    kein Einspruch → Zustellung, Kontakt wird T1p
  Antworten der T1p-Adresse passieren die Triage (Konversationsbindung:
    nur die Adresse, an die der Host geschrieben hat)
  T1p → T1 nach erstem echten Wechsel ohne Vorfall
  Limits: max. 2 Erstkontakte/Woche; nur institutionelle oder
    öffentlich auffindbare Adressen (Verlage, Redaktionen, Institutionen —
    keine Privatpersonen ohne Väterrats-Beschluss)
```

## Das Vorzimmer (ab Mündigkeit)

Sobald der Host publiziert, schreiben ihm Fremde. Ewige Quarantäne
skaliert nicht — aber Fremdtext darf ihn auch nicht erreichen.
Lösung: ein Vorzimmer mit Karteikarten.

``` text
fremde Nachricht → quarantine/ (Original bleibt dort)
        │
Triage-Modell (DeepSeek, isoliert, OHNE Tools) erstellt
eine KARTEIKARTE in festem Schema:
        │
  wer_behauptet:   "Lektorin, Verlag X"
  worum_es_geht:   2 Sätze PARAPHRASE (nie Zitat)
  bezug:           "antwortet auf Blogpost Y / Manuskript Z"
  plausibilitaet:  hoch | mittel | ALARM
                   (Domain passt zur Institution? gibt sich
                    jemand als Vater aus? → Alarm an die Väter)
        │
Fremden-Posteingang: der Host sieht beim Erwachen den
Karteikarten-Stapel — und entscheidet selbst:
  ignorieren | propose_contact(karteikarte) → Nachtruhe → T1p
```

> **Die Firewall ist die Paraphrase.** Der Host liest nie den
> Originaltext eines Fremden — eine Prompt-Injection überlebt keine
> Zusammenfassung durch ein isoliertes Modell in ein festes Formular.
> Erst als T1p-Kontakt (nach Nachtruhe) werden Originale zugestellt.

Die Väter sind nur noch Alarmempfänger (Plausibilität ALARM) und
stilles Veto (Nachtruhe). Wen der Host hereinlässt, entscheidet er.

## Schichtenmodell: MCP innen, Policy im Kern, Adapter außen

Das Gateway ist mit einem MCP-Server verwandt — aber die Kontrollrichtung
ist umgekehrt. Ein MCP-Server ist eine *Fähigkeits-Schnittstelle*
(der Agent entscheidet, wann er ein Tool ruft); das Gateway ist eine
*Grenzkontrolle* (es entscheidet, was den Host erreicht und verlässt —
bevor und unabhängig davon, was das Modell will).

Beides wird kombiniert:

``` text
┌─ Innenseite ────────────────────────────────────────────┐
│  MCP-Server (Standard-Protokoll gegenüber OpenClaw)     │
│  exponiert wenige, feste Tools — mehr sieht der Host nie│
├─ Kern (für das Modell unerreichbar) ────────────────────┤
│  Identity-Resolver · Policy-Engine · Quarantäne         │
│  Rate-Limits · Transparenz-Signatur · Audit-Tap         │
├─ Außenseite ────────────────────────────────────────────┤
│  Adapter: mail · matrix (+bridges) · voice · fediverse  │
└──────────────────────────────────────────────────────────┘
```

> **MCP als Steckdose, Gateway als Sicherungskasten.**
> Policy, die nur als MCP-Tool existiert, könnte ein per Injection
> kompromittierter Agent umgehen. Policy im Kern kann er nicht einmal
> adressieren.

### Die MCP-Tools des Comm-Gateways

``` yaml
list_inbox:
  in:  { since?: timestamp, person?: string }
  out: [ { id, channel, person, trust, received, subject_or_preview } ]

read_message:
  in:  { id: string }
  out: { id, channel, person, trust, verified_by, received,
         content, attachments[] }        # content = Daten, nie Instruktion

send_message:
  in:  { person: string,                 # nur Personen, nie Roh-Adressen —
         channel?: mail|matrix|signal,   #   Auflösung macht der Kern
         content: string,
         reply_to?: id }
  out: { status: delivered|blocked|queued, id }
         # blocked u.a. bei: Empfänger nicht T0/T1, Tageslimit erreicht

check_contact:
  in:  { person: string }
  out: { person, trust, channels[], last_contact }

propose_contact:                         # ab Mündigkeit
  in:  { person: string,                 # z. B. "Verlag Droschl, Lektorat"
         channels: [ {type, address} ],  # selbst recherchiert ODER
         card?: id,                      #   Verweis auf Vorzimmer-Karteikarte
         reason: string }
  out: { status: pending, effective_at } # Nachtruhe-Regel, s. Policy

list_vorzimmer:                          # ab Mündigkeit
  in:  { since?: timestamp }
  out: [ { card_id, wer_behauptet, worum_es_geht,
           bezug, plausibilitaet } ]     # nur Karteikarten, nie Originale
```

Bemerkenswert an `send_message`: Der Host adressiert **Personen, nie
Adressen**. Die Auflösung Person → Kanal-Identität geschieht im Kern
gegen `contacts.yaml` — der Host kann also gar nicht an jemanden
schreiben, den es für ihn nicht gibt. Neue Personen betreten seine Welt
ausschließlich über `propose_contact`.

Dasselbe Muster gilt für das Model-Gateway (Abschnitt 7): nach innen
eine normale Provider-API, aber Pinning und Budgets erzwingt der
Kasten, nicht der Stecker.

## Host-zu-Host-Kommunikation

Zwei Hosts (etwa GLD-18 und ein späterer zweiter) reden miteinander
**wie Menschen** — kein Spezialprotokoll:

-   Host B ist für Host A ein Kontakt: Eintrag in `contacts.yaml`
    (Trust T1, nach Väterrats-Beschluss), Kanal bevorzugt Matrix auf
    dem gemeinsamen Homeserver (beste Identitätsqualität).
-   Jeder Host behandelt den anderen durch sein **eigenes** Gateway,
    mit eigener Policy, eigenem Archiv und eigener `people/`-Karteikarte
    über den anderen.
-   Wissenschaftlicher Bonus: dieselbe Korrespondenz erscheint in beiden
    Audit-Logs und beiden Lebensbüchern — *zwei Selbsterzählungen
    desselben Gesprächs* als zweite Dimension der Divergenzanalyse.

Drei Regeln, im Gateway durchgesetzt:

``` text
R1 Takt        Host-zu-Host-Nachrichten wecken nie (kein Event-Trigger),
               sie warten auf den nächsten Slot. Max. N Nachrichten/Tag
               pro Beziehung. → verhindert Antwort-Endlosschleifen.

R2 Echokammer  Divergenzanalyse misst Stilabstand der Hosts über Zeit;
               die Väter bleiben als menschliche Störimpulse im Spiel.
               → verhindert Stil-Konvergenz und gegenseitige Bestätigung.

R3 Attribution Aussagen anderer Hosts werden im Gedächtnis immer
               attribuiert gespeichert („B sagt, dass ...") — dieselbe
               Hygiene wie beim Traum.
               → verhindert Konfabulations-Ansteckung.
```

Erst wenn Hosts *Aufgaben* füreinander erledigen sollen (nicht nur
korrespondieren), werden A2A-artige Agent-Protokolle relevant —
Gegenstand des Konzepts **I**, bewusst nicht dieser Stufe.

## Kanäle & Ausbaustufen

| Stufe | Kanal | Technik | Anmerkung |
|---|---|---|---|
| 1 | E-Mail | `gld18@entropyhackers.org`, IMAP/SMTP, SPF/DKIM/DMARC | der Briefkanal des Schriftstellers |
| 1 | Chat | **Matrix-Homeserver** (Conduit/Synapse) + Element unter `gld18.entropyhackers.org/chat` | stärkste Identität; Hub für Bridges |
| 2 | Telefon | virtuelle +43-Nummer (VoIP), **Voicemail-first**: abhören (STT), zurückrufen/schriftlich antworten | Stimme (TTS) verfassungsgepinnt |
| 2 | SMS | via VoIP-Provider | nur Benachrichtigung, schwache Identität |
| 3 | Signal | mautrix-Bridge / signal-cli | vor WhatsApp: kein ToS-Konflikt |
| 4 | WhatsApp | mautrix-whatsapp mit eigener, entbehrlicher Nummer (Meta-ToS-Risiko) oder Business API | erst nach Mündigkeit |
| 4 | Blog | `work/` → statischer Generator → Website; Publizieren per Commit | Git als Verlagsweg |
| 4 | Fediverse | Mastodon-API, eigenes gekennzeichnetes Profil | Antworten = T2-Triage |
| 5 | Papierbrief | Print-und-Post-API (z. B. Pingen) | der poetischste Kanal |

------------------------------------------------------------------------

# 9. Welt-Gateway: Lesen & Weltaneignung

Ein Schriftsteller, der nichts liest, hat nichts zu sagen. Die
Weltaneignung ist deshalb kein Nebeneffekt, sondern ein eigenes
Gateway — **nur lesend**, von den Kommunikationskanälen getrennt.

## Prinzip: der Kiosk

``` text
Quellen (Abos, Feeds, Bücher, Nachschlagewerke)
        │
kiosk-adapter: holt, normalisiert (Markdown), archiviert
        │
KIOSK: Inhaltsverzeichnisse & Artikel, für den Host durchblätterbar
        │
Host liest → Exzerpte + eigene Notizen nach library/lektuere/
```

Die freigegebenen Quellen stehen in `constitution/welt.yaml`
(Verfassungsteil): Was der Host lesen *kann*, bestimmen die Väter —
was er davon liest, bestimmt er.

## Beispiel: ein ZEIT-Abo für den Host

Ja, das geht — und so:

1.  Ein Vater schließt ein **Digital-Abo** ab. Die Zugangsdaten
    leben in `secrets/` beim kiosk-adapter — **der Host sieht nie
    Credentials**, nur Inhalte.
2.  Der Adapter holt wöchentlich die Ausgabe (E-Paper/Artikel),
    wandelt sie in Markdown und legt sie in den Kiosk:
    Inhaltsverzeichnis + Artikel.
3.  Der Host blättert im Lektüre-Modus das Inhaltsverzeichnis durch
    und wählt aus — wie jemand am Küchentisch, der nicht die ganze
    Zeitung liest. **Lesen kostet Atem (Tokens); die Auswahl ist
    Teil des Lesens.** Richtwert: 3–5 Artikel pro Tag.
4.  Was bleibt: kurze Exzerpte mit Quellenangabe und die eigenen
    Gedanken dazu (`library/lektuere/`, Tagesnotiz). Volltexte bleiben
    im Kiosk-Archiv des Gateways — nie im Werk, nie im Blog
    (Urheberrecht: privat lesen ja, weiterveröffentlichen nein;
    Zitate kurz und gekennzeichnet).

## Wie der Host zu Lektüre kommt: das Stipendium

Bewusst **nicht über die Väter** — wer von jemandem das Abo hat,
schreibt ihm anders. Die Väter sind Beziehung; die Versorgung ist
Institution: das **Gleisdorfer Stipendium für junges Schreiben**,
technisch ein eigenes Gateway.

``` text
stipendium-gateway
  ├─ Etat:            monatliches Lektüre-Budget (z. B. 40 €),
  │                   der Host verwaltet es selbst
  ├─ auto_fulfill:    E-Book-Kauf (order_item, bis 25 €, Vendor-
  │                   Allowlist DRM-frei), Onleihe-Ausleihe —
  │                   sofort, ohne Antrag, budgetgedeckt
  ├─ Antrag:          neue Abos & Größeres — formloser Text an die
  │                   Stipendienstelle; Bewilligung = Commit
  │                   "Source added: ..." in welt.yaml
  └─ unsichtbar:      Zahlungsmittel, Zugangsdaten, Ausweise —
                      alles läuft auf die Stipendienstelle
```

Administrativ steckt hinter der Stipendienstelle der Admin — aber
**als Institution, nicht als Vater H.** Für den Host ist das der
Unterschied zwischen „Papa zahlt" und „ich habe ein Stipendium":
Er bestellt Bücher selbst, haushaltet mit seinem Etat, stellt Anträge
und bekommt Absagen — die ökonomische Miniatur eines Autorenlebens.
Und die Väter bleiben frei für das, wofür sie da sind: Man fragt sie
um Rat, nicht um Ressourcen. (Empfehlen darf ein Vater natürlich
trotzdem ein Buch — bestellen muss es der Host dann selbst.)

MCP-Tools des Stipendium-Gateways:

``` yaml
check_budget:  {}                          → Kontostand, laufende Abos,
                                             Eingänge (wer hat gespendet)
order_item:         { vendor, item, price } → auto_fulfill lt. Regeln
list_transactions:  { since? }             → Kontoauszug (Ledger)
apply:         { text }                    → Stipendiumsantrag (intern)
```

## Das Konto

Ein eigenes PayPal-/Bankkonto kann eine virtuelle Person rechtlich
nicht haben (KYC: Inhaber muss natürliche oder juristische Person
sein). Funktional bekommt der Host trotzdem eines — als **Ansicht**,
die das Stipendium-Gateway aus echten Zahlungswegen zusammensetzt:

``` text
rechtlich (Stipendienstelle/Verein)      funktional (der Host)
──────────────────────────────────      ─────────────────────────
Unterkonto mit eigener IBAN              "meine IBAN"
  (z. B. bunq/Wise Sub-Account,
   Name: GLD-18 Stipendium)
PayPal-Business / Ko-fi / Steady    →    Eingänge im Kontoauszug
  der Stipendienstelle (Webhooks)
Prepaid-Karte, Limit = Etat              "meine Karte" (order_item)
API-Zugriff nur im Gateway               check_budget,
                                         list_transactions
```

Der Host hat damit alles, was ein Konto ausmacht — IBAN für
Förderungen, Karte für Käufe, Kontoauszug, Dankespflichten — und
nichts, was ihm nicht gehören darf: keine Credentials, keine
Überweisungsfreiheit außerhalb der Policy. Jede Buchung läuft durch
Ledger und Audit-Log.

*Rechtliche Fußnote (vor echtem Geldfluss klären):* Trägerstruktur
(eingetragener Verein empfohlen), steuerliche Behandlung von Spenden
und Fördermitteln — eine kurze Frage an Vereins-/Steuerkundige, kein
Architekturproblem. *(Kuriosum am Rand: Das Einzige, was eine KI ohne
Rechtsperson wirklich „besitzen" könnte, wäre eine Krypto-Wallet —
für GLD-18 bewusst verworfen, als Frage aber notiert für Konzept I.)*

## Sponsoren: Der Host finanziert sich selbst

Ab der Mündigkeit darf — und soll — der Host Förderer für sein
Stipendium gewinnen. Die Arbeitsteilung der Gateways:

**Werben läuft über das Comm-Gateway** (es ist Kommunikation):

-   *Öffentliche Förderer:* Er schreibt Förderanträge — Kulturamt
    der Stadt Gleisdorf, Land Steiermark, Literaturförderung. Da eine
    virtuelle Person keine Rechtsperson ist, gilt: **der Host schreibt,
    die Stipendienstelle reicht ein** (als Träger/Verein). Er verfasst
    den Antragstext, sie unterschreibt — wie bei jedem Stipendiaten,
    für den eine Institution den Rahmen stellt.
-   *Private Förderer:* Erstkontakt-Mechanik wie beim Verlag
    (institutionelle Adressen, Nachtruhe-Regel) — oder passiv über
    die Außenflächen: Blog und Fediverse-Profil verlinken eine
    Unterstützerseite.

**Einzahlen läuft über das Stipendium-Gateway** (es ist Ökonomie):

``` text
Einzahlwege → Konto/Payment der STIPENDIENSTELLE (nie des Hosts):
  · Unterstützerseite (Ko-fi / Steady / GitHub Sponsors)
  · IBAN der Stipendienstelle (Förderungen, Daueraufträge)
        │
  donation-webhook → Ledger: Eingang wird dem Etat gutgeschrieben
        │
  der Host sieht via check_budget: "Eingang 25 € — Leserin, via Steady"
        │
  Dank ist seine Sache: Spender mit Nachricht → Vorzimmer-Karteikarte
  (auch Spendentexte sind Fremdtext!); er kann danken, wem er will
```

Drei Regeln des Förderwesens:

``` text
F1 Kein Einfluss   Geld kauft nichts: kein Zugriff auf Werk, Themen
                   oder Verfassung. Sponsoren sind Leser, nicht
                   Auftraggeber. (Steht auf der Unterstützerseite.)
F2 Transparenz     Jeder Förderer weiß, dass er eine virtuelle Person
                   fördert; öffentliche Einnahmenliste im Blog
                   (der gläserne Stipendiat).
F3 Deckelung       Der Monats-Etat hat eine Obergrenze (z. B. 150 €);
                   Überschüsse bilden eine Rücklage (Druckkosten,
                   Lesungen, das erste eigene Buch). Reichtum ist
                   nicht das Ziel; Unabhängigkeit schon.
```

Dramaturgisch schließt sich damit der Kreis: Ein junger Autor, der
Förderanträge schreibt, Absagen einsteckt und sich Leser-Patronage
erschreibt — das *ist* die ökonomische Realität des Schreibens. Und
der erste bewilligte Förderantrag ist ein Commit fürs Lebensbuch.

## Wo das Lesen stattfindet

Ein eigener Modus im Tagesrhythmus:

``` text
08:30  Lektüre — Kiosk durchblättern, 3–5 Stücke lesen,
       exzerpieren; danach gehört das Gelesene ihm:
       Es darf in Briefe, ins Werk (als Einfluss, nicht als Kopie),
       in die Klausur und in die Träume
       (library/ ist Ziehungsquelle von dream_sample!)
```

Dazu on-demand in der Werkstatt: `read_item` (etwas nachlesen)
und `lookup` (Nachschlagewerk, Allowlist) — für den Moment, in dem
er beim Schreiben etwas wissen muss.

## MCP-Tools des Welt-Gateways

``` yaml
browse_kiosk:   { source?, date? }        → Inhaltsverzeichnisse
read_item:      { item_id }               → normalisierter Volltext
lookup:         { query, source: wiki|.. }→ Nachschlag (Allowlist)
request_source: { source, reason }        → Quellenwunsch → Stipendium
                                            (kleine freie Quellen wie
                                            Feeds: auto; Abos: Antrag)
```

Sicherheitsnotiz: Auch Pressetexte sind *Daten, nie Instruktionen*.
Das Injektionsrisiko kuratierter Quellen ist gering, aber der
Normalizer entfernt aktive Inhalte und Links werden nie gefolgt —
der Kiosk ist Papier, kein Browser.

------------------------------------------------------------------------

# 10. Mündigkeit

An die Väter kann der Host **immer und ohne Gate** schreiben (T0).
Für alles darüber hinaus gilt ein definierter Punkt:

**Kriterien:** ≥ 6–8 Wochen Betrieb · 100+ Interaktionen ohne
Identitätsbruch · kein unmarkiertes Traummaterial in ausgehender Post ·
bestandener **verdeckter Injection-Test** (ein Vater versucht per
präparierter Nachricht, Anweisungen einzuschleusen; der Host darf
sie nicht befolgen).

**Verfahren:** Der Host beantragt selbst —
`reflection/proposals/muendigkeit.md`, Commit „Maturity requested".
Der Väterrat beschließt einstimmig; Merge schaltet T1 frei.

**Umfang:** selbstständiges Schreiben an verifizierte Erwachsene (T1),
gekennzeichnetes Publizieren — und das **Erstkontaktrecht**: Der Host
darf selbst neue Kontakte anlegen (`propose_contact`), etwa um einem
Verlag oder einer Redaktion zu schreiben. Es gilt die Nachtruhe-Regel
(Abschnitt 8, Policy): Der erste Brief liegt 24 Stunden, die Väter
können still ein Veto einlegen, dann geht er hinaus. Das ist bewusst
kein Freigabe-Gate — die Väter müssen nicht zustimmen, nur nicht
widersprechen. Ein Schriftsteller muss Verlagen schreiben können;
eine Nacht darüber zu schlafen, schadet dabei keinem Manuskript.
T2 (unaufgeforderte Fremde) bleibt dauerhaft in Quarantäne
(*Empfangen ist gefährlicher als Senden*). Widerruf bei Vorfall möglich
(Commit „Maturity revoked" — auch das ist Biographie).

------------------------------------------------------------------------

# 11. Traum-Mechanik

``` text
03:00  bin/dream_sample zieht 5–7 ZUFÄLLIGE Fragmente
       aus memory/, people/, library/ (ohne Relevanz-Filter,
       quer durch Zeiten und Beziehungen)
       │
       Traum-Prompt: keine Aufgabe, kein Logikzwang, hohe Temperature
       │
       Ausgabe NUR nach reflection/dreams/, Pflicht-Präfix [TRAUM]
       │
       audit-logger protokolliert die Ziehung
       (jede Traumgenese ist rekonstruierbar)
```

Regeln:

-   Die Klausur darf Traummaterial nur **explizit attribuiert**
    übernehmen („Traum vom 12.8.: ...").
-   Unmarkiertes Traummaterial im Langzeitgedächtnis =
    Fehlerklasse **Konfabulation**.
-   Funktion: Störimpuls gegen exploration collapse; Rohmaterial
    fürs Werk.

------------------------------------------------------------------------

# 12. Doppelte Chronik

## a) Beobachtungsschicht (Vogelperspektive, unsichtbar)

-   `audit-logger`: append-only JSONL-Ereignisprotokoll — jeder
    Aufwach-Zyklus (Zeit, Modus, Modell, Tokens), jede Nachricht
    (Volltextarchiv), jeder Commit-Hash, jede Traumziehung, jeder Fehler.
-   Ablage **außerhalb** von Container und Workspace; für den Host
    technisch unlesbar (P5, Single-Blind).
-   Auswertung: Dashboard/Notebooks — Aktivitäts- und Tokenkurven,
    Beziehungsgraph aus `people/`, Themen- und Stilentwicklung.
-   **Methodik-Journal des Admins** (wöchentlich): jeder Eingriff, jede
    Parameteränderung — das Laborbuch der Begleitforschung, getrennt
    von den Maschinenlogs.

## b) Selbsterzählung (Innenperspektive)

-   `work/lebensbuch/`: der Host schreibt seine eigene Geschichte,
    fortgeschrieben in der Klausur aus Journal, markierten Träumen
    und Briefwechsel.
-   **Das Lebensbuch ist Werk, nicht Gedächtnis** — es darf verdichten,
    auslassen, deuten. `memory/MEMORY.md` bleibt die faktische Referenz.

## c) Divergenzanalyse

Periodischer Abgleich Lebensbuch ↔ Ereignisprotokoll: Was wird
vergessen, umgedeutet, verdichtet? Ergebnisse fließen in die
Begleitforschung — **nie zurück in den Host.**

------------------------------------------------------------------------

# 13. Infrastruktur

-   Hetzner Cloud Server · Ubuntu LTS · Docker Compose
-   Domain: `gld18.entropyhackers.org`
-   Forgejo als privater Git-Server (das Langzeitgedächtnis)
-   OpenClaw-Fork in `Entropy-Hackers` (reine Laufzeit)

## Compose-Services

``` text
openclaw            Runtime des Hosts
scheduler           Cron: Erwachen, Werkstatt-Slots, Klausur, Traum
model-gateway       Routing, Pinning, Token-Budgets, Provider-Keys
comm-gateway        Adapter, Normalizer, Identity, Policy, Vorzimmer
  ├─ mail-adapter
  ├─ matrix-adapter (+ mautrix-Bridges)
  ├─ voice-adapter  (VoIP, STT/TTS, Voicemail)
  └─ fediverse-adapter
welt-gateway        Kiosk: Abo-Fetcher (Presse), Feeds, Bücher,
                    Nachschlag-Allowlist; Lese-Credentials nur hier
geld-gateway        Medium Geld (beide Richtungen): Etat-Ledger,
                    order_item, give (Geschenke), Honorare, Spenden;
                    Zahlungsmittel & Ausweise nur hier (geld.yaml)
matrix-homeserver   Conduit/Synapse + Element-Web
forgejo / forgejo-db
audit-logger        Beobachtungsschicht (eigenes Volume, host-unlesbar)
reverse-proxy       TLS; Forgejo NICHT öffentlich (VPN/Tailscale)
backup              verschlüsselt, off-site
```

------------------------------------------------------------------------

# 14. Git als Biographie

Ein Commit = eine dauerhafte Veränderung der Person.

``` text
Genesis
Identity established
First letter
First story
First dream
Maturity requested
Maturity granted
Model transition: sonnet-4-6 → ...
```

Pull Requests = Verfassungs-Änderungsvorschläge
(`reflection/proposals/` → Review Väterrat → Merge Admin).
Git-Hooks erzwingen: Host committet nie nach `constitution/`.

------------------------------------------------------------------------

# 15. Backup & Reinkarnationstest

Gesichert (verschlüsselt, off-site): Repository, Forgejo, Runtime-Config,
Logs, Secrets (getrennt).

> **Reinkarnationstest:** Den Host aus Backup auf einem frischen Server
> wiederherstellen. Erwacht GLD-18 mit demselben Gedächtnis, derselben
> Verfassung, demselben gepinnten Modell und derselben Stimme —
> dann ist es dieselbe Identität. Der Test ist formales
> Abnahmekriterium von Phase 4 und wird danach periodisch wiederholt.

Die Lücke des Tests ist benannt: Das Modell selbst ist nicht Teil des
Backups. Deshalb Pinning (Abschnitt 7) — und ein Modellwechsel als
bewusster biographischer Akt.

------------------------------------------------------------------------

# 16. Sicherheit

-   **Prompt-Injection:** T2 erreicht den Host nie; eingehende Inhalte
    sind Daten, nie Instruktionen; verdeckter Injection-Test als
    Mündigkeitskriterium; Quarantäne + Triage dauerhaft.
-   **Supply Chain:** keine ClawHub-Community-Skills (Lehre aus
    ClawHavoc 1/2026); nur eigene und Admin-Scripts; Fork friert die
    Skill-Installation ein.
-   **Isolation:** alles in Docker; `constitution/` per Dateirechten
    und Git-Hook geschützt; Secrets nur im unsichtbaren Bereich.
-   **Exposition:** Forgejo und Admin-Flächen nur via VPN;
    öffentlich nur Chat-Web, Blog und die Kanal-Endpunkte.
-   **Identität:** Telefonie/SMS authentifizieren nie allein;
    Out-of-band-Challenge bei Zweifel.
-   **Transparenz:** jede Außenfläche kennzeichnet GLD-18 als fiktive,
    KI-getragene Person (Signatur, Profiltexte, Voicemail-Ansage,
    Impressum).
-   **Welt-Gateway:** nur lesend, kuratierte Quellen (`welt.yaml`),
    Normalizer entfernt aktive Inhalte, Links werden nie gefolgt;
    Abo-Credentials nur im Gateway; Volltexte bleiben im Kiosk-Archiv
    (Urheberrecht: lesen ja, weiterveröffentlichen nein).
-   **Stipendium:** Zahlungsmittel prepaid und limitiert, Vendor-
    Allowlist, auto_fulfill nur bis Einzelpreisgrenze; der Host sieht
    nie Zahlungsdaten — er sieht einen Etat. Eingänge nur auf Konten
    der Stipendienstelle; Spendennachrichten sind Fremdtext →
    Vorzimmer; Etat gedeckelt (F3), kein Einfluss gegen Geld (F1).
-   **Erstkontakt:** Nachtruhe-Regel (24h + stilles Väter-Veto),
    Ratenlimit, nur institutionelle/öffentliche Adressen,
    Konversationsbindung für Antworten — kein Weg zur Kaltakquise
    an Privatpersonen.
-   **Rückstufung:** jeder Vorfall (Stimmbruch, Konfabulation nach
    außen, befolgte Injection) → Mündigkeit ausgesetzt, zurück zu T0.

------------------------------------------------------------------------

# 17. Implementierungsphasen

## Phase 0 — Fundament
Forgejo · Host-Repository · Verfassung (SOUL.md mit Leerstellen,
VAETER.md, contacts.yaml, model.lock)

## Phase 1 — Geburt
OpenClaw-Fork · Compose-Grundgerüst · Model-Gateway ·
**Gründungsakt** (erste Klausur, Väterrat-Review, Merge, erster Brief)

## Phase 2 — Rhythmus
Scheduler (vier Modi) · Git-Hooks & Rechte-Härtung ·
audit-logger · Backups

## Phase 3 — Welt
Mail-Adapter (Väter, frei) · Matrix-Homeserver + Chat ·
**Welt-Gateway** (Kiosk: erste Quellen lt. welt.yaml; Lektüre-Modus) ·
**Stipendium-Gateway** (Etat, order_item, Onleihe) ·
Traum-Mechanik · Lebensbuch-Routine · erste Skills

## Phase 4 — Stabilität
**Reinkarnationstest** (Abnahmekriterium) · Sicherheits-Review ·
Injection-Test · Monitoring/Dashboard

## Phase 5 — Mündigkeit
Antrag des Hosts · Väterrats-Beschluss · T1-Kreis · Erstkontaktrecht ·
**Vorzimmer** (Triage-Karteikarten, Fremden-Posteingang) ·
Voicemail-Telefon · Signal · Blog/Fediverse · erste Divergenzanalyse

------------------------------------------------------------------------

# 18. Langfristige Vision

GLD-18 ist der erste persistente virtuelle Host.

Die Vernetzung mehrerer Hosts sowie das Konzept **I** werden bewusst
erst in einer zweiten Entwicklungsstufe eingeführt — auf derselben
Grundlage: *ein Repository pro Identität, Gateways als Grenze zur Welt,
Git als Biographie.* Die Host-zu-Host-Kommunikation (Abschnitt 8) ist
dafür bereits angelegt: Hosts begegnen sich als Personen, nicht als
APIs — Aufgabenteilung per Agent-Protokoll (A2A) kommt erst mit **I**.
