"""Tests der Aktion state_announce.announce mit echten Aufrufen."""

from datetime import timedelta

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import area_registry as ar, entity_registry as er
from homeassistant.helpers.service import SERVICE_DESCRIPTION_CACHE
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.state_announce.const import DOMAIN


@pytest.fixture
async def setup(hass: HomeAssistant) -> list[ServiceCall]:
    """Integration einrichten und Benachrichtigungsdienste nachbilden."""
    hass.config.language = "de"
    calls: list[ServiceCall] = []

    async def _record(call: ServiceCall) -> None:
        calls.append(call)

    assert await async_setup_component(hass, "notify", {})
    hass.services.async_register("notify", "alexa_media_alexa_kuche", _record)
    hass.services.async_register("notify", "mobile_app_iphone", _record)

    entry = MockConfigEntry(domain=DOMAIN, title="Zustandsansage")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    hass.states.async_set("binary_sensor.a", "on", {"friendly_name": "Eltern rechts"})
    hass.states.async_set("binary_sensor.b", "on", {"friendly_name": "Gäste WC"})
    hass.states.async_set("binary_sensor.c", "off", {"friendly_name": "Tobi"})
    return calls


async def test_announce_alexa_and_phone(
    hass: HomeAssistant, setup: list[ServiceCall]
) -> None:
    """Alexa bekommt die Art, das Handy den Titel."""
    response = await hass.services.async_call(
        DOMAIN,
        "announce",
        {
            "entities": ["binary_sensor.a", "binary_sensor.b", "binary_sensor.c"],
            "state": "on",
            "message_one": "Das Fenster {namen} ist offen.",
            "message_many": "Die Fenster {namen} sind offen.",
            "targets": ["notify.alexa_media_alexa_kuche", "notify.mobile_app_iphone"],
            "title": "Fenster",
            "alexa_type": "announce",
        },
        blocking=True,
        return_response=True,
    )
    assert response["count"] == 2
    assert response["sent"] is True
    message = "Die Fenster Eltern rechts und Gäste WC sind offen."
    by_service = {call.service: call.data for call in setup}
    assert by_service["alexa_media_alexa_kuche"] == {
        "message": message,
        "data": {"type": "announce"},
    }
    assert by_service["mobile_app_iphone"] == {"message": message, "title": "Fenster"}


async def test_nothing_sent_without_sentence(
    hass: HomeAssistant, setup: list[ServiceCall]
) -> None:
    """Keiner offen und kein Satz bei keinem: nichts senden."""
    await hass.services.async_call(
        DOMAIN,
        "announce",
        {
            "entities": ["binary_sensor.c"],
            "message_many": "{namen} offen",
            "targets": ["notify.mobile_app_iphone"],
        },
        blocking=True,
    )
    assert setup == []


async def test_unknown_target(hass: HomeAssistant, setup: list[ServiceCall]) -> None:
    """Unbekanntes Ziel gibt eine verständliche Fehlermeldung."""
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "announce",
            {
                "entities": ["binary_sensor.a"],
                "message_many": "{namen}",
                "targets": ["notify.gibt_es_nicht"],
            },
            blocking=True,
        )


async def test_target_options(hass: HomeAssistant, setup: list[ServiceCall]) -> None:
    """Die Auswahlliste der Ziele enthält die Dienste."""
    description = hass.data[SERVICE_DESCRIPTION_CACHE][(DOMAIN, "announce")]
    options = description["fields"]["targets"]["selector"]["select"]["options"]
    values = [option["value"] for option in options]
    assert "notify.alexa_media_alexa_kuche" in values
    assert "notify.mobile_app_iphone" in values
    assert "notify.send_message" not in values
    # Beispiele in der Sprache von Home Assistant
    assert description["fields"]["message_many"]["example"] == (
        "{anzahl} eingeschaltet: {namen}."
    )


async def test_unload(hass: HomeAssistant, setup: list[ServiceCall]) -> None:
    """Nach dem Entladen meldet die Aktion einen Fehler."""
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert await hass.config_entries.async_unload(entry.entry_id)
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "announce",
            {
                "entities": ["binary_sensor.a"],
                "message_many": "{namen}",
                "targets": ["notify.mobile_app_iphone"],
            },
            blocking=True,
        )


async def test_target_options_follow_new_services(
    hass: HomeAssistant, setup: list[ServiceCall]
) -> None:
    """Später registrierte Dienste erscheinen in der Auswahlliste."""

    async def _noop(call: ServiceCall) -> None:
        return

    hass.services.async_register("notify", "alexa_media_spaeter", _noop)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=5))
    await hass.async_block_till_done()

    description = hass.data[SERVICE_DESCRIPTION_CACHE][(DOMAIN, "announce")]
    options = description["fields"]["targets"]["selector"]["select"]["options"]
    assert "notify.alexa_media_spaeter" in [option["value"] for option in options]


async def test_no_entities(hass: HomeAssistant, setup: list[ServiceCall]) -> None:
    """Ohne Entitäten und ohne Auswahl gibt es eine klare Fehlermeldung."""
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "announce",
            {"message_many": "{namen}", "targets": ["notify.mobile_app_iphone"]},
            blocking=True,
        )


async def test_announce_by_selection(
    hass: HomeAssistant, setup: list[ServiceCall]
) -> None:
    """Auswahl über einen Bereich mit Geräteklasse."""
    area = ar.async_get(hass).async_create("Flur")
    registry = er.async_get(hass)
    entry = registry.async_get_or_create("binary_sensor", "test", "flur_fenster")
    registry.async_update_entity(entry.entity_id, area_id=area.id)
    hass.states.async_set(
        entry.entity_id, "on", {"friendly_name": "Flur", "device_class": "window"}
    )
    response = await hass.services.async_call(
        DOMAIN,
        "announce",
        {
            "selection": {"area_id": area.id},
            "device_classes": ["window"],
            "message_many": "{anzahl} offen: {namen}",
            "targets": ["notify.mobile_app_iphone"],
        },
        blocking=True,
        return_response=True,
    )
    assert response["names"] == ["Flur"]
    assert setup[0].data["message"] == "1 offen: Flur"
