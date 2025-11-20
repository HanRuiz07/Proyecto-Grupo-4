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
