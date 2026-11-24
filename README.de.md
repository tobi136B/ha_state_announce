<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/dark_logo.png">
    <img src="docs/logo.png" alt="State Announce" height="96">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/tobi136B/ha_state_announce/actions/workflows/validate.yml"><img src="https://github.com/tobi136B/ha_state_announce/actions/workflows/validate.yml/badge.svg" alt="Prüfung"></a>
  <a href="https://github.com/tobi136B/ha_state_announce/releases"><img src="https://img.shields.io/github/v/release/tobi136B/ha_state_announce" alt="Release"></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2026.3%2B-41BDF5" alt="Home Assistant 2026.3+">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/tobi136B/ha_state_announce" alt="Lizenz"></a>
</p>

# State Announce

Deutsch | [English](README.md)

Manchmal reicht es nicht zu wissen, *ob* etwas an, offen oder erkannt ist. Man will wissen, *was*. State Announce nimmt eine Gruppe von Entitäten, sucht die heraus, die gerade den gewünschten Zustand haben, und macht daraus einen ganz normalen Satz:

> „2 Lichter sind noch an: Flur und Garage.“
> „Person und Tier erkannt.“
> „Batterie schwach: Haustür und Badsensor.“

Der Satz geht dorthin, wo du ihn haben willst: als Benachrichtigung aufs Handy oder den Fernseher, als Sprache auf einen smarten Lautsprecher, auf Alexa oder jeden anderen Lautsprecher, über den Home Assistant sprechen kann. Ganz ohne Templates.

## Was geprüft werden kann

Alles, was einen Zustand hat. Ein paar Ideen:

- Lichter oder Schalter, die noch an sind
- offene Fenster, Türen oder Rollläden
- Personen, Fahrzeuge oder Tiere, die eine Kamera erkannt hat
- wer zu Hause ist
- Batterien unter einem bestimmten Stand
- Geräte, die laufen oder ein Problem melden

Die Entitäten wählst du einzeln aus oder lässt sie über Etage, Bereich, Gerät oder Label finden. Eine Auswahl wird bei jedem Ausführen neu ermittelt, später hinzugefügte Geräte sind also automatisch dabei.

## Wohin gesendet werden kann

| Ziel | So kommt die Nachricht an |
|---|---|
| Benachrichtigungs Entitäten (Handy App, Fernseher, Wanddisplay, …) | als Benachrichtigung |
| Benachrichtigungsdienste (ältere Integrationen) | als Benachrichtigung |
| Media Player (Google, Sonos, HA Voice, …) | gesprochen über eine Sprachausgabe Engine |
| Alexa über [Alexa Media Player](https://github.com/alandtse/alexa_media_player) | gesprochen, normal oder als Ansage mit Gong |

Alle verfügbaren Ziele stehen in einer Auswahlliste. Mehrere gleichzeitig sind möglich.

## Installation

Ab Home Assistant 2026.11:

1. **Einstellungen > Marketplace** öffnen und **Aus Link hinzufügen** wählen.
2. `tobi136B/ha_state_announce` eingeben und den Typ **Integration** wählen.
3. **State Announce** installieren.
4. Unter **Einstellungen > Geräte & Dienste > Integration hinzufügen** die Integration **State Announce** hinzufügen.

Bei älteren Versionen das Repository in HACS als benutzerdefiniertes Repository vom Typ **Integration** hinzufügen.

## Benutzung

Die Aktion **Zustand ansagen** in eine Automation oder ein Skript einfügen.

### Was geprüft wird

| Feld | Beschreibung |
|---|---|
| Entitäten | Einzelne Entitäten, werden in dieser Reihenfolge geprüft. |
| Auswahl | Etagen, Bereiche, Geräte oder Labels, optional mit Ausnahmen. |
| Geräteklasse | Filter für die Auswahl, z. B. Fenster, Bewegung oder Batterie. |
| Entitätstyp | Filter für die Auswahl, z. B. Licht oder Schalter. |
| Zustand | Gesuchter Zustand oder Zahlenwert. Standard `on`. |
| Vergleich | ist gleich, ist nicht gleich, größer als, kleiner als. |

Die Anzahl unter Auswahl ist die Gesamtzahl der Etage oder des Bereichs. Die Filter greifen erst beim Ausführen. Deaktivierte, ausgeblendete, Diagnose und Konfigurations Entitäten werden immer übersprungen.

### Was gesagt wird

| Feld | Wird gesendet, wenn |
|---|---|
| Nachricht bei einem Treffer | genau eine Entität zutrifft (leer: das nächste Feld gilt) |
| Nachricht bei mehreren Treffern | zwei oder mehr zutreffen |
| Nachricht ohne Treffer | keine zutrifft (leer: es wird nichts gesendet) |

In jeder Nachricht gibt es diese Platzhalter:

| Platzhalter | Wird ersetzt durch |
|---|---|
| `{namen}` | die Namen, verbunden als `A`, `A und B` oder `A, B und C` |
| `{anzahl}` | wie viele zutreffen |

`{names}` und `{count}` gehen genauso. Das Verbindungswort richtet sich nach der Sprache von Home Assistant.

Weil es eigene Nachrichten für einen und für mehrere Treffer gibt, stimmt die Grammatik immer, und du entscheidest selbst, ob die Anzahl mitgesagt wird:

| Nachricht | Ergebnis bei 2 Treffern |
|---|---|
| `{anzahl} Lichter sind noch an: {namen}.` | 2 Lichter sind noch an: Flur und Garage. |
| `Noch an: {namen}.` | Noch an: Flur und Garage. |
| `{namen} erkannt.` | Person und Tier erkannt. |

Bei Sprachausgabe wird die Zahl als Wort gesprochen.

### Namen

Die Option **Namensquelle** legt fest, was für jede Entität gesagt wird: ihr Alias, ihr Name oder ihr Name ohne Bereich. Mit Aliasen bekommst du am einfachsten kurze, natürliche Namen wie „Flur“ oder „Tier“. Du stellst sie pro Entität ein unter **Einstellungen > Geräte & Dienste > Entitäten > (Entität) > Einstellungen > Sprachassistenten > Aliase**.

### Erweiterte Optionen

| Option | Beschreibung |
|---|---|
| Namensquelle | Alias (sonst Name), Name oder Name ohne Bereich |
| Sprachausgabe Engine | Für Media Player Ziele. Leer: die erste vorhandene Engine |
| Titel | Titel der Benachrichtigung, wenn das Ziel einen unterstützt |
| Alexa Ausgabe | Normale Sprache oder Ansage mit Gong, nur Alexa Media Player |
| Nicht erreichbare melden | Nicht erreichbare Entitäten zusätzlich nennen |
| Nachricht bei nicht erreichbar | Standard `Nicht erreichbar: {namen}.` |

Fällt ein Ziel aus, bekommen die anderen die Nachricht trotzdem. Die Aktion meldet danach das fehlerhafte Ziel.

## Beispiele

### Kamera Erkennung

```yaml
action: state_announce.announce
data:
  entities:
    - binary_sensor.haustuer_person
    - binary_sensor.haustuer_fahrzeug
    - binary_sensor.haustuer_tier
  message_one: "{namen} erkannt."
  message_many: "{namen} erkannt."
  targets:
    - media_player.wohnzimmer_lautsprecher
```

Mit den Aliasen „Person“, „Fahrzeug“ und „Tier“ wird eine gleichzeitige Erkennung als „Person und Tier erkannt.“ angesagt.

### Vergessene Lichter

```yaml
action: state_announce.announce
data:
  selection:
    floor_id: erdgeschoss
  domains:
    - light
  message_one: "{namen} ist noch an."
  message_many: "{anzahl} Lichter sind noch an: {namen}."
  targets:
    - notify.mobile_app_telefon
  title: Licht
```

### Schwache Batterien

```yaml
action: state_announce.announce
data:
  selection:
    label_id: batteriebetrieben
  device_classes:
    - battery
  domains:
    - sensor
  state: "20"
  comparison: below
  message_one: "Batterie schwach: {namen}."
  message_many: "{anzahl} Batterien sind schwach: {namen}."
  targets:
    - notify.mobile_app_telefon
```

### Offene Fenster einer Etage

```yaml
action: state_announce.announce
data:
  selection:
    floor_id: obergeschoss
  device_classes:
    - window
  message_one: "{namen} ist offen."
  message_many: "{anzahl} Fenster sind offen: {namen}."
  message_none: "Alle Fenster sind zu."
  targets:
    - notify.alexa_media_kueche
```

### Wer ist zu Hause

```yaml
action: state_announce.announce
data:
  entities:
    - person.anna
    - person.ben
  state: home
  message_one: "{namen} ist zu Hause."
  message_many: "{namen} sind zu Hause."
  message_none: "Niemand ist zu Hause."
  targets:
    - notify.mobile_app_telefon
```

## Rückgabe

Die Aktion kann ihr Ergebnis in eine Antwortvariable schreiben, etwa um den Satz woanders weiterzuverwenden:

```yaml
names: ["Flur", "Garage"]
count: 2
unavailable: []
message: "2 Lichter sind noch an: Flur und Garage."
sent: true
```

## Entwicklung

```bash
pip install -r requirements_test.txt
pytest
ruff check custom_components tests
```

## Lizenz

[MIT](LICENSE)
