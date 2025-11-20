// ======================================================================
// MODO CONECTAR — PRUEBAS DE INFRAESTRUCTURA
// ======================================================================

import { addLog } from "../core/logger.js";
import { safeFetch } from "../core/api.js";
import { setText } from "../core/utils.js";

export const conectarMode = {
    init() {
        addLog("Inicializando modo CONECTAR…");
    }
};

export async function probarConexion() {
    addLog("Probar conexión general Raspberry/VM…");
    const r = await safeFetch("/conectar/test-backend");
    if (r) {
        setText("conectar-diagnostico", r.detalle ?? "Conexión OK");
    }
}

export async function mqttLeer() {
    addLog("Probar lectura MQTT…");
    const r = await safeFetch("/conectar/test-mqtt");
    if (r) {
        setText("mqtt-test-resultado", r.detalle ?? "MQTT OK");
    }
}

export async function mqttComando() {
    addLog("Enviando comando MQTT de prueba…");
    await safeFetch("/conectar/mqtt/comando", { method: "POST" });
}

export async function mqttRelay(modo) {
    addLog(`MQTT Relay → ${modo}`);
    await safeFetch("/conectar/mqtt/relay", {
        method: "POST",
        body: JSON.stringify({ modo })
    });
}

export async function simSend() {
    addLog("Enviando datos de prueba a Simulink…");
    await safeFetch("/simulink/enviar", { method: "POST" });
}

export async function simCargar() {
    addLog("Cargar escenario en Simulink…");
    await safeFetch("/simulink/cargar", { method: "POST" });
}

export async function probarWebSocket() {
    addLog("Probar flujo WS desde backend…");
    await safeFetch("/conectar/test-ws", { method: "POST" });
}

export async function probarDB() {
    addLog("Probar escritura/lectura DB…");
    const r = await safeFetch("/conectar/test-db", { method: "POST" });
    if (r) {
        setText("conect-db-estado", r.estado ?? "--");
        setText("conect-db-last-write", r.last_write ?? "--");
        setText("conect-db-last-read", r.last_read ?? "--");
        setText("conect-db-muestras", r.muestras ?? "--");
    }
}
