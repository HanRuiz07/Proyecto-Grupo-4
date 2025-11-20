// ======================================================================
// ESTADO GLOBAL DEL DASHBOARD (CENTRALIZADO)
// ======================================================================

export const state = {
    modo: "manual",
    logs: [],
    connected: {
        backend: false,
        mqtt: false,
        ws: false,
        db: false,
        simulink: false,
        raspberry: false
    },
    kpis: {
        pv: 0,
        soc: 0,
        vbus: 0,
        corriente: 0,
        eficiencia: 98,
        temp: 0
    },
    charts: {},
    ws: null,
    wsRetryCount: 0,

    config: {
        // Llevamos el prefijo `/api` para que las llamadas `safeFetch('/ml/info')`
        // se resuelvan a `http://host:8000/api/ml/info`.
        api_base: `${window.location.protocol}//${window.location.hostname}:8000/api`,
        // WebSocket ahora apunta al endpoint real del backend `/api/live`.
        ws_url: `ws://${window.location.hostname}:8000/api/live`
    }
};
