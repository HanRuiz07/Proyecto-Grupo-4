// ======================================================================
// UTILS — FUNCIONES AUXILIARES
// ======================================================================

export function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

export function setHtml(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
}
