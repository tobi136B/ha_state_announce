"""Konstanten der Integration Zustandsansage."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "state_announce"
TITLE: Final = "State Announce"

# Name der Aktion (state_announce.announce)
SERVICE_ANNOUNCE: Final = "announce"

# Felder der Aktion
ATTR_ENTITIES: Final = "entities"
ATTR_SELECTION: Final = "selection"
ATTR_DEVICE_CLASSES: Final = "device_classes"
ATTR_DOMAINS: Final = "domains"
ATTR_STATE: Final = "state"
ATTR_COMPARISON: Final = "comparison"
ATTR_NAME_SOURCE: Final = "name_source"
ATTR_MESSAGE_ONE: Final = "message_one"
ATTR_MESSAGE_MANY: Final = "message_many"
ATTR_MESSAGE_NONE: Final = "message_none"
ATTR_REPORT_UNAVAILABLE: Final = "report_unavailable"
ATTR_MESSAGE_UNAVAILABLE: Final = "message_unavailable"
ATTR_TARGETS: Final = "targets"
ATTR_TITLE: Final = "title"
ATTR_ALEXA_TYPE: Final = "alexa_type"
ATTR_TTS_ENGINE: Final = "tts_engine"

# Auswahl für den Filter Geräteklasse (eigene Werte sind zusätzlich erlaubt)
DEVICE_CLASS_OPTIONS: Final = [
    "window",
    "door",
    "garage_door",
    "opening",
    "lock",
    "motion",
    "occupancy",
    "presence",
    "moisture",
    "smoke",
    "gas",
    "carbon_monoxide",
    "problem",
    "running",
    "plug",
    "power",
    "connectivity",
    "battery",
]

# Auswahl für den Filter Entitätstyp (eigene Werte sind zusätzlich erlaubt)
DOMAIN_OPTIONS: Final = [
    "binary_sensor",
    "light",
    "switch",
    "cover",
    "lock",
    "fan",
    "climate",
    "media_player",
    "person",
    "device_tracker",
    "input_boolean",
    "sensor",
]

# Vergleich des Zustands
COMPARISON_EQUAL: Final = "equal"
COMPARISON_NOT_EQUAL: Final = "not_equal"
COMPARISON_ABOVE: Final = "above"
COMPARISON_BELOW: Final = "below"
COMPARISONS: Final = [
    COMPARISON_EQUAL,
    COMPARISON_NOT_EQUAL,
    COMPARISON_ABOVE,
    COMPARISON_BELOW,
]

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

# Alexa Media Player: Präfix der Dienste und Name der Plattform
ALEXA_SERVICE_PREFIX: Final = "alexa_media"
ALEXA_PLATFORM: Final = "alexa_media"

# Domains für Lautsprecher Ziele
MEDIA_PLAYER_DOMAIN: Final = "media_player"
TTS_DOMAIN: Final = "tts"

# Speicherort in hass.data
DATA_BASE_DESCRIPTION: Final = f"{DOMAIN}_base_description"

# Sprachabhängige Texte, die nicht über die Übersetzungsdateien laufen
LANGUAGE_TEXTS: Final[dict[str, dict[str, str]]] = {
    "de": {
        "and": "und",
        "unavailable": "Nicht erreichbar: {namen}.",
        "kind_notify": "Benachrichtigung",
        "kind_service": "Benachrichtigungsdienst",
        "kind_speaker": "Lautsprecher",
        "title": "Zustandsansage",
        "example_one": "{namen} ist eingeschaltet.",
        "example_many": "{anzahl} eingeschaltet: {namen}.",
        "example_none": "Nichts eingeschaltet.",
        "example_unavailable": "Nicht erreichbar: {namen}.",
        "example_title": "Status",
    },
    "en": {
        "and": "and",
        "unavailable": "Not reachable: {names}.",
        "kind_notify": "notification",
        "kind_service": "notification service",
        "kind_speaker": "speaker",
        "title": "State Announce",
        "example_one": "{names} is on.",
        "example_many": "{count} on: {names}.",
        "example_none": "Nothing is on.",
        "example_unavailable": "Not reachable: {names}.",
        "example_title": "Status",
    },
}
DEFAULT_LANGUAGE: Final = "en"
