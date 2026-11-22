<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/dark_logo.png">
    <img src="docs/logo.png" alt="State Announce" height="96">
  </picture>
</p>

# Zustandsansage (State Announce)

**Deutsch** | [English](README.md)

Eigene Home Assistant Integration, die ansagt, welche Entitäten einen bestimmten Zustand haben. Zum Beispiel:

> „Die Fenster Eltern rechts und Gäste WC sind offen.“

Alles läuft über eine normale Aktion im UI Editor. **Kein Template nötig.**

## Funktionen

- Aktion **„Zustand ansagen“** (`state_announce.announce`) für Automationen und Skripte
- Eigener Satz für **einen**, **mehrere** und **keinen** Treffer (Einzahl und Mehrzahl stimmen immer)
- Namen als lesbare Liste: „A“, „A und B“, „A, B und C“ (Deutsch „und“, Englisch „and“)
- **Namensquelle** wählbar: Alias, Name oder Name ohne Bereich
- **Ziele** per Auswahlliste: Alexa (Alexa Media Player), Handy, Fernseher, Wanddisplay und alle anderen Benachrichtigungen; mehrere gleichzeitig
- Alexa: normale Sprachausgabe oder Ansage mit Gong
- Nicht erreichbare Geräte optional mitmelden
- Rückgabewert (Namen, Anzahl, Satz) für eigene Weiterverarbeitung
- Deutsch und Englisch (folgt der Sprache von Home Assistant), eigenes Icon und Logo

## Voraussetzungen

- Home Assistant **2026.3** oder neuer
- Für Alexa: die Integration [Alexa Media Player](https://github.com/alandtse/alexa_media_player)

## Installation

1. **Einstellungen**, **Marketplace**
2. Oben rechts **Aus Link hinzufügen** (englisch „Add from link“)
3. `tobi136B/ha_state_announce` eingeben und **Hinzufügen** (falls gefragt, Typ **Integration**)
4. **State Announce** installieren (falls verlangt, Home Assistant neu starten)
5. **Einstellungen**, **Geräte & Dienste**, **Integration hinzufügen**, **State Announce** auswählen und bestätigen

Vor Home Assistant 2026.11 über HACS: Menü (drei Punkte), **Benutzerdefinierte Repositories**, Link mit Typ **Integration** hinzufügen.

## Benutzung

In einer Automation **Aktion hinzufügen** und **Zustand ansagen** auswählen.

| Feld | Bedeutung |
|---|---|
| Entitäten | Was geprüft wird. Die Reihenfolge ist auch die Reihenfolge in der Ansage. |
| Zustand | Welcher Zustand zählt. Fenster und Türen sind bei „Ein“ offen. Eigene Werte (z. B. `open`, `home`) lassen sich eintippen. |
| Satz bei einem | Satz, wenn genau einer zutrifft. Leer = Satz bei mehreren. |
| Satz bei mehreren | Satz, wenn mehrere zutreffen. Pflichtfeld. |
| Satz bei keinem | Satz, wenn keiner zutrifft. Leer = es wird nichts gesendet. |
| Ziele | Wohin die Nachricht geht. Mehrere möglich. |
| **Erweitert** | |
| Namensquelle | Alias (sonst Name), Name oder Name ohne Bereich |
| Titel | Überschrift für Handy Benachrichtigungen |
| Alexa Art | Sprachausgabe oder Ansage mit Gong |
| Nicht erreichbare melden | Sagt zusätzlich, welche Geräte nicht erreichbar sind |
| Satz bei nicht erreichbar | Eigener Satz dafür, Standard: „Nicht erreichbar: …“ |

### Platzhalter

| Platzhalter | Wird ersetzt durch |
|---|---|
| `{namen}` oder `{names}` | die Namen, z. B. „Eltern rechts, Gäste WC und Tobi“ |
| `{anzahl}` oder `{count}` | die Anzahl, z. B. „3“ |

Das ist ein einfaches Ersetzen, kein Template.

### Eigene Namen vergeben

Mit der Namensquelle **Alias, sonst Name** sagt die Ansage den Alias der Entität. So vergibst du ihn:

**Einstellungen**, **Geräte & Dienste**, **Entitäten**, Entität öffnen, Zahnrad, **Sprachassistenten**, **Aliase**, Alias eintragen (z. B. „Eltern rechts“).

Ist kein Alias gesetzt, wird der normale Name gesagt.

### Beispiel (YAML Ansicht)

```yaml
action: state_announce.announce
data:
  entities:
    - binary_sensor.fensterkontakt_links_schlafzimmer_eltern_contact
    - binary_sensor.fensterkontakt_rechts_schlafzimmer_eltern_contact
    - binary_sensor.gaste_wc_fensterkontakt_gaste_wc
    - binary_sensor.schlafzimmer_tobi_fensterkontakt_schlafzimmer_tobi
  state: "on"
  message_one: "Das Fenster {namen} ist offen."
  message_many: "Die Fenster {namen} sind offen."
  targets:
    - notify.alexa_media_alexa_kuche
  alexa_type: tts
```

### Rückgabewert

Mit **Antwortvariable** in der Aktion bekommst du:

```yaml
names: ["Eltern rechts", "Gäste WC"]
count: 2
unavailable: []
message: "Die Fenster Eltern rechts und Gäste WC sind offen."
sent: true
```

## Hinweise

- Die Ziel Liste füllt sich automatisch mit allen Benachrichtigungen und aktualisiert sich, wenn neue dazukommen. Nach dem Hinzufügen eines Geräts einmal die Seite neu laden.
- Fällt ein Ziel aus, bekommen die anderen ihre Nachricht trotzdem. Die Automation meldet danach einen Fehler mit dem betroffenen Ziel.
- Haben eine Entität und ein Dienst denselben Namen, wird die Entität genommen.

## Entwicklung

```bash
pip install -r requirements_test.txt
pytest
ruff check custom_components tests
```

## Lizenz

MIT
