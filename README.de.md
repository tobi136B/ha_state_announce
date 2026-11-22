<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/dark_logo.png">
    <img src="docs/logo.png" alt="State Announce" height="96">
  </picture>
</p>

# State Announce

Deutsch | [English](README.md)

Eigene Integration für Home Assistant. Stellt die Aktion `state_announce.announce` bereit. Sie prüft eine Liste von Entitäten und sendet eine Nachricht mit allen Entitäten, die einen bestimmten Zustand haben.

## Voraussetzungen

- Home Assistant 2026.3 oder neuer

## Installation

Home Assistant 2026.11 oder neuer:

1. Einstellungen > Marketplace > Aus Link hinzufügen
2. `tobi136B/ha_state_announce` eingeben, Typ Integration
3. State Announce installieren
4. Einstellungen > Geräte & Dienste > Integration hinzufügen > State Announce

Ältere Versionen: Repository in HACS als benutzerdefiniertes Repository hinzufügen (Typ Integration).

## Felder der Aktion

| Feld | Beschreibung |
|---|---|
| `entities` | Zu prüfende Entitäten. Die Reihenfolge bestimmt die Reihenfolge der Namen. |
| `state` | Zustand, der gezählt wird. Standard `on`. |
| `message_one` | Nachricht bei einem Treffer. Optional, sonst gilt `message_many`. |
| `message_many` | Nachricht bei mehreren Treffern. |
| `message_none` | Nachricht ohne Treffer. Optional, leer wird nichts gesendet. |
| `targets` | Benachrichtigungs Entitäten oder Benachrichtigungsdienste. |
| `name_source` | `alias`, `name` oder `name_without_area`. Standard `alias`. |
| `title` | Titel der Benachrichtigung. Optional. |
| `alexa_type` | `tts` oder `announce`. Nur für Ziele von Alexa Media Player. |
| `report_unavailable` | Nicht erreichbare Entitäten anhängen. Standard `false`. |
| `message_unavailable` | Nachricht für nicht erreichbare Entitäten. Optional. |

### Platzhalter

| Platzhalter | Wert |
|---|---|
| `{namen}` / `{names}` | Namen als `A`, `A und B`, `A, B und C` |
| `{anzahl}` / `{count}` | Anzahl der Treffer |

Platzhalter werden als reiner Text ersetzt. Das Verbindungswort richtet sich nach der Sprache von Home Assistant.

### Namensquelle

- `alias`: erster Alias der Entität, sonst ihr Name
- `name`: Name der Entität
- `name_without_area`: Name der Entität ohne den Namen des Bereichs

### Ziele

- Benachrichtigungs Entitäten werden über `notify.send_message` aufgerufen.
- Benachrichtigungsdienste werden direkt aufgerufen.
- Dienste von Alexa Media Player (`notify.alexa_media_*`) bekommen `data.type` aus `alexa_type`. Der Titel wird an sie nicht gesendet.

Schlägt ein Ziel fehl, werden die übrigen trotzdem bedient. Danach meldet die Aktion einen Fehler.

## Beispiel

```yaml
action: state_announce.announce
data:
  entities:
    - binary_sensor.kontakt_1
    - binary_sensor.kontakt_2
    - binary_sensor.kontakt_3
  state: "on"
  message_one: "{namen} ist offen."
  message_many: "{anzahl} sind offen: {namen}."
  targets:
    - notify.mobile_app_telefon
```

Ergebnis bei zwei Treffern: `2 sind offen: Kontakt 1 und Kontakt 3.`

## Rückgabe

```yaml
names: ["Kontakt 1", "Kontakt 3"]
count: 2
unavailable: []
message: "2 sind offen: Kontakt 1 und Kontakt 3."
sent: true
```

## Entwicklung

```bash
pip install -r requirements_test.txt
pytest
ruff check custom_components tests
```

## Lizenz

MIT
