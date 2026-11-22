"""Einrichtung über die Oberfläche. Einmal hinzufügen, keine Einstellungen nötig."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
import voluptuous as vol

from .const import DOMAIN, TITLE


class StateAnnounceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Einrichtungsablauf der Zustandsansage."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Bestätigung durch den Benutzer."""
        if user_input is not None:
            return self.async_create_entry(title=TITLE, data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
