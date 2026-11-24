<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/dark_logo.png">
    <img src="docs/logo.png" alt="State Announce" height="96">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/tobi136B/ha_state_announce/actions/workflows/validate.yml"><img src="https://github.com/tobi136B/ha_state_announce/actions/workflows/validate.yml/badge.svg" alt="Validate"></a>
  <a href="https://github.com/tobi136B/ha_state_announce/releases"><img src="https://img.shields.io/github/v/release/tobi136B/ha_state_announce" alt="Release"></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2026.3%2B-41BDF5" alt="Home Assistant 2026.3+">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/tobi136B/ha_state_announce" alt="License"></a>
</p>

# State Announce

[Deutsch](README.de.md) | English

Sometimes you don't want to know *whether* something is on, open or detected. You want to know *which*. State Announce takes a group of entities, picks out the ones in the state you care about and turns them into one natural sentence:

> "2 lights are still on: Hallway and Garage."
> "Person and animal detected."
> "Battery low: Front door and Bathroom sensor."

That sentence goes wherever you want it: a phone notification, a TV, a smart speaker, Alexa, or any speaker Home Assistant can talk through. No templates involved.

## What it can check

Anything that has a state. A few ideas:

- lights or switches left on
- open windows, doors or covers
- people, vehicles or animals detected by a camera
- who is at home
- batteries below a certain level
- devices that are running or reporting a problem

You pick the entities one by one, or let it find them by floor, area, device or label. A selection is looked up again every time the action runs, so devices you add later are included automatically.

## Where it can send

| Target | How the message arrives |
|---|---|
| Notify entities (mobile app, TV, wall display, …) | as a notification |
| Notify services (older integrations) | as a notification |
| Media players (Google, Sonos, HA Voice, …) | spoken via a text to speech engine |
| Alexa via [Alexa Media Player](https://github.com/alandtse/alexa_media_player) | spoken, plain or as an announcement with chime |

All available targets show up in a dropdown. You can pick several at once.

## Installation

Home Assistant 2026.11 or newer:

1. Open **Settings > Marketplace** and select **Add from link**.
2. Enter `tobi136B/ha_state_announce` and choose the type **Integration**.
3. Install **State Announce**.
4. Go to **Settings > Devices & services > Add integration** and add **State Announce**.

On older versions, add the repository to HACS as a custom repository of type **Integration**.

## Usage

Add the action **Announce states** to an automation or script.

### What to check

| Field | Description |
|---|---|
| Entities | Individual entities, checked in the given order. |
| Selection | Floors, areas, devices or labels, with optional exclusions. |
| Device class | Filter for the selection, e.g. window, motion or battery. |
| Entity type | Filter for the selection, e.g. light or switch. |
| State | The state or number to look for. Default `on`. |
| Comparison | is equal to, is not equal to, is above, is below. |

The entity count shown under Selection is the total of the floor or area. The filters are applied when the action runs. Disabled, hidden, diagnostic and configuration entities are always skipped.

### What to say

| Field | Sent when |
|---|---|
| Message for one match | exactly one entity matches (falls back to the next field if empty) |
| Message for multiple matches | two or more match |
| Message for no match | nothing matches (nothing is sent if empty) |

Use these placeholders in any message:

| Placeholder | Replaced with |
|---|---|
| `{names}` | the names, joined as `A`, `A and B` or `A, B and C` |
| `{count}` | how many matched |

`{namen}` and `{anzahl}` work too. The joining word follows the language of your Home Assistant.

Having separate messages for one and for several matches means the grammar is always right, and you can decide whether the count should be spoken:

| Message | Result with 2 matches |
|---|---|
| `{count} lights are still on: {names}.` | 2 lights are still on: Hallway and Garage. |
| `Still on: {names}.` | Still on: Hallway and Garage. |
| `{names} detected.` | Person and animal detected. |

Voice output reads the number as a word.

### Names

The **Name source** option decides what is said for each entity: its alias, its name, or its name without the area. Aliases are the easiest way to get short, natural names such as "Hallway" or "animal". You set them per entity under **Settings > Devices & services > Entities > (entity) > Settings > Voice assistants > Aliases**.

### Advanced options

| Option | Description |
|---|---|
| Name source | Alias (otherwise name), name, or name without area |
| Text to speech engine | Used for media player targets. Empty: the first available engine |
| Title | Notification title for targets that support one |
| Alexa output | Plain speech or announcement with chime, Alexa Media Player only |
| Report unavailable | Also mention entities that are unavailable |
| Message for unavailable | Default `Not reachable: {names}.` |

If one target fails, the others still get the message. The action reports the failed target afterwards.

## Examples

### Camera detections

```yaml
action: state_announce.announce
data:
  entities:
    - binary_sensor.front_door_person
    - binary_sensor.front_door_vehicle
    - binary_sensor.front_door_animal
  message_one: "{names} detected."
  message_many: "{names} detected."
  targets:
    - media_player.living_room_speaker
```

With aliases "Person", "Vehicle" and "Animal", two detections at once are announced as "Person and animal detected."

### Lights left on

```yaml
action: state_announce.announce
data:
  selection:
    floor_id: ground_floor
  domains:
    - light
  message_one: "{names} is still on."
  message_many: "{count} lights are still on: {names}."
  targets:
    - notify.mobile_app_phone
  title: Lights
```

### Low batteries

```yaml
action: state_announce.announce
data:
  selection:
    label_id: battery_powered
  device_classes:
    - battery
  domains:
    - sensor
  state: "20"
  comparison: below
  message_one: "Battery low: {names}."
  message_many: "{count} batteries are low: {names}."
  targets:
    - notify.mobile_app_phone
```

### Open windows on a floor

```yaml
action: state_announce.announce
data:
  selection:
    floor_id: upstairs
  device_classes:
    - window
  message_one: "{names} is open."
  message_many: "{count} windows are open: {names}."
  message_none: "All windows are closed."
  targets:
    - notify.alexa_media_kitchen
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

The action can hand its result to a response variable, for example to use the sentence somewhere else:

```yaml
names: ["Hallway", "Garage"]
count: 2
unavailable: []
message: "2 lights are still on: Hallway and Garage."
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
