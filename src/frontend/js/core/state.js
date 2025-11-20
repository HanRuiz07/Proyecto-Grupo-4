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
        api_base: `${window.location.protocol}//${window.location.hostname}:8000`,
        ws_url: `ws://${window.location.hostname}:8000/ws`
    }
};
