// ======================================================================
// TABS — GESTOR DE MODOS
// ======================================================================

import { state } from "../core/state.js";
import { addLog } from "../core/logger.js";
import { alert } from "../core/alerts.js";

import { manualMode } from "../modes/manual.js";
import { autoMode } from "../modes/automatico.js";
import { mlMode } from "../modes/ml.js";
import { conectarMode } from "../modes/conectar.js";

export async function setModo(modo) {
    ["manual","automatico","ml","conectar"].forEach(m => {
        const btn = document.getElementById(`btn-${m}`);
        btn?.classList.remove("active-mode");
    });

    const btnActivo = document.getElementById(`btn-${modo}`);
    btnActivo?.classList.add("active-mode");

    ["manual","automatico","ml","conectar"].forEach(m => {
        document.getElementById(`modo-${m}`)?.classList.add("hidden");
    });

    document.getElementById(`modo-${modo}`)?.classList.remove("hidden");

    state.modo = modo;
    addLog(`Modo cambiado a: ${modo}`);

    if (modo === "manual") manualMode.init();
    if (modo === "automatico") autoMode.init();
    if (modo === "ml") mlMode.init();
    if (modo === "conectar") conectarMode.init();

    alert("green", `Modo ${modo} cargado`);
}
