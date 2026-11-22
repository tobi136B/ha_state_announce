"""Ziele der Ansage: Auswahlliste bauen und Nachrichten senden.

Unterstützt werden
- Benachrichtigungs Entitäten (notify.xyz als Entität, z. B. Handy, Wanddisplay)
- klassische Benachrichtigungsdienste (notify.xyz als Dienst, z. B. Alexa, LG TV)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from .announce import language_texts
from .const import ALEXA_SERVICE_PREFIX, DOMAIN, EXCLUDED_NOTIFY_SERVICES

_LOGGER = logging.getLogger(__name__)

KIND_ENTITY = "entity"
KIND_SERVICE = "service"


@dataclass(frozen=True)
class Target:
    """Ein aufgelöstes Ziel."""

    value: str  # z. B. notify.iphone_von_tobias
    kind: str  # KIND_ENTITY oder KIND_SERVICE

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
    """Eingabe auf die Form notify.xyz bringen."""
    value = value.strip()
    return value if "." in value else f"{NOTIFY_DOMAIN}.{value}"


def _notify_entities(hass: HomeAssistant) -> list[str]:
    """Alle Benachrichtigungs Entitäten."""
    return sorted(hass.states.async_entity_ids(NOTIFY_DOMAIN))


def _notify_services(hass: HomeAssistant) -> list[str]:
    """Alle klassischen Benachrichtigungsdienste, die als Ziel taugen."""
    services = hass.services.async_services_for_domain(NOTIFY_DOMAIN)
    return sorted(
        f"{NOTIFY_DOMAIN}.{name}"
        for name in services
        if name not in EXCLUDED_NOTIFY_SERVICES
    )


def build_target_options(hass: HomeAssistant) -> list[dict[str, str]]:
    """Auswahlliste für das Feld Ziele bauen (Entitäten zuerst)."""
    texts = language_texts(hass)
    options: list[dict[str, str]] = []

    entity_options = []
    for entity_id in _notify_entities(hass):
        state = hass.states.get(entity_id)
        name = state.name if state is not None else entity_id
        entity_options.append(
            {"value": entity_id, "label": f"{name} ({texts['entity']})"}
        )
    options.extend(sorted(entity_options, key=lambda item: item["label"].lower()))

    entity_ids = {option["value"] for option in entity_options}
    for service in _notify_services(hass):
        # Gleicher Name wie eine Entität: die Entität hat Vorrang
        if service in entity_ids:
            continue
        options.append(
            {
                "value": service,
                "label": f"{service.split('.', 1)[1]} ({texts['service']})",
            }
        )
    return options


def resolve_targets(hass: HomeAssistant, values: list[str]) -> list[Target]:
    """Eingaben in Ziele umwandeln. Unbekannte Ziele lösen einen Fehler aus."""
    targets: list[Target] = []
    seen: set[str] = set()
    for raw in values:
        value = _normalize(raw)
        if value in seen:
            continue
        seen.add(value)
        domain, _, object_id = value.partition(".")
        if domain != NOTIFY_DOMAIN or not object_id:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_target",
                translation_placeholders={"target": raw},
            )
        if hass.states.get(value) is not None:
            targets.append(Target(value, KIND_ENTITY))
        elif object_id not in EXCLUDED_NOTIFY_SERVICES and hass.services.has_service(
            NOTIFY_DOMAIN, object_id
        ):
            targets.append(Target(value, KIND_SERVICE))
        else:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="unknown_target",
                translation_placeholders={"target": raw},
            )
    return targets


async def _send_one(
    hass: HomeAssistant,
    target: Target,
    message: str,
    title: str | None,
    alexa_type: str,
) -> None:
    """Nachricht an ein einzelnes Ziel senden."""
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
) -> None:
    """An alle Ziele gleichzeitig senden.

    Fällt ein Ziel aus, bekommen die anderen ihre Nachricht trotzdem.
    Am Ende wird ein gesammelter Fehler gemeldet.
    """
    results = await asyncio.gather(
        *(_send_one(hass, target, message, title, alexa_type) for target in targets),
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
