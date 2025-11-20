// ======================================================================
// API CLIENT — WRAPPER SEGURO PARA LLAMADAS REST
// ======================================================================

import { state } from "./state.js";
import { addLog } from "./logger.js";
import { alert } from "./alerts.js";

export async function safeFetch(path, options = {}) {
    const url = `${state.config.api_base}${path}`;

    const finalOpts = {
        headers: { "Content-Type": "application/json" },
        ...options
    };

    try {
        const t0 = performance.now();
        const resp = await fetch(url, finalOpts);
        const dt = (performance.now() - t0).toFixed(1);

        if (!resp.ok) {
            addLog(`❌ API ${path} → ${resp.status}`);
            alert("red", `Error API ${path}: ${resp.status}`);
            return null;
        }

        addLog(`✔ API ${path} (${dt} ms)`);
        return await resp.json();
    } catch (e) {
        addLog(`❌ API ${path} falló: ${e}`);
        alert("red", `No se pudo contactar a ${path}`);
        return null;
    }
}
