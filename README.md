<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/dark_logo.png">
    <img src="docs/logo.png" alt="State Announce" height="96">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/tobi136B/ha_state_announce/actions/workflows/validate.yml"><img src="https://github.com/tobi136B/ha_state_announce/actions/workflows/validate.yml/badge.svg" alt="Validate"></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2026.3%2B-41BDF5" alt="Home Assistant 2026.3+">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/tobi136B/ha_state_announce" alt="License"></a>
</p>

# State Announce

[Deutsch](README.de.md) | English

State Announce adds one action to Home Assistant: **Announce states**. You give it a list of entities and a state. It sends a single message to one or more notification targets that names every entity currently in that state.

Typical uses:

- Which windows or doors are open
- Which lights are still on
- Who is at home
- Which devices are running
- Which batteries are low

The message is built from plain text with placeholders, so no templates are required.

## Installation

Home Assistant 2026.11 or newer:

1. Open **Settings > Marketplace** and select **Add from link**.
2. Enter `tobi136B/ha_state_announce` and choose the type **Integration**.
3. Install **State Announce**.
4. Go to **Settings > Devices & services > Add integration** and add **State Announce**.

On older versions, add the repository to HACS as a custom repository of type **Integration**.

## Usage

Add the action **Announce states** to an automation or script and fill in:

- **Entities** and/or **Selection**: what to check
- **State**: the state to look for, `on` by default
- **Messages**: what to send for one, several or no matches
- **Targets**: where to send it

### Entities and selection

There are two ways to choose what gets checked. They can be combined.

| Field | Description |
|---|---|
| Entities | Individual entities. Checked in the given order, filters do not apply. |
| Selection | Floors, areas, devices or labels, optionally with excluded targets. Resolved on every run, so entities added later are included automatically. |
| Device class | Filter for the selection, e.g. window or door. |
| Entity type | Filter for the selection, e.g. light or switch. |

The entity count shown in the selection is the total of the floor or area. The filters are applied when the action runs.

Entities found through the selection are sorted by name and follow the individually chosen ones. Disabled, hidden, diagnostic and configuration entities are skipped, so a battery sensor on a window contact is not counted as a window.

Example: Selection *Upstairs*, device class *Window* checks every window contact on that floor, including ones you add later.

### Messages and placeholders

There are three message fields, so the wording can match the number of results:

| Field | Sent when | Required |
|---|---|---|
| Message for one match | exactly one entity matches | no, falls back to the next field |
| Message for multiple matches | two or more entities match | yes |
| Message for no match | nothing matches | no, nothing is sent if empty |

Two placeholders can be used in every message:

| Placeholder | Replaced with |
|---|---|
| `{names}` | the names, joined as `A`, `A and B` or `A, B and C` |
| `{count}` | the number of matches |

German placeholders `{namen}` and `{anzahl}` work as well. The word used to join the names follows the language of your Home Assistant.

### Announcing the count

Put `{count}` in front of the names to say how many there are:

| Message | Result with 3 matches |
|---|---|
| `{count} windows are open: {names}.` | 3 windows are open: Kitchen, Bath and Office. |
| `There are {count} lights on, namely {names}.` | There are 3 lights on, namely Hall, Desk and Porch. |
| `{names} are open ({count} in total).` | Kitchen, Bath and Office are open (3 in total). |

Voice assistants such as Alexa read the number as a word.

### Names

The **Name source** option controls which name is used for each entity:

| Option | Name used |
|---|---|
| Alias, otherwise name (default) | the first alias of the entity, or its name if it has none |
| Name | the name of the entity |
| Name without area | the name with the area name removed |

Aliases are the easiest way to set short spoken names. They are set per entity under **Settings > Devices & services > Entities > (entity) > Settings > Voice assistants > Aliases**.

### Targets

The target list is filled automatically with every notification in your system:

- notify entities, for example mobile apps or TVs, are sent via `notify.send_message`
- notify services are called directly
- Alexa Media Player devices (`notify.alexa_media_*`) additionally get the output type from **Alexa output**: text to speech or announcement

Several targets can be selected at once. If one of them fails, the others still receive the message and the action reports the failed target afterwards.

### Advanced options

| Option | Description |
|---|---|
| Title | Notification title for targets that support one |
| Alexa output | Text to speech or announcement, used for Alexa Media Player only |
| Report unavailable | Appends entities that are unavailable or unknown |
| Message for unavailable | Text for those entities, default `Not reachable: {names}.` |

## Examples

### Open windows on a floor, announced by a voice assistant

```yaml
action: state_announce.announce
data:
  selection:
    floor_id: upstairs
  device_classes:
    - window
  state: "on"
  message_one: "The window {names} is open."
  message_many: "{count} windows are open: {names}."
  message_none: "All windows are closed."
  targets:
    - notify.alexa_media_living_room
  alexa_type: tts
```

### Lights left on, sent to a phone

```yaml
action: state_announce.announce
data:
  entities:
    - light.hall
    - light.desk
    - light.porch
  state: "on"
  message_one: "{names} is still on."
  message_many: "{count} lights are still on: {names}."
  targets:
    - notify.mobile_app_phone
  title: Lights
```

### Who is home

```yaml
action: state_announce.announce
data:
  entities:
    - person.anna
    - person.ben
  state: home
  message_one: "{names} is home."
  message_many: "{names} are home."
  message_none: "Nobody is home."
  targets:
    - notify.mobile_app_phone
```

## Response data

The action can return its result to a response variable:

```yaml
names: ["Kitchen", "Office"]
count: 2
unavailable: []
message: "2 windows are open: Kitchen and Office."
sent: true
```

## Development

```bash
pip install -r requirements_test.txt
pytest
ruff check custom_components tests
```

## License

[MIT](LICENSE)
