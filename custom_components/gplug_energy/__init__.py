"""
gPlug Energy – HACS Integration for gPlug Smart Meter Sensors.

Reads energy data from gPlugD/gPlugE/gPlugD-E devices (Tasmota-based)
via MQTT and creates properly configured sensor entities for the
Home Assistant Energy Dashboard.
"""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

CARD_URL = "/gplug_energy/gplug-energy-card.js"
CARD_PATH = Path(__file__).parent / "www" / "gplug-energy-card.js"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up gPlug Energy from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register custom Lovelace card
    await _register_card(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Auto-configure Energy Dashboard after sensors have had time to register
    async def _delayed_energy_config(_now=None):
        from .energy import async_configure_energy_dashboard

        await async_configure_energy_dashboard(hass, entry.entry_id)

    async_call_later(hass, 30, _delayed_energy_config)

    _LOGGER.info(
        "gPlug Energy integration loaded for topic: %s",
        entry.data.get("mqtt_topic", "n/a"),
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _register_card(hass: HomeAssistant) -> None:
    """Register the gPlug Energy Lovelace card as a frontend resource."""
    # Serve the JS file – handle both old and new HA API
    try:
        if hasattr(hass.http, "async_register_static_paths"):
            from homeassistant.components.http import StaticPathConfig

            await hass.http.async_register_static_paths(
                [StaticPathConfig(CARD_URL, str(CARD_PATH), True)]
            )
        else:
            hass.http.register_static_path(CARD_URL, str(CARD_PATH), cache_headers=True)
    except Exception as exc:
        _LOGGER.warning("Could not register card static path: %s", exc)
        return

    # Auto-add to Lovelace resources so card appears in card picker
    try:
        if "lovelace" not in hass.data:
            _LOGGER.debug("Lovelace not loaded yet, card served at %s", CARD_URL)
            return

        resources = None
        lovelace_data = hass.data.get("lovelace")

        if hasattr(lovelace_data, "resources"):
            resources = lovelace_data.resources
        elif isinstance(lovelace_data, dict) and "resources" in lovelace_data:
            resources = lovelace_data["resources"]

        if resources is None:
            _LOGGER.debug("Lovelace resources not found, card served at %s", CARD_URL)
            return

        # Check if already registered
        existing = []
        if hasattr(resources, "async_items"):
            existing = resources.async_items()

        for item in existing:
            if CARD_URL in item.get("url", ""):
                _LOGGER.debug("gPlug Energy card already registered")
                return

        # Register the resource
        await resources.async_create_item({"res_type": "module", "url": CARD_URL})
        _LOGGER.info("gPlug Energy card auto-registered at %s", CARD_URL)

    except Exception as exc:
        _LOGGER.debug(
            "Could not auto-register card resource (%s): %s",
            CARD_URL,
            exc,
        )
