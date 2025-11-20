// ======================================================================
// MODO AUTOMÁTICO — EMS + ML
// ======================================================================

import { addLog } from "../core/logger.js";
import { safeFetch } from "../core/api.js";
import { setText } from "../core/utils.js";

export const autoMode = {
    async init() {
        addLog("Inicializando modo AUTOMÁTICO…");

        // TEMPORAL: evita que el dashboard se rompa por el 404
        try {
            const info = await safeFetch("/ems/estado");

            if (info) {
                setText("auto-estado", info.estado ?? "--");
                setText("auto-flujo", info.flujo ?? "--");
            }
        } catch (e) {
            addLog("⚠ /ems/estado no está implementado todavía");
        }
    }
};

export async function forzarAutomatico() {
    addLog("Forzando decisión del EMS…");

    try {
        await safeFetch("/ems/forzar", { method: "POST" });
    } catch {
        addLog("⚠ /ems/forzar no disponible");
    }
}
