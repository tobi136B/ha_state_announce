"""Ziele der Ansage: Auswahlliste bauen und Nachrichten senden.

Drei Arten von Zielen werden unterstützt:
- Benachrichtigungs Entitäten (notify.*), z. B. Handy App, Fernseher, Wanddisplay
- Benachrichtigungsdienste (notify.*), z. B. Alexa Media Player, ältere Integrationen
- Lautsprecher (media_player.*), Ausgabe als Sprache über eine TTS Engine
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er

from .announce import language_texts
from .const import (
    ALEXA_PLATFORM,
    ALEXA_SERVICE_PREFIX,
    DOMAIN,
    EXCLUDED_NOTIFY_SERVICES,
    MEDIA_PLAYER_DOMAIN,
    TTS_DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

KIND_ENTITY = "entity"
KIND_SERVICE = "service"
KIND_SPEAKER = "speaker"


@dataclass(frozen=True)
class Target:
    """Ein aufgelöstes Ziel."""

    value: str  # z. B. notify.mobile_app_phone oder media_player.kitchen
    kind: str  # KIND_ENTITY, KIND_SERVICE oder KIND_SPEAKER

    @property
    def object_id(self) -> str:
        """Teil nach dem Punkt."""
        return self.value.split(".", 1)[1]

    @property
    def is_alexa(self) -> bool:
        """Ziel ist ein Gerät von Alexa Media Player."""
        return self.kind == KIND_SERVICE and self.object_id.startswith(
            ALEXA_SERVICE_PREFIX
        )


def _normalize(value: str) -> str:
    """Eingabe ohne Domain als notify.xyz verstehen."""
    value = value.strip()
    return value if "." in value else f"{NOTIFY_DOMAIN}.{value}"


def _notify_services(hass: HomeAssistant) -> list[str]:
    """Benachrichtigungsdienste, die als Ziel taugen."""
    services = hass.services.async_services_for_domain(NOTIFY_DOMAIN)
    return sorted(
        f"{NOTIFY_DOMAIN}.{name}"
        for name in services
        if name not in EXCLUDED_NOTIFY_SERVICES
    )


def _speakers(hass: HomeAssistant) -> list[str]:
    """Media Player, die sich für Sprachausgabe eignen.

    Geräte von Alexa Media Player werden ausgelassen, sie sind schon
    über ihre Benachrichtigungsdienste erreichbar und unterstützen
    die normale Sprachausgabe von Home Assistant nicht.
    """
    registry = er.async_get(hass)
    speakers = []
    for entity_id in hass.states.async_entity_ids(MEDIA_PLAYER_DOMAIN):
        entry = registry.async_get(entity_id)
        if entry is not None and entry.platform == ALEXA_PLATFORM:
            continue
        speakers.append(entity_id)
    return speakers


def _name(hass: HomeAssistant, entity_id: str) -> str:
    state = hass.states.get(entity_id)
    return state.name if state is not None else entity_id


def build_target_options(hass: HomeAssistant) -> list[dict[str, str]]:
    """Auswahlliste für das Feld Ziele bauen."""
    texts = language_texts(hass)

    def _sorted(items: list[dict[str, str]]) -> list[dict[str, str]]:
        return sorted(items, key=lambda item: item["label"].lower())

    notify_entities = hass.states.async_entity_ids(NOTIFY_DOMAIN)
    options = _sorted(
        [
            {
                "value": entity_id,
                "label": f"{_name(hass, entity_id)} ({texts['kind_notify']})",
            }
            for entity_id in notify_entities
        ]
    )
    options += _sorted(
        [
            {
                "value": entity_id,
                "label": f"{_name(hass, entity_id)} ({texts['kind_speaker']})",
            }
            for entity_id in _speakers(hass)
        ]
    )
    # Gleicher Name wie eine Entität: die Entität hat Vorrang
    options += [
        {
            "value": service,
            "label": f"{service.split('.', 1)[1]} ({texts['kind_service']})",
        }
        for service in _notify_services(hass)
        if service not in notify_entities
    ]
    return options


def resolve_targets(hass: HomeAssistant, values: list[str]) -> list[Target]:
    """Eingaben in Ziele umwandeln. Unbekannte Ziele lösen einen Fehler aus."""
    targets: list[Target] = []
    for raw in dict.fromkeys(values):
        value = _normalize(raw)
        domain, _, object_id = value.partition(".")
        if domain == MEDIA_PLAYER_DOMAIN and hass.states.get(value) is not None:
            targets.append(Target(value, KIND_SPEAKER))
        elif domain == NOTIFY_DOMAIN and hass.states.get(value) is not None:
            targets.append(Target(value, KIND_ENTITY))
        elif (
            domain == NOTIFY_DOMAIN
            and object_id not in EXCLUDED_NOTIFY_SERVICES
            and hass.services.has_service(NOTIFY_DOMAIN, object_id)
        ):
            targets.append(Target(value, KIND_SERVICE))
        elif domain not in (NOTIFY_DOMAIN, MEDIA_PLAYER_DOMAIN):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_target",
                translation_placeholders={"target": raw},
            )
        else:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="unknown_target",
                translation_placeholders={"target": raw},
            )
    return targets


def resolve_tts_engine(
    hass: HomeAssistant, targets: list[Target], engine: str | None
) -> str | None:
    """TTS Engine für Lautsprecher Ziele bestimmen.

    Ohne Angabe wird die erste vorhandene Engine genommen.
    """
    if not any(target.kind == KIND_SPEAKER for target in targets):
        return None
    if engine:
        if hass.states.get(engine) is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="unknown_tts_engine",
                translation_placeholders={"engine": engine},
            )
        return engine
    engines = sorted(hass.states.async_entity_ids(TTS_DOMAIN))
    if not engines:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="no_tts_engine"
        )
    return engines[0]


async def _send_one(
    hass: HomeAssistant,
    target: Target,
    message: str,
    title: str | None,
    alexa_type: str,
    tts_engine: str | None,
) -> None:
    """Nachricht an ein einzelnes Ziel senden."""
    if target.kind == KIND_SPEAKER:
        await hass.services.async_call(
            TTS_DOMAIN,
            "speak",
            {
                "entity_id": tts_engine,
                "media_player_entity_id": target.value,
                "message": message,
            },
            blocking=True,
        )
        return

    if target.kind == KIND_ENTITY:
        data: dict[str, Any] = {"entity_id": target.value, "message": message}
        if title:
            data["title"] = title
        await hass.services.async_call(
            NOTIFY_DOMAIN, "send_message", data, blocking=True
        )
        return

    data = {"message": message}
    if target.is_alexa:
        # Alexa Media Player braucht die Ausgabeart, den Titel liest sie nicht vor
        data["data"] = {"type": alexa_type}
    elif title:
        data["title"] = title
    await hass.services.async_call(NOTIFY_DOMAIN, target.object_id, data, blocking=True)


async def send_to_targets(
    hass: HomeAssistant,
    targets: list[Target],
    message: str,
    title: str | None,
    alexa_type: str,
    tts_engine: str | None,
) -> None:
    """An alle Ziele gleichzeitig senden.

    Fällt ein Ziel aus, bekommen die anderen ihre Nachricht trotzdem.
    Danach wird ein gesammelter Fehler gemeldet.
    """
    results = await asyncio.gather(
        *(
            _send_one(hass, target, message, title, alexa_type, tts_engine)
            for target in targets
        ),
        return_exceptions=True,
    )
    failed: list[str] = []
    for target, result in zip(targets, results, strict=True):
        if isinstance(result, BaseException):
            _LOGGER.warning("Senden an %s fehlgeschlagen: %s", target.value, result)
            failed.append(f"{target.value} ({result})")
    if failed:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="send_failed",
            translation_placeholders={"targets": ", ".join(failed)},
        )
