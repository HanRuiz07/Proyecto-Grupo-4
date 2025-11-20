// ======================================================================
// SISTEMA GLOBAL DE ALERTAS INDUSTRIALES
// ======================================================================

export function alert(color, message) {
    const cont = document.getElementById("alertas");
    if (!cont) return;

    const card = document.createElement("div");
    card.classList.add("alert-card");

    card.classList.add(
        color === "red" ? "alert-red" :
        color === "yellow" ? "alert-yellow" :
        "alert-green"
    );

    card.textContent = message;
    cont.appendChild(card);

    setTimeout(() => {
        if (cont.contains(card)) {
            cont.removeChild(card);
        }
    }, 3500);
}
