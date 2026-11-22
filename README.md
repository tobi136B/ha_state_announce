<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/dark_logo.png">
    <img src="docs/logo.png" alt="State Announce" height="96">
  </picture>
</p>

# State Announce

[Deutsch](README.de.md) | English

Custom integration for Home Assistant. Provides the action `state_announce.announce`, which checks a list of entities and sends a message containing all entities that have a given state.

## Requirements

- Home Assistant 2026.3 or newer

## Installation

Home Assistant 2026.11 or newer:

1. Settings > Marketplace > Add from link
2. Enter `tobi136B/ha_state_announce`, type Integration
3. Install State Announce
4. Settings > Devices & services > Add integration > State Announce

Older versions: add the repository as a custom repository in HACS (type Integration).

## Action fields

| Field | Description |
|---|---|
| `entities` | Entities to check. Their order defines the order of the names. |
| `state` | State that is counted. Default `on`. |
| `message_one` | Message for one match. Optional, falls back to `message_many`. |
| `message_many` | Message for multiple matches. |
| `message_none` | Message for no match. Optional, nothing is sent if empty. |
| `targets` | Notify entities or notify services. |
| `name_source` | `alias`, `name` or `name_without_area`. Default `alias`. |
| `title` | Notification title. Optional. |
| `alexa_type` | `tts` or `announce`. Only used for Alexa Media Player targets. |
| `report_unavailable` | Append unavailable entities. Default `false`. |
| `message_unavailable` | Message for unavailable entities. Optional. |

### Placeholders

| Placeholder | Value |
|---|---|
| `{names}` / `{namen}` | Names joined as `A`, `A and B`, `A, B and C` |
| `{count}` / `{anzahl}` | Number of matches |

Placeholders are replaced as plain text. The joining word follows the language of Home Assistant.

### Name source

- `alias`: first alias of the entity, otherwise its name
- `name`: name of the entity
- `name_without_area`: name of the entity without the area name

### Targets

- Notify entities are called with `notify.send_message`.
- Notify services are called directly.
- Services of Alexa Media Player (`notify.alexa_media_*`) get `data.type` from `alexa_type`. The title is not sent to them.

If one target fails, the remaining targets are still served and the action raises an error afterwards.

## Example

```yaml
action: state_announce.announce
data:
  entities:
    - binary_sensor.contact_1
    - binary_sensor.contact_2
    - binary_sensor.contact_3
  state: "on"
  message_one: "{names} is open."
  message_many: "{count} are open: {names}."
  targets:
    - notify.mobile_app_phone
```

Result with two matches: `2 are open: Contact 1 and Contact 3.`

## Response

```yaml
names: ["Contact 1", "Contact 3"]
count: 2
unavailable: []
message: "2 are open: Contact 1 and Contact 3."
sent: true
```

## Development

```bash
pip install -r requirements_test.txt
pytest
ruff check custom_components tests
```

## License

MIT
