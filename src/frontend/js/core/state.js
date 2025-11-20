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
        // Usar puertos explícitos para frontend/backend en el entorno del usuario.
        // Frontend estará servido en el puerto 8080 y el backend en 8081.
        api_base: `${window.location.protocol}//${window.location.hostname}:8081/api`,
        // WebSocket apunta al backend en el puerto 8081
        ws_url: `ws://${window.location.hostname}:8081/api/live`
    }
};
