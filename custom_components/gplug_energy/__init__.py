"""
gPlugD Energy – HACS Integration for gPlugD Smart Meter Sensors.

Reads energy data from gPlugD/gPlugE/gPlugD-E devices (Tasmota-based)
via MQTT and creates properly configured sensor entities for the
Home Assistant Energy Dashboard.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

_MANIFEST_PATH = Path(__file__).parent / "manifest.json"
_VERSION = json.loads(_MANIFEST_PATH.read_text()).get("version", "0.0.0")

CARD_STATIC_URL = "/gplug_energy/gplug-energy-card.js"
CARD_URL = f"{CARD_STATIC_URL}?v={_VERSION}"
CARD_PATH = Path(__file__).parent / "www" / "gplug-energy-card.js"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up gPlugD Energy from a config entry."""
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
        "gPlugD Energy integration loaded for topic: %s",
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
    """Register the gPlugD Energy Lovelace card as a frontend resource."""
    # Step 1: Serve the JS file via HTTP (static path without query string)
    try:
        if hasattr(hass.http, "async_register_static_paths"):
            from homeassistant.components.http import StaticPathConfig

            await hass.http.async_register_static_paths(
                [StaticPathConfig(CARD_STATIC_URL, str(CARD_PATH), True)]
            )
        else:
            hass.http.register_static_path(
                CARD_STATIC_URL, str(CARD_PATH), cache_headers=True
            )
        _LOGGER.info("gPlugD card served at %s", CARD_STATIC_URL)
    except Exception as exc:
        _LOGGER.warning("Could not serve card file: %s", exc)
        return

    # Step 2: Register in Lovelace resources with version for cache busting
    await _add_lovelace_resource(hass, CARD_URL)


async def _add_lovelace_resource(hass: HomeAssistant, url: str) -> None:
    """Add or update a JS module in Lovelace resources (with version cache-bust)."""
    storage_path = Path(hass.config.path(".storage")) / "lovelace_resources"

    try:
        # Read existing resources
        data = {"data": {"items": []}, "version": 1, "key": "lovelace_resources"}
        if storage_path.exists():
            raw = await hass.async_add_executor_job(storage_path.read_text)
            data = json.loads(raw)

        items = data.get("data", {}).get("items", [])

        # Check if already registered (match on base URL without ?v=)
        for item in items:
            existing_url = item.get("url", "")
            if CARD_STATIC_URL in existing_url:
                if existing_url == url:
                    _LOGGER.debug("gPlugD card already registered with current version")
                    return
                # Update version
                item["url"] = url
                data["data"]["items"] = items
                content = json.dumps(data, indent=2)
                await hass.async_add_executor_job(storage_path.write_text, content)
                _LOGGER.info("gPlugD card updated to %s", url)
                return

        # Not found – add new entry
        existing_ids = [
            int(item.get("id", "0"))
            for item in items
            if str(item.get("id", "")).isdigit()
        ]
        next_id = str(max(existing_ids, default=0) + 1)

        items.append({"id": next_id, "type": "module", "url": url})
        data["data"]["items"] = items

        content = json.dumps(data, indent=2)
        await hass.async_add_executor_job(storage_path.write_text, content)

        _LOGGER.info(
            "gPlugD card registered in lovelace_resources (id=%s, url=%s)",
            next_id,
            url,
        )

    except Exception as exc:
        _LOGGER.warning("Could not register card in lovelace_resources: %s", exc)
        _LOGGER.warning(
            "Please add manually: Settings > Dashboards > Resources > "
            "Add Resource > URL: %s > Type: JavaScript Module",
            url,
        )
