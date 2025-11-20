// ======================================================================
// HTTP WRAPPER — GET / POST industriales
// ======================================================================

import { state } from "./state.js";
import { addLog } from "./logger.js";
import { showAlert } from "./alerts.js";

export async function apiGet(path) {
    const url = `${state.config.api_base}${path}`;
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        addLog(`GET ${path} OK`);
        return data;
    } catch (e) {
        addLog(`❌ GET ${path} — Error: ${e}`);
        showAlert("red", `GET error: ${path}`);
        return null;
    }
}

export async function apiPost(path, body = {}) {
    const url = `${state.config.api_base}${path}`;
    try {
        const res = await fetch(url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(body)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        addLog(`POST ${path} OK`);
        return data;
    } catch (e) {
        addLog(`❌ POST ${path} — Error: ${e}`);
        showAlert("red", `POST error: ${path}`);
        return null;
    }
}
