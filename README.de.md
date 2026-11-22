<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/dark_logo.png">
    <img src="docs/logo.png" alt="State Announce" height="96">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/tobi136B/ha_state_announce/actions/workflows/validate.yml"><img src="https://github.com/tobi136B/ha_state_announce/actions/workflows/validate.yml/badge.svg" alt="Prüfung"></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2026.3%2B-41BDF5" alt="Home Assistant 2026.3+">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/tobi136B/ha_state_announce" alt="Lizenz"></a>
</p>

# State Announce

Deutsch | [English](README.md)

State Announce ergänzt Home Assistant um eine Aktion: **Zustand ansagen**. Sie bekommt eine Liste von Entitäten und einen Zustand und schickt eine Nachricht an ein oder mehrere Ziele, in der alle Entitäten genannt werden, die gerade diesen Zustand haben.

Typische Anwendungen:

- Welche Fenster oder Türen offen sind
- Welche Lichter noch an sind
- Wer zu Hause ist
- Welche Geräte laufen
- Welche Batterien schwach sind

Die Nachricht besteht aus normalem Text mit Platzhaltern. Templates sind nicht nötig.

## Installation

Ab Home Assistant 2026.11:

1. **Einstellungen > Marketplace** öffnen und **Aus Link hinzufügen** wählen.
2. `tobi136B/ha_state_announce` eingeben und den Typ **Integration** wählen.
3. **State Announce** installieren.
4. Unter **Einstellungen > Geräte & Dienste > Integration hinzufügen** die Integration **State Announce** hinzufügen.

Bei älteren Versionen das Repository in HACS als benutzerdefiniertes Repository vom Typ **Integration** hinzufügen.

## Benutzung

Die Aktion **Zustand ansagen** in eine Automation oder ein Skript einfügen und ausfüllen:

- **Entitäten**: die zu prüfenden Entitäten
- **Zustand**: der gesuchte Zustand, Standard `on`
- **Nachrichten**: was bei einem, mehreren oder keinem Treffer gesendet wird
- **Ziele**: wohin gesendet wird

### Nachrichten und Platzhalter

Es gibt drei Nachrichtenfelder, damit der Text zur Anzahl der Treffer passt:

| Feld | Wird gesendet, wenn | Pflicht |
|---|---|---|
| Nachricht bei einem Treffer | genau eine Entität zutrifft | nein, sonst gilt das nächste Feld |
| Nachricht bei mehreren Treffern | zwei oder mehr Entitäten zutreffen | ja |
| Nachricht ohne Treffer | keine Entität zutrifft | nein, leer wird nichts gesendet |

In jeder Nachricht gibt es zwei Platzhalter:

| Platzhalter | Wird ersetzt durch |
|---|---|
| `{namen}` | die Namen, verbunden als `A`, `A und B` oder `A, B und C` |
| `{anzahl}` | die Anzahl der Treffer |

Die englischen Platzhalter `{names}` und `{count}` funktionieren ebenfalls. Das Verbindungswort richtet sich nach der Sprache von Home Assistant.

### Anzahl ansagen

Mit `{anzahl}` vor den Namen wird gesagt, wie viele es sind:

| Nachricht | Ergebnis bei 3 Treffern |
|---|---|
| `{anzahl} Fenster sind offen: {namen}.` | 3 Fenster sind offen: Küche, Bad und Büro. |
| `Es sind {anzahl} Lichter an, nämlich {namen}.` | Es sind 3 Lichter an, nämlich Flur, Schreibtisch und Eingang. |
| `{namen} sind offen ({anzahl} insgesamt).` | Küche, Bad und Büro sind offen (3 insgesamt). |

Sprachassistenten wie Alexa sprechen die Zahl als Wort aus.

### Namen

Die Option **Namensquelle** legt fest, welcher Name für jede Entität verwendet wird:

| Option | Verwendeter Name |
|---|---|
| Alias, sonst Name (Standard) | der erste Alias der Entität, ohne Alias ihr Name |
| Name | der Name der Entität |
| Name ohne Bereich | der Name ohne den Namen des Bereichs |

Mit Aliasen lassen sich am einfachsten kurze Sprechnamen vergeben. Sie werden pro Entität eingestellt unter **Einstellungen > Geräte & Dienste > Entitäten > (Entität) > Einstellungen > Sprachassistenten > Aliase**.

### Ziele

Die Liste der Ziele wird automatisch mit allen Benachrichtigungen im System gefüllt:

- Benachrichtigungs Entitäten, zum Beispiel Handy Apps oder Fernseher, werden über `notify.send_message` angesprochen
- Benachrichtigungsdienste werden direkt aufgerufen
- Geräte von Alexa Media Player (`notify.alexa_media_*`) bekommen zusätzlich die Ausgabeart aus **Alexa Ausgabe**: Sprachausgabe oder Ansage

Es können mehrere Ziele gleichzeitig gewählt werden. Fällt eines aus, bekommen die anderen die Nachricht trotzdem, und die Aktion meldet danach das fehlerhafte Ziel.

### Erweiterte Optionen

| Option | Beschreibung |
|---|---|
| Titel | Titel der Benachrichtigung bei Zielen, die einen Titel unterstützen |
| Alexa Ausgabe | Sprachausgabe oder Ansage, nur für Alexa Media Player |
| Nicht erreichbare melden | Hängt Entitäten an, die nicht erreichbar oder unbekannt sind |
| Nachricht bei nicht erreichbar | Text für diese Entitäten, Standard `Nicht erreichbar: {namen}.` |

## Beispiele

### Offene Fenster über einen Sprachassistenten

```yaml
action: state_announce.announce
data:
  entities:
    - binary_sensor.fenster_kueche
    - binary_sensor.fenster_bad
    - binary_sensor.fenster_buero
  state: "on"
  message_one: "Das Fenster {namen} ist offen."
  message_many: "{anzahl} Fenster sind offen: {namen}."
  message_none: "Alle Fenster sind zu."
  targets:
    - notify.alexa_media_wohnzimmer
  alexa_type: tts
```

### Vergessene Lichter aufs Handy

```yaml
action: state_announce.announce
data:
  entities:
    - light.flur
    - light.schreibtisch
    - light.eingang
  state: "on"
  message_one: "{namen} ist noch an."
  message_many: "{anzahl} Lichter sind noch an: {namen}."
  targets:
    - notify.mobile_app_telefon
  title: Licht
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

Die Aktion kann ihr Ergebnis in eine Antwortvariable schreiben:

```yaml
names: ["Küche", "Büro"]
count: 2
unavailable: []
message: "2 Fenster sind offen: Küche und Büro."
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
