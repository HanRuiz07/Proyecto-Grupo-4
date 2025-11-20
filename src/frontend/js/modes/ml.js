// ======================================================================
// MODO ML — INFORMACIÓN DEL MODELO Y MÉTRICAS
// ======================================================================

import { addLog } from "../core/logger.js";
import { safeFetch } from "../core/api.js";
import { setText } from "../core/utils.js";

export const mlMode = {
    async init() {
        addLog("Inicializando modo ML…");
        const info = await safeFetch("/ml/info");
        if (info) {
            setText("ml-modelo", info.nombre ?? "--");
            setText("ml-mape", info.mape != null ? `${info.mape.toFixed(2)} %` : "-- %");
            setText("ml-train", info.ultimo_entrenamiento ?? "--");
            setText("ml-arquitectura", info.arquitectura ?? "--");
            setText("ml-variables", Array.isArray(info.variables) ? info.variables.join(", ") : "--");
        }
    }
};

export async function predecir() {
    try {
        const raw = document.getElementById('ml-input-corriente')?.value || '';
        const arr = raw.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
        const r = await safeFetch('/ml/predict', { method: 'POST', body: JSON.stringify({ corriente: arr }) });
        if (r && r.status === 'ok') {
            document.getElementById('ml-result').textContent = JSON.stringify(r.prediccion);
        } else if (r) {
            document.getElementById('ml-result').textContent = r.mensaje || JSON.stringify(r);
        }
    } catch (e) {
        console.error('Error predict', e);
        document.getElementById('ml-result').textContent = 'Error';
    }
}
