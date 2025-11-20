// ======================================================================
// MODO AUTOMÁTICO — EMS + ML
// ======================================================================

import { addLog } from "../core/logger.js";
import { safeFetch } from "../core/api.js";
import { setText } from "../core/utils.js";

export const autoMode = {
    async init() {
        addLog("Inicializando modo AUTOMÁTICO…");

        // Obtener estado simplificado (compatibilidad) y estado interno del EMS
        try {
            const info = await safeFetch("/ems/estado");
            if (info) {
                setText("auto-estado", info.estado ?? "--");
                setText("auto-flujo", info.flujo ?? "--");
            }
        } catch (e) {
            addLog("⚠ /ems/estado no disponible");
        }

        try {
            const estado = await safeFetch("/modo/automatico/estado");
            if (estado && estado.ultimo_timestamp) {
                setText("auto-ultima-accion", estado.ultima_accion ?? "--");
                setText("auto-motivo", estado.ultimo_motivo ?? "--");
                setText("auto-ts", estado.ultimo_timestamp ? new Date(estado.ultimo_timestamp*1000).toLocaleString() : "--");
                setText("auto-estado", estado.activo ? "SI" : "NO");
            }
        } catch (e) {
            addLog("⚠ /modo/automatico/estado no disponible");
        }

        // Enlazar botones
        try {
            const onBtn = document.getElementById('btn-auto-on');
            const offBtn = document.getElementById('btn-auto-off');
            const forzarBtn = document.getElementById('btn-auto-forzar');

            if (onBtn) onBtn.addEventListener('click', async () => {
                addLog('Activando modo automático...');
                const r = await safeFetch('/modo/automatico/on', { method: 'POST' });
                if (r) addLog('Respuesta: ' + (r.msg || JSON.stringify(r)));
            });

            if (offBtn) offBtn.addEventListener('click', async () => {
                addLog('Desactivando modo automático...');
                const r = await safeFetch('/modo/automatico/off', { method: 'POST' });
                if (r) addLog('Respuesta: ' + (r.msg || JSON.stringify(r)));
            });

            if (forzarBtn) forzarBtn.addEventListener('click', async () => {
                addLog('Forzando decisión EMS...');
                const r = await safeFetch('/ems/forzar', { method: 'POST' });
                if (r) addLog('Respuesta: ' + (r.msg || JSON.stringify(r)));
            });
        } catch (e) {
            console.warn('Error enlazando botones modo automático', e);
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
