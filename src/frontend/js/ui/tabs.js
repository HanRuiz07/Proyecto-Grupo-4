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
    try {
        console.log(`[tabs] setModo() llamado con: ${modo}`);

        ["manual","automatico","ml","conectar"].forEach(m => {
            const btn = document.getElementById(`btn-${m}`);
            if (btn) btn.classList.remove("active-mode");
            else console.warn(`[tabs] btn-${m} no encontrado`);
        });

        const btnActivo = document.getElementById(`btn-${modo}`);
        if (btnActivo) btnActivo.classList.add("active-mode");
        else console.warn(`[tabs] btn activo no encontrado: btn-${modo}`);

        ["manual","automatico","ml","conectar"].forEach(m => {
            const sec = document.getElementById(`modo-${m}`);
            if (sec) sec.classList.add("hidden");
            else console.warn(`[tabs] sección no encontrada: modo-${m}`);
        });

        const secAct = document.getElementById(`modo-${modo}`);
        if (secAct) {
            secAct.classList.remove("hidden");
            console.log(`[tabs] se mostró sección: modo-${modo}`);
        } else {
            console.warn(`[tabs] sección activa no encontrada: modo-${modo}`);
        }

        state.modo = modo;
        addLog(`Modo cambiado a: ${modo}`);

        // Llamadas a inicializadores (si existen)
        try { if (modo === "manual" && manualMode?.init) manualMode.init(); } catch (e) { console.error(e); }
        try { if (modo === "automatico" && autoMode?.init) autoMode.init(); } catch (e) { console.error(e); }
        try { if (modo === "ml" && mlMode?.init) mlMode.init(); } catch (e) { console.error(e); }
        try { if (modo === "conectar" && conectarMode?.init) conectarMode.init(); } catch (e) { console.error(e); }

        alert("green", `Modo ${modo} cargado`);
    } catch (err) {
        console.error('[tabs] Error en setModo:', err);
    }
}
