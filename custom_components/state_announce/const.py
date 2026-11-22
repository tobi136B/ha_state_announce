"""Konstanten der Integration Zustandsansage."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "state_announce"
TITLE: Final = "State Announce"

# Name der Aktion (state_announce.announce)
SERVICE_ANNOUNCE: Final = "announce"

# Felder der Aktion
ATTR_ENTITIES: Final = "entities"
ATTR_STATE: Final = "state"
ATTR_NAME_SOURCE: Final = "name_source"
ATTR_MESSAGE_ONE: Final = "message_one"
ATTR_MESSAGE_MANY: Final = "message_many"
ATTR_MESSAGE_NONE: Final = "message_none"
ATTR_REPORT_UNAVAILABLE: Final = "report_unavailable"
ATTR_MESSAGE_UNAVAILABLE: Final = "message_unavailable"
ATTR_TARGETS: Final = "targets"
ATTR_TITLE: Final = "title"
ATTR_ALEXA_TYPE: Final = "alexa_type"

# Namensquellen
NAME_SOURCE_ALIAS: Final = "alias"
NAME_SOURCE_NAME: Final = "name"
NAME_SOURCE_NAME_WITHOUT_AREA: Final = "name_without_area"
NAME_SOURCES: Final = [
    NAME_SOURCE_ALIAS,
    NAME_SOURCE_NAME,
    NAME_SOURCE_NAME_WITHOUT_AREA,
]

# Ausgabearten für Alexa Media Player
ALEXA_TYPE_TTS: Final = "tts"
ALEXA_TYPE_ANNOUNCE: Final = "announce"
ALEXA_TYPES: Final = [ALEXA_TYPE_TTS, ALEXA_TYPE_ANNOUNCE]

# Platzhalter im Satz (deutsch und englisch erlaubt)
PLACEHOLDERS_NAMES: Final = ("{namen}", "{names}")
PLACEHOLDERS_COUNT: Final = ("{anzahl}", "{count}")

# Dienste der Domain notify, die nicht als Ziel angeboten werden.
# send_message wird intern für Benachrichtigungs Entitäten genutzt,
# alexa_media ohne Gerät braucht zwingend ein extra Ziel.
EXCLUDED_NOTIFY_SERVICES: Final = {"send_message", "alexa_media"}

# Präfix der Dienste von Alexa Media Player
ALEXA_SERVICE_PREFIX: Final = "alexa_media"

# Speicherort in hass.data
DATA_BASE_DESCRIPTION: Final = f"{DOMAIN}_base_description"

# Sprachabhängige Texte, die nicht über die Übersetzungsdateien laufen
LANGUAGE_TEXTS: Final[dict[str, dict[str, str]]] = {
    "de": {
        "and": "und",
        "unavailable": "Nicht erreichbar: {namen}.",
        "entity": "Entität",
        "service": "Dienst",
        "title": "Zustandsansage",
        "example_one": "Das Fenster {namen} ist offen.",
        "example_many": "Die Fenster {namen} sind offen.",
        "example_none": "Alle Fenster sind zu.",
        "example_unavailable": "Nicht erreichbar: {namen}.",
        "example_title": "Fenster",
    },
    "en": {
        "and": "and",
        "unavailable": "Not reachable: {names}.",
        "entity": "entity",
        "service": "service",
        "title": "State Announce",
        "example_one": "The {names} window is open.",
        "example_many": "The {names} windows are open.",
        "example_none": "All windows are closed.",
        "example_unavailable": "Not reachable: {names}.",
        "example_title": "Windows",
    },
}
DEFAULT_LANGUAGE: Final = "en"
