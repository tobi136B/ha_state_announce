<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/dark_logo.png">
    <img src="docs/logo.png" alt="State Announce" height="96">
  </picture>
</p>

# State Announce

[Deutsch](README.de.md) | **English**

A Home Assistant integration that announces which entities have a certain state. For example:

> “The windows Parents right and Guest WC are open.”

Everything works through a normal action in the UI editor. **No templates needed.**

## Features

- Action **“Announce states”** (`state_announce.announce`) for automations and scripts
- Separate sentence for **one**, **many** and **no** match, so singular and plural are always right
- Names as a readable list: “A”, “A and B”, “A, B and C” (German “und”, English “and”)
- Selectable **name source**: alias, name or name without area
- **Targets** from a dropdown: Alexa (Alexa Media Player), phones, TVs, wall displays and every other notification; several at once
- Alexa: plain text to speech or announcement with chime
- Optionally report unreachable devices
- Response data (names, count, sentence) for further use
- English and German, own icon and logo

## Requirements

- Home Assistant **2026.3** or newer
- For Alexa: the [Alexa Media Player](https://github.com/alandtse/alexa_media_player) integration

## Installation

1. **Settings**, **Marketplace**
2. **Add from link** (top right)
3. Enter `tobi136B/ha_state_announce` and select **Add** (type **Integration** if asked)
4. Install **State Announce** (restart Home Assistant if asked)
5. **Settings**, **Devices & services**, **Add integration**, select **State Announce** and confirm

On Home Assistant before 2026.11, use HACS: menu (three dots), **Custom repositories**, add the link with type **Integration**.

## Usage

In an automation, choose **Add action** and select **Announce states**.

| Field | Meaning |
|---|---|
| Entities | What gets checked. The order here is the order in the announcement. |
| State | Which state counts. Windows and doors are open when “On”. Custom values (e.g. `open`, `home`) can be typed. |
| Sentence for one | Used when exactly one matches. Empty = sentence for many. |
| Sentence for many | Used when several match. Required. |
| Sentence for none | Used when nothing matches. Empty = nothing is sent. |
| Targets | Where the message goes. Several allowed. |
| **Advanced** | |
| Name source | Alias (otherwise name), name or name without area |
| Title | Title for phone notifications |
| Alexa type | Text to speech or announcement with chime |
| Report unreachable | Also announces which devices are unreachable |
| Sentence for unreachable | Own sentence for that, default: “Not reachable: …” |

### Placeholders

| Placeholder | Replaced by |
|---|---|
| `{names}` or `{namen}` | the names, e.g. “Parents right, Guest WC and Office” |
| `{count}` or `{anzahl}` | the number, e.g. “3” |

This is a plain text replacement, not a template.

### Own names

With the name source **Alias, otherwise name** the announcement uses the entity's alias. To set one:

**Settings**, **Devices & services**, **Entities**, open the entity, gear icon, **Voice assistants**, **Aliases**, add an alias (e.g. “Parents right”).

Without an alias, the normal name is used.

### Example (YAML view)

```yaml
action: state_announce.announce
data:
  entities:
    - binary_sensor.window_parents_left
    - binary_sensor.window_parents_right
    - binary_sensor.window_guest_wc
  state: "on"
  message_one: "The {names} window is open."
  message_many: "The windows {names} are open."
  targets:
    - notify.alexa_media_kitchen
  alexa_type: tts
```

### Response data

With a **response variable** on the action you get:

```yaml
names: ["Parents right", "Guest WC"]
count: 2
unavailable: []
message: "The windows Parents right and Guest WC are open."
sent: true
```

## Notes

- The target list fills itself with all notifications and updates when new ones appear. After adding a device, reload the page once.
- If one target fails, the others still get their message. The automation then reports an error naming the failed target.
- If an entity and a service have the same name, the entity is used.
- The language of “and” and of the default texts follows the language set in Home Assistant.

## Development

```bash
pip install -r requirements_test.txt
pytest
ruff check custom_components tests
```

## License

MIT
