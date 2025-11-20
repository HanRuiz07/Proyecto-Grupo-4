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

            // Telemetría habitual (KPIs + gráficos)
            if (msg.tipo === "telemetria") {
                const data = msg.data || {};
                updateKpisFromTelemetry(data);
                updateChartsFromTelemetry(data);
                return;
            }

            // Mensaje de test para modo CONECTAR
            if (msg.tipo === "conectar_test") {
                const d = msg.data || {};
                // Actualiza el elemento de diagnóstico si existe
                const el = document.getElementById('conectar-diagnostico');
                if (el) el.textContent = d.msg || JSON.stringify(d);
                addLog(`WS conectar_test: ${d.msg || JSON.stringify(d)}`);
                return;
            }

            // Actualizaciones de estado del EMS
            if (msg.tipo === "ems_estado") {
                const d = msg.data || {};
                const estEl = document.getElementById('auto-estado');
                const ultAcc = document.getElementById('auto-ultima-accion');
                const motivo = document.getElementById('auto-motivo');
                const tsEl = document.getElementById('auto-ts');
                if (estEl) estEl.textContent = d.activo ? 'SI' : 'NO';
                if (ultAcc) ultAcc.textContent = d.ultima_accion ?? '--';
                if (motivo) motivo.textContent = d.ultimo_motivo ?? '--';
                if (tsEl && d.ultimo_timestamp) tsEl.textContent = new Date(d.ultimo_timestamp*1000).toLocaleString();
                addLog('WS ems_estado recibido');
                return;
            }

            // Resultados de predicción ML
            if (msg.tipo === "ml_pred") {
                const d = msg.data || {};
                const el = document.getElementById('ml-result');
                if (el) el.textContent = d.prediccion != null ? d.prediccion : JSON.stringify(d);
                addLog('WS ml_pred recibido');
                return;
            }

        } catch (e) {
            console.error("WS parse error", e);
            addLog("❌ Error parseando mensaje WS");
        }
    };
}
