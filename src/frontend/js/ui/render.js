// ======================================================================
// RENDER HELPERS
// ======================================================================

export function clear(el) {
    if (!el) return;
    el.innerHTML = "";
}

export function append(el, html) {
    if (!el) return;
    el.innerHTML += html;
}
