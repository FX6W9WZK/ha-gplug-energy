"""Diagnostics support for gPlugD Energy."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return {
        "config_entry_data": {
            k: "**REDACTED**" if "password" in k.lower() else v
            for k, v in entry.data.items()
        },
        "config_entry_options": dict(entry.options),
    }
