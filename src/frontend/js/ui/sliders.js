// ======================================================================
// SLIDERS — INICIALIZACIÓN GENERAL DE SLIDERS
// ======================================================================

import { addLog } from "../core/logger.js";
import { setText } from "../core/utils.js";

export function initSliders() {
    const sliderPot = document.getElementById("slider-potencia");
    const valPot = document.getElementById("slider-potencia-value");
    if (sliderPot && valPot) {
        valPot.textContent = `${sliderPot.value} %`;
        sliderPot.addEventListener("input", () => {
            valPot.textContent = `${sliderPot.value} %`;
        });
    }

    const umbralV = document.getElementById("umbral-vbat-min");
    const umbralVVal = document.getElementById("umbral-vbat-min-value");
    if (umbralV && umbralVVal) {
        umbralVVal.textContent = `${umbralV.value} V`;
        umbralV.addEventListener("input", () => {
            umbralVVal.textContent = `${umbralV.value} V`;
        });
    }

    const umbralI = document.getElementById("umbral-ibat-max");
    const umbralIVal = document.getElementById("umbral-ibat-max-value");
    if (umbralI && umbralIVal) {
        umbralIVal.textContent = `${umbralI.value} A`;
        umbralI.addEventListener("input", () => {
            umbralIVal.textContent = `${umbralI.value} A`;
        });
    }

    const umbralT = document.getElementById("umbral-tbat-max");
    const umbralTVal = document.getElementById("umbral-tbat-max-value");
    if (umbralT && umbralTVal) {
        umbralTVal.textContent = `${umbralT.value} °C`;
        umbralT.addEventListener("input", () => {
            umbralTVal.textContent = `${umbralT.value} °C`;
        });
    }

    addLog("Sliders inicializados");
}
