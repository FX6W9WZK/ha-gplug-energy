"""Auto-configure the Home Assistant Energy Dashboard for gPlug sensors."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Sensor keys that should be added to the Energy Dashboard
ENERGY_IMPORT_KEYS = [
    "Ei1_1.8.1",  # Tariff 1 (HT)
    "Ei2_1.8.2",  # Tariff 2 (NT)
    "Ei_1.8",  # Total (fallback)
]

ENERGY_EXPORT_KEYS = [
    "Eo1_2.8.1",  # Tariff 1 (HT)
    "Eo2_2.8.2",  # Tariff 2 (NT)
    "Eo_2.8",  # Total (fallback)
]


async def async_configure_energy_dashboard(
    hass: HomeAssistant,
    entry_id: str,
) -> None:
    """Auto-configure sensors in the Energy Dashboard."""
    try:
        from homeassistant.components.energy import (
            async_get_manager,
        )
    except ImportError:
        _LOGGER.debug("Energy component not available, skipping auto-config")
        return

    try:
        manager = await async_get_manager(hass)
        prefs = manager.data
    except Exception:
        _LOGGER.debug("Could not access energy manager, skipping auto-config")
        return

    if prefs is None:
        _LOGGER.debug("Energy preferences not initialized yet")
        return

    ent_reg = er.async_get(hass)
    existing_grid = prefs.get("energy_sources", [])

    # Find existing grid source or create new one
    grid_source = None
    for source in existing_grid:
        if source.get("type") == "grid":
            grid_source = source
            break

    if grid_source is None:
        grid_source = {
            "type": "grid",
            "flow_from": [],
            "flow_to": [],
            "cost_adjustment_day": 0.0,
        }

    existing_from_ids = {
        f.get("stat_energy_from", "") for f in grid_source.get("flow_from", [])
    }
    existing_to_ids = {
        f.get("stat_energy_to", "") for f in grid_source.get("flow_to", [])
    }

    added_from = []
    added_to = []

    # Find and add import sensors (consumption)
    for key in ENERGY_IMPORT_KEYS:
        entity_id = _find_entity_id(ent_reg, entry_id, key)
        if entity_id and entity_id not in existing_from_ids:
            grid_source.setdefault("flow_from", []).append(
                {
                    "stat_energy_from": entity_id,
                    "stat_cost": None,
                    "entity_energy_price": None,
                    "number_energy_price": None,
                }
            )
            added_from.append(entity_id)
            existing_from_ids.add(entity_id)

    # Find and add export sensors (feed-in)
    for key in ENERGY_EXPORT_KEYS:
        entity_id = _find_entity_id(ent_reg, entry_id, key)
        if entity_id and entity_id not in existing_to_ids:
            grid_source.setdefault("flow_to", []).append(
                {
                    "stat_energy_to": entity_id,
                    "stat_compensation": None,
                    "entity_energy_price": None,
                    "number_energy_price": None,
                }
            )
            added_to.append(entity_id)
            existing_to_ids.add(entity_id)

    if not added_from and not added_to:
        _LOGGER.debug("No new sensors to add to Energy Dashboard")
        return

    # Update or insert grid source
    new_sources = []
    found_grid = False
    for source in existing_grid:
        if source.get("type") == "grid":
            new_sources.append(grid_source)
            found_grid = True
        else:
            new_sources.append(source)

    if not found_grid:
        new_sources.insert(0, grid_source)

    try:
        await manager.async_update({"energy_sources": new_sources})
        _LOGGER.info(
            "Auto-configured Energy Dashboard: from=%s, to=%s",
            added_from,
            added_to,
        )
    except Exception as exc:
        _LOGGER.warning("Could not auto-configure Energy Dashboard: %s", exc)


def _find_entity_id(
    ent_reg: er.EntityRegistry,
    entry_id: str,
    sensor_key: str,
) -> str | None:
    """Find an entity_id by its unique_id pattern."""
    unique_id = f"{entry_id}_{sensor_key}"
    entry = ent_reg.async_get_entity_id("sensor", DOMAIN, unique_id)
    return entry
