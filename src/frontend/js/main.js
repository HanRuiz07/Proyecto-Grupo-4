// ======================================================================
// MAIN — INICIALIZACIÓN GLOBAL DEL FRONTEND
// ======================================================================

import { addLog } from "./core/logger.js";
import { initCharts } from "./ui/charts.js";
import { setModo as setModoInterno } from "./ui/tabs.js";
import { initSliders } from "./ui/sliders.js";
import { initWebSocket } from "./core/websocket.js";

// Modos / acciones
import {
    manualMode,
    cmdSistema,
    actualizarSliderPotencia,
    actualizarUmbral,
    aplicarUmbrales
} from "./modes/manual.js";

import {
    autoMode,
    forzarAutomatico
} from "./modes/automatico.js";

import {
    mlMode
} from "./modes/ml.js";

import {
    conectarMode,
    probarConexion,
    mqttLeer,
    mqttComando,
    mqttRelay,
    simSend,
    simCargar,
    probarWebSocket,
    probarDB
} from "./modes/conectar.js";

function toggleLogs() {
    const panel = document.getElementById("panel-logs");
    if (!panel) return;
    panel.classList.toggle("logs-hidden");
}

// ----------------------------------------------------------------------
// INICIALIZACIÓN AL CARGAR
// ----------------------------------------------------------------------

window.addEventListener("load", () => {
    addLog("Iniciando dashboard…");

    initCharts();
    initSliders();
    initWebSocket();

    // Modo por defecto
    setModoInterno("manual");

    addLog("Dashboard iniciado");
    
    // ----------------------------
    // Enlazar botones del HTML (si existen)
    // ----------------------------
    try {
        // Modo buttons
        ["manual","automatico","ml","conectar"].forEach(m => {
            const el = document.getElementById(`btn-${m}`);
            if (el) el.addEventListener("click", () => setModoInterno(m));
        });

        // Sistema (on/off/emerg)
        const sysOn = document.getElementById("btn-sys-on");
        const sysOff = document.getElementById("btn-sys-off");
        const sysEmerg = document.getElementById("btn-sys-emerg");
        if (sysOn) sysOn.addEventListener("click", () => cmdSistema("on"));
        if (sysOff) sysOff.addEventListener("click", () => cmdSistema("off"));
        if (sysEmerg) sysEmerg.addEventListener("click", () => cmdSistema("reset"));

        // Aplicar umbrales
        const btnUmbrales = document.getElementById("btn-aplicar-umbrales");
        if (btnUmbrales) btnUmbrales.addEventListener("click", () => aplicarUmbrales());

        // Toggle logs
        const btnLogs = document.getElementById("btn-logs");
        if (btnLogs) btnLogs.addEventListener("click", () => toggleLogs());
    } catch (err) {
        console.warn("Error al enlazar botones del UI:", err);
    }
});

// ----------------------------------------------------------------------
// EXPONER FUNCIONES GLOBALES PARA EL HTML (onclick="...")
// ----------------------------------------------------------------------

// Modos
window.setModo = (modo) => {
    setModoInterno(modo);
};

// ----------------------------------------------------------------------
// ASIGNAR EVENTOS A LOS BOTONES DEL NAVBAR
// ----------------------------------------------------------------------

function initNavbar() {
    const botones = [
        { id: "btn-manual", modo: "manual" },
        { id: "btn-automatico", modo: "automatico" },
        { id: "btn-ml", modo: "ml" },
        { id: "btn-conectar", modo: "conectar" }
    ];

    botones.forEach(btn => {
        const el = document.getElementById(btn.id);
        if (el) {
            el.addEventListener("click", () => {
                addLog(`Click → ${btn.modo}`);
                setModoInterno(btn.modo);
            });
        } else {
            console.warn(`⚠️ Botón no encontrado: ${btn.id}`);
        }
    });
}


// Logs
window.toggleLogs = toggleLogs;

// Manual
window.cmdSistema = cmdSistema;
window.actualizarSliderPotencia = actualizarSliderPotencia;
window.actualizarUmbral = actualizarUmbral;
window.aplicarUmbrales = aplicarUmbrales;

// Automático
window.forzarAutomatico = forzarAutomatico;

// Conectar
window.probarConexion = probarConexion;
window.mqttLeer = mqttLeer;
window.mqttComando = mqttComando;
window.mqttRelay = mqttRelay;
window.simSend = simSend;
window.simCargar = simCargar;
window.probarWebSocket = probarWebSocket;
window.probarDB = probarDB;
