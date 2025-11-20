// ======================================================================
// VALIDADORES PARA ML / TELEMETRÍA / CONTROL
// ======================================================================

export function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

export function isValidNumber(n) {
    return typeof n === "number" && !isNaN(n);
}
