// ======================================================================
// LOGGER GLOBAL — GUARDA Y MUESTRA LOGS EN EL PANEL
// ======================================================================

import { state } from "./state.js";

export function addLog(msg) {
    const ts = new Date().toLocaleTimeString();
    const entry = `[${ts}] ${msg}`;

    state.logs.push(entry);
    if (state.logs.length > 300) {
        state.logs.shift();
    }

    console.log(entry);

    const cont = document.getElementById("logs-contenido");
    if (!cont) return;

    const div = document.createElement("div");
    div.classList.add("log-line");
    div.textContent = entry;
    cont.appendChild(div);

    cont.scrollTop = cont.scrollHeight;
}
