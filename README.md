# gPlug Energy – Home Assistant Integration (HACS)

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![Validate](https://github.com/FX6W9WZK/ha-gplug-energy/actions/workflows/validate.yml/badge.svg)](https://github.com/FX6W9WZK/ha-gplug-energy/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Vollwertige Home Assistant Integration für [gPlug](https://gplug.ch/) Smart-Meter-Sensoren (gPlugD, gPlugD-E, gPlugE) mit direkter Anbindung an das Energy Dashboard.**

---

## Features

- **Auto-Discovery**: Sensoren werden automatisch aus den MQTT-Payloads erkannt – kein manuelles YAML nötig
- **Energy Dashboard Ready**: Alle Energie-Sensoren haben korrekte `device_class`, `state_class` und `unit_of_measurement` für das HA Energy Dashboard
- **Dual-Verbindung**: MQTT (empfohlen) oder HTTP-Polling
- **Schweizer Smart Meter**: Optimiert für P1-DSMR-Schnittstelle (Elster AS3000, Ensor eRS801, L&G E360, Sagemcom XT211, ISKRA AM550, NES Gen-5, M+C Flexy)
- **Mehrere Script-Varianten**: Unterstützt DSMR ASCII, HDLC/DLMS und verschiedene JSON-Formate
- **3-Phasen-Monitoring**: Spannung, Strom und Leistung pro Phase
- **Tarif-Unterstützung**: Doppeltarif Hoch-/Niedertarif (HT/NT)
- **Config Flow**: Komfortable Einrichtung über die HA-Oberfläche
- **Mehrsprachig**: DE / FR / EN

---

## Unterstützte Sensoren

| Sensor | OBIS-Code | Einheit | Energy Dashboard |
|--------|-----------|---------|:----------------:|
| Energiebezug Gesamt | 1.8.0 | kWh | ✅ Grid Consumption |
| Energiebezug Tarif 1 (HT) | 1.8.1 | kWh | ✅ |
| Energiebezug Tarif 2 (NT) | 1.8.2 | kWh | ✅ |
| Energieeinspeisung Gesamt | 2.8.0 | kWh | ✅ Return to Grid |
| Energieeinspeisung Tarif 1 | 2.8.1 | kWh | ✅ |
| Energieeinspeisung Tarif 2 | 2.8.2 | kWh | ✅ |
| Bezugsleistung | 1.7.0 | kW | ⚡ Momentanwert |
| Einspeiseleistung | 2.7.0 | kW | ⚡ Momentanwert |
| Spannung L1 / L2 / L3 | 32.7 / 52.7 / 72.7 | V | 📊 |
| Strom L1 / L2 / L3 | 31.7 / 51.7 / 71.7 | A | 📊 |

---

## Installation

### Über HACS (empfohlen)

1. Öffne **HACS** in Home Assistant
2. Klicke auf **⋮** (oben rechts) → **Benutzerdefinierte Repositories**
3. URL eingeben: `https://github.com/FX6W9WZK/ha-gplug-energy`
4. Kategorie: **Integration**
5. **gPlug Energy** suchen und installieren
6. Home Assistant neu starten

### Manuell

1. Kopiere den Ordner `custom_components/gplug_energy/` nach `<config>/custom_components/`
2. Home Assistant neu starten

---

## Konfiguration

### Voraussetzung

Dein gPlugD muss per MQTT mit einem Broker verbunden sein (z.B. Mosquitto). Die Einrichtung erfolgt über die gPlug Web-UI unter **Einstellungen → MQTT**.

### Schritt 1: Integration hinzufügen

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Suche nach **gPlug Energy**
3. Wähle **MQTT** (empfohlen) oder **HTTP**

### Schritt 2: MQTT-Topic konfigurieren

Gib das Sensor-Topic deines gPlug ein. Das Standard-Format ist:

```
tele/<dein-gplug-topic>/SENSOR
```

Das Topic findest du in der gPlug Web-UI unter **Information** oder im MQTT Explorer.

### Schritt 3: Sensoren erscheinen automatisch

Sobald der gPlug Daten sendet, werden die Sensoren automatisch erkannt und in Home Assistant angelegt. Das dauert normalerweise nur wenige Sekunden.

---

## Energy Dashboard einrichten

Nach der Installation sind die Energie-Sensoren sofort für das Energy Dashboard verfügbar. So gehst du Schritt für Schritt vor:

### Schritt 1: Netzanschluss konfigurieren

Navigiere zu **Einstellungen → Dashboards → Energie → Stromnetz → Netzanschluss konfigurieren**.

#### Aus dem Netz bezogene Energie (Verbrauch)

Wähle hier den **kumulativen Energiezähler** (kWh, `total_increasing`). Bei den meisten Schweizer Smart Metern wird der Bezug in **Tarif 1** (Hochtarif) gezählt:

| Sensor-Entity | Beschreibung | Wann verwenden |
|---------------|-------------|----------------|
| `sensor.gplugd_energy_import_tariff_1` | Bezug Tarif 1 (HT) | **Standard** – bei den meisten VNB der Hauptzähler |
| `sensor.gplugd_energy_import_tariff_2` | Bezug Tarif 2 (NT) | Nur bei Doppeltarif (HT/NT) als zweiten Eintrag hinzufügen |
| `sensor.gplugd_energy_import_total` | Bezug Gesamt | Falls dein SM einen Gesamtzähler liefert (Ei > 0) |

**Tipp:** Prüfe unter **Entwicklerwerkzeuge → Zustände**, welcher Sensor tatsächlich Werte > 0 hat. Bei deinem Smart Meter ist typischerweise `Ei1` (Tarif 1) der Hauptzähler.

#### In das Netz eingespeiste Energie (PV-Einspeisung)

Wenn du eine PV-Anlage hast:

| Sensor-Entity | Beschreibung |
|---------------|-------------|
| `sensor.gplugd_energy_export_tariff_1` | Einspeisung Tarif 1 |
| `sensor.gplugd_energy_export_total` | Einspeisung Gesamt |

#### Kostenerfassung (optional)

- **Fester Preis**: Trage deinen Stromtarif in CHF/kWh ein (z.B. 0.27)
- **Entität mit aktuellem Preis**: Falls du einen dynamischen Tarif hast

#### Art der Leistungsmessung

Wähle hier **keinen** Leistungssensor. Das Energy Dashboard berechnet den Verbrauch aus den kumulativen kWh-Zählern automatisch. Die Leistungssensoren (`Pi`, `Po`) sind für Live-Dashboards, nicht fürs Energy Dashboard.

### Schritt 2: Prüfen

Nach dem Speichern dauert es ca. 1-2 Stunden, bis das Energy Dashboard die ersten Daten anzeigt. Prüfe unter **Entwicklerwerkzeuge → Statistiken**, ob die Sensoren korrekte Langzeitstatistiken aufbauen.

### Übersicht: Welcher Sensor wofür?

```
Energy Dashboard (kWh, kumulativ)
├── Netzbezug:      sensor.gplugd_energy_import_tariff_1  (Ei1)
├── Netzeinspeisung: sensor.gplugd_energy_export_tariff_1  (Eo1)
└── ggf. Tarif 2:   sensor.gplugd_energy_import_tariff_2  (Ei2)

Live-Dashboard / Lovelace (kW/W, Momentanwerte)
├── Bezugsleistung:  sensor.gplugd_power_import            (Pi)
├── Einspeiseleist.: sensor.gplugd_power_export            (Po)
├── Leistung L1-L3:  sensor.gplugd_power_import_l1/l2/l3  (P1i/P2i/P3i)
├── Spannung L1-L3:  sensor.gplugd_voltage_l1/l2/l3       (V1/V2/V3)
└── Strom L1-L3:     sensor.gplugd_current_l1/l2/l3       (I1/I2/I3)
```

---

## Utility Meter (optional)

Für tägliche/wöchentliche/monatliche Auswertungen kann der `utility_meter` Helper ergänzt werden. Füge dies in `configuration.yaml` hinzu:

```yaml
utility_meter:
  energy_import_daily:
    source: sensor.gplugd_energy_import_total
    cycle: daily
  energy_import_monthly:
    source: sensor.gplugd_energy_import_total
    cycle: monthly
  energy_import_yearly:
    source: sensor.gplugd_energy_import_total
    cycle: yearly
  energy_export_daily:
    source: sensor.gplugd_energy_export_total
    cycle: daily
  energy_export_monthly:
    source: sensor.gplugd_energy_export_total
    cycle: monthly
```

---

## Beispiel-Dashboard (Lovelace)

```yaml
type: entities
title: gPlug Smart Meter
entities:
  - entity: sensor.gplugd_energy_import_total
    name: Bezug Gesamt
  - entity: sensor.gplugd_energy_export_total
    name: Einspeisung Gesamt
  - type: divider
  - entity: sensor.gplugd_power_import
    name: Aktuelle Leistung (Bezug)
  - entity: sensor.gplugd_power_export
    name: Aktuelle Leistung (Einspeisung)
  - type: divider
  - entity: sensor.gplugd_voltage_l1
  - entity: sensor.gplugd_voltage_l2
  - entity: sensor.gplugd_voltage_l3
  - entity: sensor.gplugd_current_l1
  - entity: sensor.gplugd_current_l2
  - entity: sensor.gplugd_current_l3
```

---

## Kompatible Tasmota Scripts

Die Integration erkennt automatisch verschiedene JSON-Formate:

**P1-DSMR (ASCII)** – Standard-Script:
```json
{"Time":"...","ENERGY":{"Ei_1.8":1234.56,"Pi_1.7":0.450,...}}
```

**HDLC/DLMS** – Für ISKRA, M+C etc.:
```json
{"Time":"...","ENERGY":{"Total_in":1234.56,"Power_in":0.450,...}}
```

**Benutzerdefiniert** – Unbekannte Keys werden automatisch als generische Sensoren angelegt.

---

## Troubleshooting

### Sensoren erscheinen nicht

1. Prüfe mit **MQTT Explorer**, ob dein gPlug auf dem konfigurierten Topic sendet
2. Stelle sicher, dass die **Tasmota Integration** in HA _nicht_ parallel dieselben Sensoren verwaltet (Duplikate vermeiden)
3. Überprüfe das Topic-Format: `tele/<topic>/SENSOR`

### Sensoren nicht im Energy Dashboard sichtbar

Die Sensoren müssen folgende Attribute haben:
- `device_class: energy`
- `state_class: total_increasing`
- `unit_of_measurement: kWh`

Überprüfe dies unter **Entwicklerwerkzeuge → Zustände**.

### MQTT-Verbindung prüfen

In der gPlug Tasmota-Konsole:
```
Status 6
```
zeigt den MQTT-Verbindungsstatus an.

---

## Architektur

```
gPlugD (ESP32-C3 / Tasmota)
    │
    │  P1-DSMR / HDLC/DLMS
    │
    ▼
Smart Meter (Elster, ISKRA, Sagemcom, ...)
    │
    │  MQTT (tele/<topic>/SENSOR)
    │
    ▼
Mosquitto Broker
    │
    │  MQTT Subscribe
    │
    ▼
gPlug Energy Integration
    │
    ├── Auto-Discovery der Sensoren
    ├── device_class / state_class Zuweisung
    └── Energy Dashboard Ready
```

---

## Mitwirken

Pull Requests und Issues sind willkommen! Bitte beachte:

- Neue Sensor-Typen in `const.py` → `SENSOR_TYPES_ENERGY` hinzufügen
- Neue JSON-Key-Aliase in `const.py` → `SENSOR_KEY_ALIASES` ergänzen
- Übersetzungen in `translations/` pflegen

---

## Lizenz

MIT License – siehe [LICENSE](LICENSE)

---

## Links

- [gPlug.ch – Produkte](https://gplug.ch/produkte/)
- [gPlug Installationsanleitung](https://gplug.ch/installationsanleitung/gplugd/)
- [Tasmota Smart Meter Interface](https://tasmota.github.io/docs/Smart-Meter-Interface/)
- [Tasmota MQTT Dokumentation](https://tasmota.github.io/docs/MQTT/)
- [Home Assistant Energy Dashboard FAQ](https://www.home-assistant.io/docs/energy/faq/)
