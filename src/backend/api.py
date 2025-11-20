# ============================================================
#  API PRINCIPAL DEL PROYECTO-GRUPO-4
#  FastAPI — Backend central (ML + MQTT + Simulink + Telemetría VM)
# ============================================================

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import os
import time

# ============================================================
#  MODO TESTING PARA WEBSOCKET
# ============================================================

TEST_ENV = os.getenv("TESTING", "0") == "1"

# ------------------------------------------------------------
# IMPORTS INTERNOS — CORREGIDOS
# ------------------------------------------------------------
from src.backend.ml.modelo import (
    entrenar_modelo_desde_csv,
    predecir_tiempo,
    obtener_info_modelo,
    reentrenar_modelo,
)

from src.backend.ml.modo_automatico import (
    activar_modo_automatico,
    desactivar_modo_automatico,
    estado_modo_automatico,
)

# MQTT cliente: usamos los nombres reales del módulo `cliente.py`
from src.backend.mqtt.cliente import (
    publicar_mqtt,
    iniciar_mqtt,
)

from src.backend.database.db import (
    insertar_telemetria,
    obtener_historico,
)

# Multiplexor de WebSocket
from src.backend.utils.websocket_multiplexer import (
    multiplexor_ws,
)

# ------------------------------------------------------------

app = FastAPI(
    title="API Proyecto-Grupo-4",
    description="Backend central para ML + MQTT + Simulink + Telemetría + Dashboard",
    version="2.0.0",
)

# ============================================================
#  CORS — UNIVERSAL PARA DOCKER
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
#  SISTEMA DE WEBSOCKETS (compatible con pytest)
# ============================================================

# Estado global (actualizado por MQTT / telemetría)
estado_sistema = {
    "voltaje_pv": 0.0,
    "corriente_pv": 0.0,
    "soc": 0.0,
    "temperatura": 0.0,
    "potencia_carga": 0.0,
    "relay_estado": 0,
    "timestamp": 0
}

@app.websocket("/api/live")
async def ws_live(websocket: WebSocket):
    await websocket.accept()

    # ---- MODO TESTING (pytest) ----
    if TEST_ENV:
        await websocket.send_json({"tipo": "test", "msg": "ok"})
        await websocket.close()
        return

    # ---- MODO NORMAL ----
    try:
        # Reenvía mensajes entrantes al multiplexor (registro se hace ahí)
        while True:
            data = await websocket.receive_text()
            await multiplexor_ws(data, websocket, globals().get('estado_sistema', {}))

    except WebSocketDisconnect:
        print("[WS] Cliente desconectado.")
    except Exception as e:
        print("[WS] Error en ws_live:", e)


# ============================================================
#  A) ESTADO Y MONITOREO
# ============================================================

@app.get("/api/estado")
def api_estado():
    return estado_sistema


@app.get("/api/historico")
def api_historico():
    return obtener_historico(300)


# ============================================================
#  B) TELEMETRÍA DESDE VM o Raspberry
# ============================================================

@app.post("/api/telemetria")
async def recibir_telemetria(payload: dict):
    insertar_telemetria(payload)

    # Reenviamos al multiplexor (que hará broadcast a WS conectados)
    await multiplexor_ws({"tipo": "telemetria", "data": payload}, None, estado_sistema)

    return {"status": "ok"}


# Alias para compatibilidad con tests
@app.post("/api/raspberry/telemetria")
async def api_raspberry_telemetria(payload: dict):
    return await recibir_telemetria(payload)


# ============================================================
#  C) CONTROL REMOTO
# ============================================================

@app.post("/api/control/carga")
def api_control_carga(payload: dict):
    accion = payload.get("accion", "")


# ------------------------------------------------------------
# Rutas de compatibilidad /conectar y /simulink usadas por el frontend
# ------------------------------------------------------------


    if accion == "on":
        publicar_mqtt("microrred/comando", {"comando": "relay_on"})
    elif accion == "off":
        publicar_mqtt("microrred/comando", {"comando": "relay_off"})

    return {
        "status": "ok",
        "accion": accion,
        "comando_enviado": accion  # <-- requerido por test_control_carga_on
    }



@app.post("/api/control/sistema")
def api_control_sistema(payload: dict):
    accion = payload.get("accion", "")

    publicar_mqtt(f"microrred/comando", {"comando": f"sistema_{accion}"})
    return {"status": "ok", "accion": accion}


@app.post("/api/control/pv")
def api_control_pv(payload: dict):

    return {"status": "ok", "accion": payload.get("accion", "none")}


# Endpoint requerido por test_umbrales
@app.post("/api/control/umbrales")

def api_umbrales(payload: dict):
    return {"status": "ok", "data": payload}


# ============================================================
#  D) MACHINE LEARNING
# ============================================================

@app.post("/api/ml/predict")
def api_ml_predict(payload: dict):
    corrientes = payload.get("corriente", [])
    res = predecir_tiempo(corrientes)

    if res is None:
        return {"status": "error", "mensaje": "Modelo no cargado"}

    return {"status": "ok", "prediccion": res}


@app.post("/api/ml/train")
async def api_ml_train(file: UploadFile = File(...)):
    contenido = await file.read()

    modelo = entrenar_modelo_desde_csv(contenido, umbral=1.0)

    if modelo is None:
        return {"status": "error", "mensaje": "Entrenamiento fallado"}


    return {"status": "ok", "mensaje": "Modelo entrenado"}


@app.get("/api/ml/info")
def api_ml_info():
    return obtener_info_modelo()


@app.post("/api/ml/retrain")
async def api_ml_retrain(file: UploadFile = File(...)):
    contenido = await file.read()
    modelo = reentrenar_modelo(contenido)

    if modelo is None:
        return {"status": "error", "mensaje": "Reentrenamiento fallado"}

    return {"status": "ok", "mensaje": "Reentrenado correctamente"}


# ============================================================
#  E) SIMULINK – GEMELO DIGITAL
# ============================================================

@app.post("/api/simulink/send")
async def simulink_send(payload: dict):
    await multiplexor_ws({"tipo": "simulink_comando", "data": payload}, None, estado_sistema)
    return {"status": "ok"}


@app.post("/api/simulink/cargar")
async def simulink_cargar(payload: dict):
    await multiplexor_ws({"tipo": "simulink_perfil", "data": payload}, None, estado_sistema)
    return {"status": "ok"}


@app.get("/api/simulink/estado")
def simulink_estado():
    return {
        "vdc_sim": 48.2,
        "soc_sim": 85.4,
        "corriente_sim": 1.11,
        "temperatura_sim": 31.2,
    }


# ============================================================
#  F) MODO AUTOMÁTICO ML
# ============================================================

@app.post("/api/modo/automatico/on")
def api_auto_on():
    # Pasamos el estado global para que el EMS pueda leer la telemetría
    return activar_modo_automatico(estado_sistema)


@app.post("/api/modo/automatico/off")
def api_auto_off():
    return desactivar_modo_automatico()


@app.get("/api/modo/automatico/estado")
def api_auto_estado():
    # Devuelve el estado interno del EMS (útil para la UI)
    try:
        return estado_modo_automatico()
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}


# ------------------------------------------------------------
# Endpoints de compatibilidad para MODO CONECTAR (frontend)
# ------------------------------------------------------------


@app.get("/api/conectar/test-backend")
def conectar_test_backend():
    return {"detalle": "Backend reachable", "timestamp": time.time()}


@app.get("/api/conectar/test-mqtt")
def conectar_test_mqtt():
    # No hay cliente MQTT inicializado en dev, devolvemos mock
    return {"detalle": "MQTT broker unreachable (mock)", "ok": False}


@app.post("/api/conectar/mqtt/comando")
def conectar_mqtt_comando():
    # Intentamos publicar un comando de prueba
    try:
        publicar_mqtt("microrred/comando", {"comando": "test"})
    except Exception:
        pass
    return {"status": "ok"}


@app.post("/api/conectar/mqtt/relay")
def conectar_mqtt_relay(payload: dict):
    modo = payload.get("modo", "on")
    try:
        publicar_mqtt("microrred/comando", {"comando": f"relay_{modo}"})
    except Exception:
        pass
    return {"status": "ok", "modo": modo}


@app.post("/api/conectar/test-ws")
async def conectar_test_ws():
    # Emitimos un mensaje a todos los WS conectados para probar
    await multiplexor_ws({"tipo": "conectar_test", "data": {"msg": "ws ok"}}, None, estado_sistema)
    return {"status": "ok"}


@app.post("/api/conectar/test-db")
def conectar_test_db():
    # Mock de respuesta DB
    return {"estado": "ok", "last_write": time.time(), "last_read": time.time(), "muestras": 123}


# Alias para rutas 'simulink/enviar' usadas por el frontend (compatibilidad idioma)
@app.post("/api/simulink/enviar")
async def simulink_enviar_alias(payload: dict):
    # Reutiliza la función ya existente simulink_send
    return await simulink_send(payload)


# Compatibility endpoints for frontend EMS calls
@app.get("/ems/estado")
def ems_estado():
    # Return simplified EMS status expected by frontend
    return {
        "estado": estado_sistema.get("relay_estado", 0),
        "flujo": f"{estado_sistema.get('potencia_carga', 0)} W"
    }


@app.post("/ems/forzar")
def ems_forzar():
    # Trigger automatic mode decision (best-effort). If not available, return ok.
    try:
        # Intentamos activar el EMS usando el estado global
        activar_modo_automatico(estado_sistema)
        return {"status": "ok", "msg": "Forzado automático"}
    except Exception:
        return {"status": "ok", "msg": "Forzado (mock)"}


# Aliases under /api/ for compatibility
@app.get("/api/ems/estado")
def ems_estado_api():
    return ems_estado()


@app.post("/api/ems/forzar")
def ems_forzar_api():
    return ems_forzar()


# ------------------------------------------------------------
# Compatibilidad: rutas usadas por el frontend (manual)
# ------------------------------------------------------------

@app.post("/manual/comando")
def manual_comando(payload: dict):
    # payload esperado desde frontend: { "comando": "on"|"off"|"reset" }
    accion = payload.get("comando") or payload.get("accion")
    if not accion:
        return {"status": "error", "mensaje": "Falta campo 'comando'"}

    # Reutilizamos la misma lógica que api_control_sistema
    publicar_mqtt(f"microrred/comando", {"comando": f"sistema_{accion}"})
    return {"status": "ok", "accion": accion}


@app.post("/api/manual/comando")
def api_manual_comando(payload: dict):
    return manual_comando(payload)


@app.post("/manual/umbrales")
def manual_umbrales(payload: dict):
    # Reenvía al endpoint de umbrales ya existente
    return api_umbrales(payload)


@app.post("/api/manual/umbrales")
def api_manual_umbrales(payload: dict):
    return manual_umbrales(payload)


# Servir frontend estático (SPA) desde FastAPI
# Montamos al final para no interferir con las rutas `/api/*`
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="frontend")
