"""Tests der reinen Logik (Liste, Platzhalter, Namen, Satzwahl)."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    entity_registry as er,
    floor_registry as fr,
)

from custom_components.state_announce.announce import (
    AnnounceResult,
    build_message,
    collect_entities,
    evaluate,
    fill_placeholders,
    join_names,
    state_matches,
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


async def test_collect_by_floor_with_filters(hass: HomeAssistant) -> None:
    """Auswahl über Etage, gefiltert nach Geräteklasse, Diagnose fällt weg."""
    floor = fr.async_get(hass).async_create("Obergeschoss")
    area_a = ar.async_get(hass).async_create("Bad", floor_id=floor.floor_id)
    area_b = ar.async_get(hass).async_create("Büro", floor_id=floor.floor_id)
    registry = er.async_get(hass)

    def _add(unique_id, area_id, name, device_class, category=None):
        entry = registry.async_get_or_create(
            "binary_sensor", "test", unique_id, entity_category=category
        )
        registry.async_update_entity(entry.entity_id, area_id=area_id)
        hass.states.async_set(
            entry.entity_id,
            "on",
            {"friendly_name": name, "device_class": device_class},
        )
        return entry.entity_id

    window_b = _add("w_b", area_b.id, "Büro", "window")
    window_a = _add("w_a", area_a.id, "Bad", "window")
    _add("door", area_a.id, "Tür", "door")
    _add("bat", area_a.id, "Batterie", "battery", er.EntityCategory.DIAGNOSTIC)
    explicit = "binary_sensor.extra"
    hass.states.async_set(explicit, "on", {"friendly_name": "Zusatz"})

    result = collect_entities(
        hass,
        [explicit],
        {"floor_id": floor.floor_id},
        ["window", "battery"],
        [],
        "name",
    )
    # Erst die einzeln gewählte, dann alphabetisch; Tür und Batterie fehlen
    assert result == [explicit, window_a, window_b]

    # Filter Entitätstyp schließt alles außer Licht aus
    assert (
        collect_entities(hass, [], {"floor_id": floor.floor_id}, [], ["light"], "name")
        == []
    )


async def test_collect_with_exclude(hass: HomeAssistant) -> None:
    """Ausgenommene Entitäten werden nicht geprüft."""
    area = ar.async_get(hass).async_create("Flur")
    registry = er.async_get(hass)
    ids = []
    for unique_id in ("a", "b"):
        entry = registry.async_get_or_create("binary_sensor", "test", unique_id)
        registry.async_update_entity(entry.entity_id, area_id=area.id)
        hass.states.async_set(entry.entity_id, "on", {"friendly_name": unique_id})
        ids.append(entry.entity_id)

    result = collect_entities(
        hass,
        [],
        {"area_id": area.id, "exclude": {"entity_id": [ids[0]]}},
        [],
        [],
        "name",
    )
    assert result == [ids[1]]


def test_state_matches() -> None:
    """Gleich, ungleich, größer und kleiner."""
    assert state_matches("on", "ON", "equal")
    assert state_matches("off", "on", "not_equal")
    assert state_matches("15", "20", "below")
    assert state_matches("21,5", "20", "above")
    assert not state_matches("unknown", "20", "below")
    assert not state_matches("25", "20", "below")
