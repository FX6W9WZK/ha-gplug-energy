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
    """Auto-configure sensors in the Energy Dashboard.

    Only runs if no gPlug sensors are already present in the grid config.
    This prevents duplicates when the user has already configured manually
    or when HA restarts.
    """
    try:
        from homeassistant.components.energy import async_get_manager
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
    existing_sources = prefs.get("energy_sources", [])

    # Collect all entity IDs from all existing grid sources
    all_existing_from = set()
    all_existing_to = set()
    for source in existing_sources:
        if source.get("type") == "grid":
            for flow in source.get("flow_from", []):
                stat = flow.get("stat_energy_from", "")
                if stat:
                    all_existing_from.add(stat)
            for flow in source.get("flow_to", []):
                stat = flow.get("stat_energy_to", "")
                if stat:
                    all_existing_to.add(stat)

    # Check if ANY gplug sensor is already in the energy config
    all_existing = all_existing_from | all_existing_to
    if any("gplug" in eid for eid in all_existing):
        _LOGGER.debug("gPlug sensors already in Energy Dashboard, skipping auto-config")
        return

    # Resolve gPlug entity IDs
    import_entities = []
    for key in ENERGY_IMPORT_KEYS:
        entity_id = _find_entity_id(ent_reg, entry_id, key)
        if entity_id:
            import_entities.append(entity_id)

    export_entities = []
    for key in ENERGY_EXPORT_KEYS:
        entity_id = _find_entity_id(ent_reg, entry_id, key)
        if entity_id:
            export_entities.append(entity_id)

    if not import_entities and not export_entities:
        _LOGGER.debug("No gPlug energy sensors found yet, skipping auto-config")
        return

    # Build grid source
    flow_from = [
        {
            "stat_energy_from": eid,
            "stat_cost": None,
            "entity_energy_price": None,
            "number_energy_price": None,
        }
        for eid in import_entities
    ]

    flow_to = [
        {
            "stat_energy_to": eid,
            "stat_compensation": None,
            "entity_energy_price": None,
            "number_energy_price": None,
        }
        for eid in export_entities
    ]

    # Find existing grid source or create new one
    grid_source = None
    for source in existing_sources:
        if source.get("type") == "grid":
            grid_source = source
            break

    if grid_source is None:
        grid_source = {
            "type": "grid",
            "flow_from": flow_from,
            "flow_to": flow_to,
            "cost_adjustment_day": 0.0,
        }
    else:
        grid_source["flow_from"] = grid_source.get("flow_from", []) + flow_from
        grid_source["flow_to"] = grid_source.get("flow_to", []) + flow_to

    # Rebuild sources list
    new_sources = []
    found_grid = False
    for source in existing_sources:
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
            "Auto-configured Energy Dashboard: import=%s, export=%s",
            import_entities,
            export_entities,
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
    return ent_reg.async_get_entity_id("sensor", DOMAIN, unique_id)
