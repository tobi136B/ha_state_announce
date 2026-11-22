# Changelog

## 0.2.0

- New field Selection: floors, areas, devices or labels, evaluated on every run
- New filters Device class and Entity type for the selection
- Entities is now optional, at least one of Entities or Selection is required

## 0.1.1

- Fix: target list was not updated after notify services or entities were added later (e.g. after a restart)

## 0.1.0

- Action `state_announce.announce`
- Messages for one, multiple and no match with placeholders for names and count
- Name source: alias, name, name without area
- Targets: notify entities and notify services, Alexa Media Player output type
- Optional reporting of unavailable entities
- Response data
