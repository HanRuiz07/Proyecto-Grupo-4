// ======================================================================
// CHARTS — INICIALIZACIÓN Y ACTUALIZACIÓN DE GRÁFICOS
// ======================================================================

import { state } from "../core/state.js";

function baseTimeSeriesConfig(label, colorIndex = 0) {
    return {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label,
                data: [],
                tension: 0.1,
                pointRadius: 0,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                x: {
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    };
}

export function initCharts() {
    const ids = [
        "graf1","graf2","graf3","graf4",
        "auto-graf-acciones","auto-graf-pred-real",
        "ml-graf-pred-real","ml-graf-residuales","ml-graf-feature-importance",
        "conect-graf-mqtt-lat","conect-graf-ws-lat"
    ];

    ids.forEach(id => {
        const canvas = document.getElementById(id);
        if (!canvas) return;

        let label = id;

        if (id === "graf1") label = "Potencia PV";
        if (id === "graf2") label = "Potencia carga";
        if (id === "graf3") label = "Corriente batería";
        if (id === "graf4") label = "SoC batería";

        const cfg = baseTimeSeriesConfig(label);
        const chart = new Chart(canvas.getContext("2d"), cfg);
        state.charts[id] = chart;
    });
}

function pushPoint(chart, y) {
    if (!chart) return;
    const maxPoints = 60;
    const lbl = "";
    chart.data.labels.push(lbl);
    chart.data.datasets[0].data.push(y);

    if (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    chart.update("none");
}

export function updateChartsFromTelemetry(data) {
    const ts = data.timestamp || Date.now();
    const tLabel = new Date(ts * (ts < 1e12 ? 1000 : 1)).toLocaleTimeString();

    const c1 = state.charts["graf1"];
    const c2 = state.charts["graf2"];
    const c3 = state.charts["graf3"];
    const c4 = state.charts["graf4"];

    if (c1) {
        c1.data.labels.push(tLabel);
        c1.data.datasets[0].data.push(data.p_pv ?? (data.v_pv || 0) * (data.i_pv || 0));
        trimChart(c1);
        c1.update("none");
    }

    if (c2) {
        c2.data.labels.push(tLabel);
        c2.data.datasets[0].data.push(data.p_load ?? (data.v_bat || 0) * (data.i_bat || 0));
        trimChart(c2);
        c2.update("none");
    }

    if (c3) {
        c3.data.labels.push(tLabel);
        c3.data.datasets[0].data.push(data.i_bat ?? 0);
        trimChart(c3);
        c3.update("none");
    }

    if (c4) {
        c4.data.labels.push(tLabel);
        c4.data.datasets[0].data.push(data.soc ?? 0);
        trimChart(c4);
        c4.update("none");
    }
}

function trimChart(chart) {
    const maxPoints = 60;
    while (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
}
