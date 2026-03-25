/**
 * gPlug Energy Card – Custom Lovelace Card
 * Auto-registered by the gPlug Energy integration.
 *
 * Shows real-time power flow, energy totals, and per-phase details.
 */

const CARD_VERSION = "1.0.0";

class GPlugEnergyCard extends HTMLElement {
  static get properties() {
    return { hass: {}, config: {} };
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  setConfig(config) {
    if (!config.entry_id && !config.entity_prefix) {
      throw new Error("Please define entry_id or entity_prefix");
    }
    this._config = {
      title: config.title || "gPlug Smart Meter",
      entity_prefix: config.entity_prefix || "",
      entry_id: config.entry_id || "",
      show_phases: config.show_phases !== false,
      show_export: config.show_export !== false,
      ...config,
    };
    this._render();
  }

  getCardSize() {
    return this._config?.show_phases ? 6 : 4;
  }

  static getConfigElement() {
    return document.createElement("gplug-energy-card-editor");
  }

  static getStubConfig() {
    return {
      title: "gPlug Smart Meter",
      entity_prefix: "sensor.gplugd_",
      show_phases: true,
      show_export: true,
    };
  }

  _getState(suffix) {
    if (!this._hass) return null;
    const prefix = this._config.entity_prefix;
    const entityId = prefix + suffix;
    const state = this._hass.states[entityId];
    if (!state) return null;
    return state;
  }

  _val(suffix, decimals = 1) {
    const s = this._getState(suffix);
    if (!s || isNaN(parseFloat(s.state))) return "—";
    return parseFloat(s.state).toFixed(decimals);
  }

  _unit(suffix) {
    const s = this._getState(suffix);
    return s?.attributes?.unit_of_measurement || "";
  }

  _render() {
    if (!this._hass || !this._config) return;

    const Pi = parseFloat(this._val("power_import", 3)) || 0;
    const Po = parseFloat(this._val("power_export", 3)) || 0;
    const netPower = Pi - Po;
    const isExporting = netPower < -0.001;
    const flowColor = isExporting ? "#1D9E75" : "#D85A30";
    const flowLabel = isExporting ? "Einspeisung" : "Bezug";
    const flowIcon = isExporting ? "mdi:transmission-tower-export" : "mdi:transmission-tower-import";
    const absNet = Math.abs(netPower).toFixed(3);

    const dark = document.documentElement.getAttribute("data-theme") === "dark"
      || window.matchMedia("(prefers-color-scheme: dark)").matches;

    const bg = dark ? "var(--card-background-color, #1c1c1e)" : "var(--card-background-color, #fff)";
    const text1 = "var(--primary-text-color, #333)";
    const text2 = "var(--secondary-text-color, #888)";
    const border = "var(--divider-color, rgba(0,0,0,0.12))";

    let phasesHTML = "";
    if (this._config.show_phases) {
      const phases = [1, 2, 3].map(n => {
        const v = this._val(`voltage_l${n}`, 1);
        const a = this._val(`current_l${n}`, 1);
        const pi = this._val(`power_import_l${n}`, 0);
        return `
          <div style="text-align:center;flex:1;padding:4px 0">
            <div style="font-size:11px;color:${text2};margin-bottom:2px">L${n}</div>
            <div style="font-size:14px;font-weight:500;color:${text1}">${v} V</div>
            <div style="font-size:12px;color:${text2}">${a} A · ${pi} W</div>
          </div>
        `;
      }).join(`<div style="width:1px;background:${border};margin:4px 0"></div>`);

      phasesHTML = `
        <div style="display:flex;padding:8px 16px 12px;border-top:1px solid ${border}">
          ${phases}
        </div>
      `;
    }

    let exportHTML = "";
    if (this._config.show_export) {
      exportHTML = `
        <div style="display:flex;justify-content:space-between;padding:4px 16px;font-size:12px;color:${text2}">
          <span>Einspeisung: ${this._val("energy_export_tariff_1", 3)} kWh</span>
          <span>Po: ${this._val("power_export", 3)} kW</span>
        </div>
      `;
    }

    this.innerHTML = `
      <ha-card>
        <div style="padding:16px 16px 8px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <div style="font-size:16px;font-weight:500;color:${text1}">${this._config.title}</div>
            <div style="font-size:11px;color:${text2}">gPlug Energy</div>
          </div>

          <!-- Power flow indicator -->
          <div style="text-align:center;padding:12px 0">
            <div style="font-size:12px;color:${text2};margin-bottom:4px">${flowLabel}</div>
            <div style="font-size:32px;font-weight:600;color:${flowColor};line-height:1.1">${absNet}</div>
            <div style="font-size:14px;color:${text2}">kW</div>
          </div>

          <!-- Energy totals -->
          <div style="display:flex;gap:8px;padding:8px 0 4px">
            <div style="flex:1;background:${dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)'};border-radius:8px;padding:10px 12px">
              <div style="font-size:11px;color:${text2}">Bezug HT (Ei1)</div>
              <div style="font-size:16px;font-weight:500;color:${text1}">${this._val("energy_import_tariff_1", 1)} <span style="font-size:12px;font-weight:400">kWh</span></div>
            </div>
            <div style="flex:1;background:${dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)'};border-radius:8px;padding:10px 12px">
              <div style="font-size:11px;color:${text2}">Bezug NT (Ei2)</div>
              <div style="font-size:16px;font-weight:500;color:${text1}">${this._val("energy_import_tariff_2", 1)} <span style="font-size:12px;font-weight:400">kWh</span></div>
            </div>
          </div>

          ${exportHTML}
        </div>

        ${phasesHTML}
      </ha-card>
    `;
  }
}

// Card editor for visual config
class GPlugEnergyCardEditor extends HTMLElement {
  set hass(hass) { this._hass = hass; }

  setConfig(config) {
    this._config = config;
    this._render();
  }

  _render() {
    this.innerHTML = `
      <div style="padding:16px">
        <ha-textfield
          label="Title"
          id="title"
          value="${this._config.title || "gPlug Smart Meter"}"
        ></ha-textfield>
        <ha-textfield
          label="Entity prefix (e.g. sensor.gplugd_)"
          id="entity_prefix"
          value="${this._config.entity_prefix || "sensor.gplugd_"}"
          style="margin-top:8px"
        ></ha-textfield>
        <ha-formfield label="Show phase details" style="margin-top:8px;display:block">
          <ha-switch id="show_phases" ${this._config.show_phases !== false ? "checked" : ""}></ha-switch>
        </ha-formfield>
        <ha-formfield label="Show export/feed-in" style="margin-top:4px;display:block">
          <ha-switch id="show_export" ${this._config.show_export !== false ? "checked" : ""}></ha-switch>
        </ha-formfield>
      </div>
    `;

    this.querySelector("#title").addEventListener("change", (e) => {
      this._config = { ...this._config, title: e.target.value };
      this._fire();
    });
    this.querySelector("#entity_prefix").addEventListener("change", (e) => {
      this._config = { ...this._config, entity_prefix: e.target.value };
      this._fire();
    });
    this.querySelector("#show_phases").addEventListener("change", (e) => {
      this._config = { ...this._config, show_phases: e.target.checked };
      this._fire();
    });
    this.querySelector("#show_export").addEventListener("change", (e) => {
      this._config = { ...this._config, show_export: e.target.checked };
      this._fire();
    });
  }

  _fire() {
    this.dispatchEvent(
      new CustomEvent("config-changed", { detail: { config: this._config } })
    );
  }
}

// Register card
customElements.define("gplug-energy-card", GPlugEnergyCard);
customElements.define("gplug-energy-card-editor", GPlugEnergyCardEditor);

// Register in Lovelace card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "gplug-energy-card",
  name: "gPlug Energy",
  description: "Real-time smart meter overview with power flow, tariffs, and phase details.",
  preview: true,
  documentationURL: "https://github.com/FX6W9WZK/ha-gplug-energy",
});

console.info(
  `%c gPlug Energy Card v${CARD_VERSION} `,
  "background:#1D9E75;color:#fff;font-weight:bold;padding:2px 6px;border-radius:4px"
);
