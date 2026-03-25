"""Constants for the gPlug Energy integration."""

DOMAIN = "gplug_energy"
MANUFACTURER = "Gantrisch Energie AG"
MODEL_GPLUGD = "gPlugD"
MODEL_GPLUGD_E = "gPlugD-E"
MODEL_GPLUGE = "gPlugE"

CONF_MQTT_TOPIC = "mqtt_topic"
CONF_DEVICE_NAME = "device_name"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_HTTP_HOST = "http_host"
CONF_CONNECTION_TYPE = "connection_type"

CONNECTION_MQTT = "mqtt"
CONNECTION_HTTP = "http"

DEFAULT_MQTT_TOPIC = "tele/gplugd/SENSOR"
DEFAULT_POLLING_INTERVAL = 10
DEFAULT_DEVICE_NAME = "gPlugD"

# ── OBIS-Code Sensor Mapping ──────────────────────────────────────────────
# Maps gPlug Tasmota script variable names to human-readable sensor configs.
# The gPlug Tasmota scripts use a JSON prefix (e.g. "ENERGY" or custom)
# and publish values via MQTT in the format:
#   tele/<topic>/SENSOR = {"Time":"...","ENERGY":{"Ei_1.8":1234.56,...}}
#
# Each entry: (json_key, name, unit, device_class, state_class, icon)

SENSOR_TYPES_ENERGY = {
    # ── Zählerstände (Energiewerte, kumulativ) ────────────────────────────
    "Ei_1.8": {
        "name": "Energiebezug Gesamt",
        "name_en": "Energy Import Total",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:transmission-tower-import",
    },
    "Ei1_1.8.1": {
        "name": "Energiebezug Tarif 1",
        "name_en": "Energy Import Tariff 1",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:counter",
    },
    "Ei2_1.8.2": {
        "name": "Energiebezug Tarif 2",
        "name_en": "Energy Import Tariff 2",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:counter",
    },
    "Eo_2.8": {
        "name": "Energieeinspeisung Gesamt",
        "name_en": "Energy Export Total",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:transmission-tower-export",
    },
    "Eo1_2.8.1": {
        "name": "Energieeinspeisung Tarif 1",
        "name_en": "Energy Export Tariff 1",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:counter",
    },
    "Eo2_2.8.2": {
        "name": "Energieeinspeisung Tarif 2",
        "name_en": "Energy Export Tariff 2",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:counter",
    },
    # ── Momentanwerte (Leistung) ──────────────────────────────────────────
    "Pi_1.7": {
        "name": "Bezugsleistung",
        "name_en": "Power Import",
        "unit": "kW",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash",
    },
    "Po_2.7": {
        "name": "Einspeiseleistung",
        "name_en": "Power Export",
        "unit": "kW",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash-outline",
    },
    # ── Leistung pro Phase ───────────────────────────────────────────────
    "P1i": {
        "name": "Bezugsleistung L1",
        "name_en": "Power Import L1",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash",
    },
    "P2i": {
        "name": "Bezugsleistung L2",
        "name_en": "Power Import L2",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash",
    },
    "P3i": {
        "name": "Bezugsleistung L3",
        "name_en": "Power Import L3",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash",
    },
    "P1o": {
        "name": "Einspeiseleistung L1",
        "name_en": "Power Export L1",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash-outline",
    },
    "P2o": {
        "name": "Einspeiseleistung L2",
        "name_en": "Power Export L2",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash-outline",
    },
    "P3o": {
        "name": "Einspeiseleistung L3",
        "name_en": "Power Export L3",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash-outline",
    },
    # ── Spannung pro Phase ────────────────────────────────────────────────
    "V1_32.7": {
        "name": "Spannung L1",
        "name_en": "Voltage L1",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "icon": "mdi:sine-wave",
    },
    "V2_52.7": {
        "name": "Spannung L2",
        "name_en": "Voltage L2",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "icon": "mdi:sine-wave",
    },
    "V3_72.7": {
        "name": "Spannung L3",
        "name_en": "Voltage L3",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "icon": "mdi:sine-wave",
    },
    # ── Strom pro Phase ───────────────────────────────────────────────────
    "I1_31.7": {
        "name": "Strom L1",
        "name_en": "Current L1",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
        "icon": "mdi:current-ac",
    },
    "I2_51.7": {
        "name": "Strom L2",
        "name_en": "Current L2",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
        "icon": "mdi:current-ac",
    },
    "I3_71.7": {
        "name": "Strom L3",
        "name_en": "Current L3",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
        "icon": "mdi:current-ac",
    },
}

# Alternative JSON keys used by some gPlug scripts (HDLC/DLMS variant)
SENSOR_KEY_ALIASES = {
    "Total_in": "Ei_1.8",
    "Total_out": "Eo_2.8",
    "Total_in_T1": "Ei1_1.8.1",
    "Total_in_T2": "Ei2_1.8.2",
    "Total_out_T1": "Eo1_2.8.1",
    "Total_out_T2": "Eo2_2.8.2",
    "Power_in": "Pi_1.7",
    "Power_out": "Po_2.7",
    "Volt_L1": "V1_32.7",
    "Volt_L2": "V2_52.7",
    "Volt_L3": "V3_72.7",
    "Amp_L1": "I1_31.7",
    "Amp_L2": "I2_51.7",
    "Amp_L3": "I3_71.7",
    # Standard Tasmota ENERGY keys
    "Total": "Ei_1.8",
    "Power": "Pi_1.7",
    "Voltage": "V1_32.7",
    "Current": "I1_31.7",
    # Short gPlug keys (as seen in real MQTT payloads)
    "Pi": "Pi_1.7",
    "Po": "Po_2.7",
    "V1": "V1_32.7",
    "V2": "V2_52.7",
    "V3": "V3_72.7",
    "I1": "I1_31.7",
    "I2": "I2_51.7",
    "I3": "I3_71.7",
    "Ei": "Ei_1.8",
    "Ei1": "Ei1_1.8.1",
    "Ei2": "Ei2_1.8.2",
    "Eo": "Eo_2.8",
    "Eo1": "Eo1_2.8.1",
    "Eo2": "Eo2_2.8.2",
}

# Keys to ignore (not useful as sensors)
SENSOR_SKIP_KEYS = {"SMid", "Time"}

# Known JSON prefixes used by gPlug Tasmota scripts
KNOWN_JSON_PREFIXES = ["ENERGY", "SML", "P1", "DSMR", "HDLC", "z"]
