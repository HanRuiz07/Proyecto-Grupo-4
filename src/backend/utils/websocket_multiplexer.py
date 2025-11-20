# ============================================================
#  WEBSOCKET MULTIPLEXER — PROYECTO-GRUPO-4
#  Conecta backend ↔ frontend para telemetría + EMS + histórico
# ============================================================

import json
from typing import Any, Dict, List
from fastapi import WebSocket

from src.backend.database.db import obtener_historico

# Lista global de clientes WebSocket conectados
_WS_CLIENTS: List[WebSocket] = []


# ------------------------------------------------------------
#  FUNCIONES INTERNAS
# ------------------------------------------------------------

async def _safe_send(ws: WebSocket, message: Dict[str, Any]) -> bool:
    """
    Envía un mensaje JSON a un cliente.
    Devuelve False si el WebSocket está muerto.
    """
    try:
        await ws.send_text(json.dumps(message))
        return True
    except Exception as e:
        print(f"[WS] Error enviando a cliente: {e}")
        return False


async def broadcast(payload: Dict[str, Any]) -> None:
    """
    Envía el mismo payload a TODOS los clientes conectados.
    Limpia los que estén muertos.
    """
    if not _WS_CLIENTS:
        return

    vivos: List[WebSocket] = []
    for ws in _WS_CLIENTS:
        ok = await _safe_send(ws, payload)
        if ok:
            vivos.append(ws)

    # Actualizamos solo con los que siguen vivos
    if len(vivos) != len(_WS_CLIENTS):
        print(f"[WS] Limpiando clientes muertos. Activos: {len(vivos)}")
    _WS_CLIENTS[:] = vivos


# ------------------------------------------------------------
#  MULTIPLEXOR PRINCIPAL
# ------------------------------------------------------------

async def multiplexor_ws(message: Any, ws: WebSocket | None, state: Dict[str, Any]) -> None:
    """
    Punto central de ruteo de mensajes WebSocket.

    CASO 1: mensaje viene del FRONTEND (ws != None, message string JSON)
      - Registrar cliente.
      - Interpretar 'tipo' de mensaje y responder.

    CASO 2: mensaje viene del BACKEND (/telemetria) (ws == None, message dict)
      - Se hace broadcast directo a todos los clientes.

    Esto permite que:
      - /ws maneje comandos del usuario
      - /telemetria empuje datos live al dashboard
    """

    # -------------------------------
    # CASO 2: backend → broadcast
    # -------------------------------
    if ws is None:
        # Se asume que message ya es dict listo para enviar
        if isinstance(message, dict):
            await broadcast(message)
        else:
            print("[WS] Advertencia: mensaje backend no es dict, se ignora.")
        return

    # -------------------------------
    # CASO 1: frontend → backend
    # -------------------------------
    # Registramos el cliente si no estaba
    if ws not in _WS_CLIENTS:
        _WS_CLIENTS.append(ws)
        print(f"[WS] Nuevo cliente registrado. Total: {len(_WS_CLIENTS)}")

    # Parsear el mensaje si es string
    if isinstance(message, str):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            # Mensaje simple (ej: "ping")
            data = {"tipo": message}
    elif isinstance(message, dict):
        data = message
    else:
        print("[WS] Tipo de mensaje no soportado desde frontend.")
        return

    tipo = data.get("tipo")

    # -------------------------------
    # 1) Ping / keep-alive
    # -------------------------------
    if tipo == "ping":
        await _safe_send(ws, {"tipo": "pong"})
        return

    # -------------------------------
    # 2) Solicitar estado actual (KPIs)
    # -------------------------------
    if tipo == "solicitar_estado":
        await _safe_send(ws, {
            "tipo": "estado_actual",
            "data": {
                "state": state
            }
        })
        return

    # -------------------------------
    # 3) Solicitar histórico (para gráficos)
    # -------------------------------
    if tipo == "solicitar_historico":
        limite = data.get("limit", 300)
        rows = obtener_historico(limit=limite) or []
        await _safe_send(ws, {
            "tipo": "historico",
            "data": rows
        })
        return

    # -------------------------------
    # 4) Otros tipos (extensible)
    # -------------------------------
    # Aquí puedes enrutar más comandos, por ejemplo:
    # - cambiar modo
    # - disparar pruebas de conexión (Modo Conectar)
    # - etc.
    await _safe_send(ws, {
        "tipo": "ack",
        "msg": f"Comando recibido (tipo={tipo})"
    })
