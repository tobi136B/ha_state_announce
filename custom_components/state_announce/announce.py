"""Logik der Zustandsansage: Zustände prüfen, Namen ermitteln, Satz bauen.

Die Funktionen hier senden nichts. Sie liefern nur das Ergebnis,
damit sie sich einfach testen lassen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from homeassistant.const import ATTR_DEVICE_CLASS, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, split_entity_id
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

try:
    from homeassistant.helpers.target import TargetSelection
except ImportError:  # ältere Versionen von Home Assistant
    from homeassistant.helpers.target import TargetSelectorData as TargetSelection
from homeassistant.helpers.target import async_extract_referenced_entity_ids

from .const import (
    DEFAULT_LANGUAGE,
    LANGUAGE_TEXTS,
    NAME_SOURCE_ALIAS,
    NAME_SOURCE_NAME_WITHOUT_AREA,
    PLACEHOLDERS_COUNT,
    PLACEHOLDERS_NAMES,
)

# Zustände, die als "nicht erreichbar" gelten
UNAVAILABLE_STATES = {STATE_UNAVAILABLE, STATE_UNKNOWN}


@dataclass
class AnnounceResult:
    """Ergebnis einer Auswertung."""

    names: list[str] = field(default_factory=list)
    unavailable: list[str] = field(default_factory=list)
    message: str | None = None

    @property
    def count(self) -> int:
        """Anzahl der Treffer."""
        return len(self.names)


def language_texts(hass: HomeAssistant) -> dict[str, str]:
    """Texte passend zur eingestellten Sprache von Home Assistant."""
    language = (hass.config.language or DEFAULT_LANGUAGE).split("-")[0].lower()
    return LANGUAGE_TEXTS.get(language, LANGUAGE_TEXTS[DEFAULT_LANGUAGE])


def join_names(names: list[str], and_word: str) -> str:
    """Namen zu einer lesbaren Liste verbinden.

    ["A"]           -> "A"
    ["A", "B"]      -> "A und B"
    ["A", "B", "C"] -> "A, B und C"
    """
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return f"{', '.join(names[:-1])} {and_word} {names[-1]}"


def fill_placeholders(text: str, names_text: str, count: int) -> str:
    """Platzhalter im Satz ersetzen. Bewusst einfaches Ersetzen, kein Template."""
    for placeholder in PLACEHOLDERS_NAMES:
        text = text.replace(placeholder, names_text)
    for placeholder in PLACEHOLDERS_COUNT:
        text = text.replace(placeholder, str(count))
    return text.strip()


def _first_alias(entry: er.RegistryEntry | None) -> str | None:
    """Ersten gesetzten Alias einer Entität liefern."""
    if entry is None or not entry.aliases:
        return None
    aliases = entry.aliases
    # Je nach HA Version Menge (ohne Reihenfolge) oder Liste
    ordered = (
        list(aliases)
        if isinstance(aliases, (list, tuple))
        else sorted(alias for alias in aliases if isinstance(alias, str))
    )
    for alias in ordered:
        if isinstance(alias, str) and alias.strip():
            return alias.strip()
    return None


def _area_name(hass: HomeAssistant, entry: er.RegistryEntry | None) -> str | None:
    """Bereich der Entität ermitteln (eigener Bereich oder der des Geräts)."""
    if entry is None:
        return None
    area_id = entry.area_id
    if area_id is None and entry.device_id:
        device = dr.async_get(hass).async_get(entry.device_id)
        if device is not None:
            area_id = device.area_id
    if area_id is None:
        return None
    area = ar.async_get(hass).async_get_area(area_id)
    return area.name if area else None


def _remove_area(name: str, area: str | None) -> str:
    """Bereichsnamen aus dem Namen entfernen, Groß und Kleinschreibung egal."""
    if not area:
        return name
    cleaned = re.sub(re.escape(area), "", name, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -_,")
    # Bleibt nichts übrig, lieber den vollen Namen sagen
    return cleaned or name


def resolve_name(hass: HomeAssistant, entity_id: str, name_source: str) -> str:
    """Sprechnamen einer Entität nach der gewählten Namensquelle ermitteln."""
    entry = er.async_get(hass).async_get(entity_id)
    state = hass.states.get(entity_id)
    display_name = state.name if state is not None else None
    if not display_name and entry is not None:
        display_name = entry.name or entry.original_name
    display_name = display_name or entity_id

    if name_source == NAME_SOURCE_ALIAS:
        return _first_alias(entry) or display_name
    if name_source == NAME_SOURCE_NAME_WITHOUT_AREA:
        return _remove_area(display_name, _area_name(hass, entry))
    return display_name


def _matches_filters(
    hass: HomeAssistant,
    entity_id: str,
    device_classes: list[str],
    domains: list[str],
) -> bool:
    """Prüfen, ob eine Entität zu den Filtern Geräteklasse und Entitätstyp passt."""
    if domains and split_entity_id(entity_id)[0] not in domains:
        return False
    if device_classes:
        state = hass.states.get(entity_id)
        device_class = state.attributes.get(ATTR_DEVICE_CLASS) if state else None
        if device_class is None:
            # Ohne Zustand (z. B. nicht erreichbar) Geräteklasse aus der Registry
            entry = er.async_get(hass).async_get(entity_id)
            if entry is not None:
                device_class = entry.device_class or entry.original_device_class
        if device_class not in device_classes:
            return False
    return True


def collect_entities(
    hass: HomeAssistant,
    entities: list[str],
    selection: dict[str, Any] | None,
    device_classes: list[str],
    domains: list[str],
    name_source: str,
) -> list[str]:
    """Alle zu prüfenden Entitäten zusammenstellen.

    Zuerst die einzeln gewählten Entitäten in ihrer Reihenfolge, danach die
    über Etage, Bereich, Gerät oder Label gefundenen, sortiert nach Namen.
    Die Filter gelten nur für die Auswahl, einzeln gewählte Entitäten
    werden immer geprüft. Diagnose, Konfigurations und ausgeblendete
    Entitäten werden bei der Auswahl von Home Assistant bereits ausgelassen.
    """
    result = list(dict.fromkeys(entities))
    if not selection:
        return result

    selected = async_extract_referenced_entity_ids(hass, TargetSelection(selection))
    found = (selected.referenced | selected.indirectly_referenced) - set(result)
    registry = er.async_get(hass)
    filtered = [
        entity_id
        for entity_id in found
        if _matches_filters(hass, entity_id, device_classes, domains)
        and not (
            (entry := registry.async_get(entity_id)) is not None
            and entry.disabled_by is not None
        )
    ]
    filtered.sort(key=lambda entity_id: resolve_name(hass, entity_id, name_source))
    return result + filtered


def evaluate(
    hass: HomeAssistant,
    entity_ids: list[str],
    wanted_state: str,
    name_source: str,
) -> AnnounceResult:
    """Entitäten prüfen und Treffer sowie nicht erreichbare sammeln.

    Die Reihenfolge entspricht der Reihenfolge in der Aktion.
    """
    result = AnnounceResult()
    wanted = wanted_state.strip().lower()
    for entity_id in entity_ids:
        state = hass.states.get(entity_id)
        if state is None or state.state in UNAVAILABLE_STATES:
            result.unavailable.append(resolve_name(hass, entity_id, name_source))
            continue
        if state.state.lower() == wanted:
            result.names.append(resolve_name(hass, entity_id, name_source))
    return result


def build_message(
    hass: HomeAssistant,
    result: AnnounceResult,
    message_one: str | None,
    message_many: str,
    message_none: str | None,
    report_unavailable: bool,
    message_unavailable: str | None,
) -> str | None:
    """Passenden Satz auswählen und Platzhalter füllen.

    Rückgabe None heißt: nichts senden.
    """
    texts = language_texts(hass)
    parts: list[str] = []

    if result.count == 0:
        template = message_none
    elif result.count == 1:
        template = message_one or message_many
    else:
        template = message_many

    if template:
        parts.append(
            fill_placeholders(
                template, join_names(result.names, texts["and"]), result.count
            )
        )

    if report_unavailable and result.unavailable:
        parts.append(
            fill_placeholders(
                message_unavailable or texts["unavailable"],
                join_names(result.unavailable, texts["and"]),
                len(result.unavailable),
            )
        )

    message = " ".join(part for part in parts if part)
    return message or None
