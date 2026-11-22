"""Tests der reinen Logik (Liste, Platzhalter, Namen, Satzwahl)."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar, entity_registry as er

from custom_components.state_announce.announce import (
    AnnounceResult,
    build_message,
    evaluate,
    fill_placeholders,
    join_names,
)


def test_join_names() -> None:
    """Namen werden lesbar verbunden."""
    assert join_names([], "und") == ""
    assert join_names(["A"], "und") == "A"
    assert join_names(["A", "B"], "und") == "A und B"
    assert join_names(["A", "B", "C"], "und") == "A, B und C"


def test_fill_placeholders() -> None:
    """Deutsche und englische Platzhalter werden ersetzt."""
    assert fill_placeholders("{namen} ({anzahl})", "A und B", 2) == "A und B (2)"
    assert fill_placeholders("{names} ({count})", "A and B", 2) == "A and B (2)"


async def test_evaluate_and_messages(hass: HomeAssistant) -> None:
    """Einzahl, Mehrzahl, keins und nicht erreichbar."""
    hass.config.language = "de"
    hass.states.async_set("binary_sensor.a", "on", {"friendly_name": "Fenster A"})
    hass.states.async_set("binary_sensor.b", "off", {"friendly_name": "Fenster B"})
    hass.states.async_set("binary_sensor.c", "on", {"friendly_name": "Fenster C"})
    hass.states.async_set(
        "binary_sensor.d", "unavailable", {"friendly_name": "Fenster D"}
    )

    ids = ["binary_sensor.a", "binary_sensor.b", "binary_sensor.c", "binary_sensor.d"]
    result = evaluate(hass, ids, "on", "name")
    assert result.names == ["Fenster A", "Fenster C"]
    assert result.unavailable == ["Fenster D"]

    one, many, none = "{namen} ist offen.", "{namen} sind offen.", "Alles zu."
    assert (
        build_message(hass, result, one, many, none, False, None)
        == "Fenster A und Fenster C sind offen."
    )
    assert (
        build_message(hass, result, one, many, none, True, None)
        == "Fenster A und Fenster C sind offen. Nicht erreichbar: Fenster D."
    )

    single = AnnounceResult(names=["Fenster A"])
    assert (
        build_message(hass, single, one, many, none, False, None)
        == "Fenster A ist offen."
    )
    # Ohne Satz bei einem wird der Satz bei mehreren genommen
    assert (
        build_message(hass, single, None, many, none, False, None)
        == "Fenster A sind offen."
    )

    empty = AnnounceResult()
    assert build_message(hass, empty, one, many, none, False, None) == "Alles zu."
    assert build_message(hass, empty, one, many, None, False, None) is None


async def test_name_sources(hass: HomeAssistant) -> None:
    """Alias, Name und Name ohne Bereich."""
    area = ar.async_get(hass).async_create("Schlafzimmer Eltern")
    registry = er.async_get(hass)
    entry = registry.async_get_or_create("binary_sensor", "test", "rechts")
    registry.async_update_entity(
        entry.entity_id, area_id=area.id, aliases={"Eltern rechts"}
    )
    hass.states.async_set(
        entry.entity_id,
        "on",
        {"friendly_name": "Fensterkontakt rechts Schlafzimmer Eltern"},
    )

    assert evaluate(hass, [entry.entity_id], "on", "alias").names == ["Eltern rechts"]
    assert evaluate(hass, [entry.entity_id], "on", "name").names == [
        "Fensterkontakt rechts Schlafzimmer Eltern"
    ]
    assert evaluate(hass, [entry.entity_id], "on", "name_without_area").names == [
        "Fensterkontakt rechts"
    ]


async def test_alias_fallback_and_english(hass: HomeAssistant) -> None:
    """Ohne Alias gilt der Name, englische Sprache nutzt "and"."""
    hass.config.language = "en"
    hass.states.async_set("binary_sensor.x", "on", {"friendly_name": "Kitchen"})
    hass.states.async_set("binary_sensor.y", "on", {"friendly_name": "Bath"})
    result = evaluate(hass, ["binary_sensor.x", "binary_sensor.y"], "on", "alias")
    assert build_message(hass, result, None, "{names} open", None, False, None) == (
        "Kitchen and Bath open"
    )
