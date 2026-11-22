"""Zustandsansage: sagt an, welche Entitäten einen bestimmten Zustand haben.

Beispiel: "Die Fenster Eltern rechts und Gäste WC sind offen."
Ohne Template, komplett über den UI Editor bedienbar.
"""

from __future__ import annotations

import copy
import logging
from pathlib import Path
from typing import Any

from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_SERVICE_REGISTERED, EVENT_SERVICE_REMOVED
from homeassistant.core import (
    Event,
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.service import async_set_service_schema
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.yaml import load_yaml_dict
import voluptuous as vol

from .announce import build_message, evaluate, language_texts
from .const import (
    ALEXA_TYPE_TTS,
    ALEXA_TYPES,
    ATTR_ALEXA_TYPE,
    ATTR_ENTITIES,
    ATTR_MESSAGE_MANY,
    ATTR_MESSAGE_NONE,
    ATTR_MESSAGE_ONE,
    ATTR_MESSAGE_UNAVAILABLE,
    ATTR_NAME_SOURCE,
    ATTR_REPORT_UNAVAILABLE,
    ATTR_STATE,
    ATTR_TARGETS,
    ATTR_TITLE,
    DATA_BASE_DESCRIPTION,
    DOMAIN,
    NAME_SOURCE_ALIAS,
    NAME_SOURCES,
    SERVICE_ANNOUNCE,
)
from .targets import build_target_options, resolve_targets, send_to_targets

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITIES): cv.entity_ids,
        vol.Optional(ATTR_STATE, default="on"): cv.string,
        vol.Optional(ATTR_NAME_SOURCE, default=NAME_SOURCE_ALIAS): vol.In(NAME_SOURCES),
        vol.Optional(ATTR_MESSAGE_ONE): cv.string,
        vol.Required(ATTR_MESSAGE_MANY): cv.string,
        vol.Optional(ATTR_MESSAGE_NONE): cv.string,
        vol.Optional(ATTR_REPORT_UNAVAILABLE, default=False): cv.boolean,
        vol.Optional(ATTR_MESSAGE_UNAVAILABLE): cv.string,
        vol.Required(ATTR_TARGETS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_ALEXA_TYPE, default=ALEXA_TYPE_TTS): vol.In(ALEXA_TYPES),
    }
)

type StateAnnounceConfigEntry = ConfigEntry[None]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Aktion registrieren (laut HA Richtlinie in async_setup)."""

    async def _async_handle_announce(call: ServiceCall) -> ServiceResponse:
        """Aktion Zustand ansagen ausführen."""
        if not hass.config_entries.async_loaded_entries(DOMAIN):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="not_loaded"
            )

        # Ziele zuerst prüfen, damit Tippfehler sofort auffallen
        targets = resolve_targets(hass, call.data[ATTR_TARGETS])

        result = evaluate(
            hass,
            call.data[ATTR_ENTITIES],
            call.data[ATTR_STATE],
            call.data[ATTR_NAME_SOURCE],
        )
        result.message = build_message(
            hass,
            result,
            message_one=call.data.get(ATTR_MESSAGE_ONE),
            message_many=call.data[ATTR_MESSAGE_MANY],
            message_none=call.data.get(ATTR_MESSAGE_NONE),
            report_unavailable=call.data[ATTR_REPORT_UNAVAILABLE],
            message_unavailable=call.data.get(ATTR_MESSAGE_UNAVAILABLE),
        )

        sent = False
        if result.message and targets:
            await send_to_targets(
                hass,
                targets,
                result.message,
                call.data.get(ATTR_TITLE),
                call.data[ATTR_ALEXA_TYPE],
            )
            sent = True

        if not call.return_response:
            return None
        return {
            "names": result.names,
            "count": result.count,
            "unavailable": result.unavailable,
            "message": result.message,
            "sent": sent,
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_ANNOUNCE,
        _async_handle_announce,
        schema=SERVICE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


async def _async_base_description(hass: HomeAssistant) -> dict[str, Any]:
    """Beschreibung der Aktion aus services.yaml einmalig laden."""
    if DATA_BASE_DESCRIPTION not in hass.data:
        path = Path(__file__).parent / "services.yaml"
        services = await hass.async_add_executor_job(load_yaml_dict, str(path))
        hass.data[DATA_BASE_DESCRIPTION] = services[SERVICE_ANNOUNCE]
    return hass.data[DATA_BASE_DESCRIPTION]


async def _async_update_target_options(hass: HomeAssistant) -> None:
    """Auswahlliste der Ziele in der Aktion aktualisieren."""
    description = copy.deepcopy(await _async_base_description(hass))
    fields = description["fields"]
    fields[ATTR_TARGETS]["selector"]["select"]["options"] = build_target_options(hass)

    # Beispiele passend zur Sprache von Home Assistant
    texts = language_texts(hass)
    advanced = fields["advanced_options"]["fields"]
    fields[ATTR_MESSAGE_ONE]["example"] = texts["example_one"]
    fields[ATTR_MESSAGE_MANY]["example"] = texts["example_many"]
    fields[ATTR_MESSAGE_NONE]["example"] = texts["example_none"]
    advanced[ATTR_MESSAGE_UNAVAILABLE]["example"] = texts["example_unavailable"]
    advanced[ATTR_TITLE]["example"] = texts["example_title"]
    async_set_service_schema(hass, DOMAIN, SERVICE_ANNOUNCE, description)


async def async_setup_entry(
    hass: HomeAssistant, entry: StateAnnounceConfigEntry
) -> bool:
    """Eintrag laden: Zielliste füllen und bei Änderungen nachführen."""
    debouncer: Debouncer[None] = Debouncer(
        hass,
        _LOGGER,
        cooldown=2.0,
        immediate=False,
        function=lambda: _async_update_target_options(hass),
    )

    @callback
    def _service_changed(event: Event) -> None:
        if event.data.get("domain") == NOTIFY_DOMAIN:
            debouncer.async_schedule_call()

    @callback
    def _registry_changed(event: Event[er.EventEntityRegistryUpdatedData]) -> None:
        entity_id = event.data.get("entity_id", "")
        if entity_id.startswith(f"{NOTIFY_DOMAIN}."):
            debouncer.async_schedule_call()

    @callback
    def _started(_hass: HomeAssistant) -> None:
        # Nach dem Start sind alle Geräte da, Liste einmal komplett neu bauen
        debouncer.async_schedule_call()

    entry.async_on_unload(
        hass.bus.async_listen(EVENT_SERVICE_REGISTERED, _service_changed)
    )
    entry.async_on_unload(
        hass.bus.async_listen(EVENT_SERVICE_REMOVED, _service_changed)
    )
    entry.async_on_unload(
        hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, _registry_changed)
    )
    entry.async_on_unload(async_at_started(hass, _started))
    entry.async_on_unload(debouncer.async_shutdown)

    await _async_update_target_options(hass)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: StateAnnounceConfigEntry
) -> bool:
    """Eintrag entladen: Zielliste auf den Grundzustand zurücksetzen."""
    description = await _async_base_description(hass)
    async_set_service_schema(hass, DOMAIN, SERVICE_ANNOUNCE, copy.deepcopy(description))
    return True
