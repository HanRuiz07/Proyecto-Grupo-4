// ======================================================================
// KPIS — ACTUALIZACIÓN VISUAL A PARTIR DE TELEMETRÍA
// ======================================================================

import { state } from "../core/state.js";
import { setText } from "../core/utils.js";

export function updateKpisFromTelemetry(data) {
    const v_pv = data.v_pv ?? 0;
    const i_pv = data.i_pv ?? 0;
    const v_bat = data.v_bat ?? 0;
    const i_bat = data.i_bat ?? 0;
    const soc = data.soc ?? 0;
    const temp_bat = data.temp_bat ?? 0;

    const p_pv = v_pv * i_pv;
    const p_carga = v_bat * i_bat;

    // Manual
    setText("manual-pv-potencia", `${p_pv.toFixed(2)} W`);
    setText("potencia-carga", `${p_carga.toFixed(2)} W`);
    setText("manual-bateria-soc", `${soc.toFixed(1)} %`);
    setText("manual-bateria-v", `${v_bat.toFixed(2)} V`);
    setText("manual-bateria-i", `${i_bat.toFixed(2)} A`);
    setText("manual-bateria-temp", `${temp_bat.toFixed(1)} °C`);

    setText("manual-pv-v", v_pv.toFixed(2));
    setText("manual-pv-i", i_pv.toFixed(2));
    setText("manual-pv-p", p_pv.toFixed(2));

    setText("manual-bat-v", v_bat.toFixed(2));
    setText("manual-bat-i", i_bat.toFixed(2));
    setText("manual-bat-p", p_carga.toFixed(2));

    // Automático (valores básicos)
    setText("auto-pv", `${p_pv.toFixed(2)} W`);
    setText("auto-load", `${p_carga.toFixed(2)} W`);
    setText("auto-soc", `${soc.toFixed(1)} %`);

    // Conectar: estado mínimo
    setText("mqtt-last", new Date().toLocaleTimeString());

    state.kpis.pv = p_pv;
    state.kpis.soc = soc;
    state.kpis.vbus = v_bat;
    state.kpis.corriente = i_bat;
    state.kpis.temp = temp_bat;
}
