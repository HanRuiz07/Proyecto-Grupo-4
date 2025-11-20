// ======================================================================
// WEBSOCKET — TELEMETRÍA EN TIEMPO REAL
// ======================================================================

import { state } from "./state.js";
import { addLog } from "./logger.js";
import { alert } from "./alerts.js";
import { updateChartsFromTelemetry } from "../ui/charts.js";
import { updateKpisFromTelemetry } from "../ui/kpis.js";

export function initWebSocket() {
    if (state.ws) {
        try { state.ws.close(); } catch {}
    }

    const ws = new WebSocket(state.config.ws_url);
    state.ws = ws;

    addLog("Conectando WebSocket…");

    ws.onopen = () => {
        addLog("✔ WebSocket conectado");
        state.connected.ws = true;
        state.wsRetryCount = 0;
    };

    ws.onclose = () => {
        addLog("⚠ WebSocket cerrado");
        state.connected.ws = false;

        if (state.wsRetryCount < 5) {
            const delay = 2000 * (state.wsRetryCount + 1);
            state.wsRetryCount += 1;
            addLog(`Reintentando WebSocket en ${delay / 1000}s…`);
            setTimeout(initWebSocket, delay);
        } else {
            alert("yellow", "WebSocket desconectado, sin más reintentos.");
        }
    };

    ws.onerror = (ev) => {
        console.error("WS error:", ev);
        addLog("❌ Error en WebSocket");
    };

    ws.onmessage = (ev) => {
        try {
            const msg = JSON.parse(ev.data);

            if (msg.tipo === "telemetria") {
                const data = msg.data || {};
                updateKpisFromTelemetry(data);
                updateChartsFromTelemetry(data);
            }

        } catch (e) {
            console.error("WS parse error", e);
            addLog("❌ Error parseando mensaje WS");
        }
    };
}
