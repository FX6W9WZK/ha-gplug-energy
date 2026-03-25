# Changelog

Alle relevanten Änderungen an der gPlug Energy Integration werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/)
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.0.4] – 2026-03-25

### Behoben
- **Keine Duplikate im Energy Dashboard**: Auto-Konfiguration prüft jetzt ob bereits gPlug-Sensoren im Energy Dashboard vorhanden sind und überspringt in diesem Fall
- Verhindert `duplicate unique ID` Fehler bei HA-Neustart wenn Sensoren bereits manuell oder durch vorherigen Lauf konfiguriert wurden

## [1.0.3] – 2026-03-25

### Behoben
- **Lovelace-Karte Cache-Busting**: Resource-URL enthält jetzt Versionsparameter (`?v=1.0.3`), damit Browser bei Updates die neue Version laden
- Bei Version-Update wird die bestehende Resource-URL automatisch aktualisiert (kein Duplikat)

## [1.0.2] – 2026-03-25

### Behoben
- **Lovelace-Karte wird jetzt zuverlässig registriert**: Schreibt direkt in `.storage/lovelace_resources` statt über die instabile interne Lovelace-API
- Karte erscheint nach HA-Neustart automatisch unter Einstellungen → Dashboards → Ressourcen
- Fallback mit manueller Anleitung falls Schreibzugriff fehlschlägt

## [1.0.1] – 2026-03-25

### Behoben
- **HA 2025.x+ Kompatibilität**: `async_register_static_paths` statt `register_static_path` (mit Fallback)
- **Manifest**: `http`, `lovelace`, `energy` in `after_dependencies`, korrekte Key-Sortierung
- **OptionsFlow**: Kompatibel mit neuerer HA `config_entry` Property
- **Device Registry**: Keine ungültige `configuration_url` bei reiner MQTT-Verbindung
- **Sensor-Erstellung**: `entity_id`-Check vor `async_write_ha_state()` verhindert `NoEntitySpecifiedError`
- **gPlugD Payload**: `z`-Prefix und Kurzkeys (`Pi`, `V1`, `Ei1` etc.) korrekt gemappt
- **SMid**: Meter-Seriennummer wird übersprungen (kein Sensor)

### Hinzugefügt
- Per-Phase Leistungssensoren: `P1i`/`P2i`/`P3i` und `P1o`/`P2o`/`P3o` (W)
- Offizielle gPlug Brand Assets (Logo, Icon)

## [1.0.0] – 2026-03-25

### Hinzugefügt
- **Auto-Discovery** aller Sensoren via MQTT (Prefixes: `z`, `ENERGY`, `SML`, `P1`, `HDLC`)
- **Energy Dashboard ready** – Sensoren mit `device_class: energy` / `state_class: total_increasing`
- **Auto-Konfiguration** des Energy Dashboards 30s nach HA-Start
- **Lovelace-Karte** (`gplug-energy-card`) mit Auto-Registrierung und visuellem Editor
- **Doppeltarif (HT/NT)** – optimiert für Schweizer VNB (z.B. EWZ Zürich)
- **3-Phasen-Monitoring** – Spannung, Strom, Leistung pro Phase (L1/L2/L3)
- **Config Flow** mit MQTT (empfohlen) und HTTP-Polling
- **Übersetzungen**: DE / FR / EN
- **Diagnostics** Support
- CI/CD: HACS + Hassfest + Ruff Validation
- Beispiel-Configs für `utility_meter`, Templates und Automations

### Kompatible Hardware
- gPlugD, gPlugD-E, gPlugE
- Smart Meter: Elster AS3000, Ensor eRS801, L&G E360, Sagemcom XT211, ISKRA AM550, NES Gen-5, M+C Flexy

[1.0.4]: https://github.com/FX6W9WZK/ha-gplug-energy/releases/tag/v1.0.4
[1.0.3]: https://github.com/FX6W9WZK/ha-gplug-energy/releases/tag/v1.0.3
[1.0.2]: https://github.com/FX6W9WZK/ha-gplug-energy/releases/tag/v1.0.2
[1.0.1]: https://github.com/FX6W9WZK/ha-gplug-energy/releases/tag/v1.0.1
[1.0.0]: https://github.com/FX6W9WZK/ha-gplug-energy/releases/tag/v1.0.0
