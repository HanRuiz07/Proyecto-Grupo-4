// ======================================================================
// MODO MANUAL — LÓGICA ASOCIADA
// ======================================================================

import { addLog } from "../core/logger.js";
import { safeFetch } from "../core/api.js";
import { setText } from "../core/utils.js";

export const manualMode = {
    init() {
        addLog("Inicializando modo MANUAL…");
        // Podrías llamar a /api/estado aquí si quieres precargar algo
    }
};

// ----- ACCIONES QUE USAN LOS BOTONES DEL HTML -----

export async function cmdSistema(accion) {
    addLog(`Comando sistema: ${accion}`);
    setText("last-cmd-sys", accion.toUpperCase());

    await safeFetch("/manual/comando", {
        method: "POST",
        body: JSON.stringify({ comando: accion })
    });
}

export function actualizarSliderPotencia(valor) {
    const span = document.getElementById("slider-potencia-value");
    if (span) span.textContent = `${valor} %`;
}

export const umbrales = {
    vbat_min: 11.5,
    ibat_max: 2.0,
    tbat_max: 45
};

export function actualizarUmbral(tipo, valor) {
    const v = parseFloat(valor);
    if (tipo === "vbat") umbrales.vbat_min = v;
    if (tipo === "ibat") umbrales.ibat_max = v;
    if (tipo === "tbat") umbrales.tbat_max = v;
}

export async function aplicarUmbrales() {
    addLog(`Aplicando umbrales: ${JSON.stringify(umbrales)}`);
    document.getElementById("estado-umbrales-manual").textContent =
        "Umbrales actualizados localmente (envío a backend opcional).";

    await safeFetch("/manual/umbrales", {
        method: "POST",
        body: JSON.stringify(umbrales)
    });
}
