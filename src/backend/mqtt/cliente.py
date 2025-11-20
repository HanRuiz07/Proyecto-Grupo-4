# ============================================================
#  CLIENTE MQTT DEL BACKEND — PROYECTO-GRUPO-4
#  Maneja conexión con Raspberry/VM y envía telemetría al backend FastAPI
# ============================================================

import json
import threading
import time
import os
from typing import Dict, Any

from paho.mqtt import client as mqtt
import requests   # Asegúrate de tener 'requests' en requirements.txt

# ------------------------------------------------------------
# CONFIGURACIÓN MQTT (se puede sobreescribir con variables de entorno)
# ------------------------------------------------------------

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")               # nombre del servicio en Docker
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_SUB = os.getenv("MQTT_TOPIC_SUB", "microrred/telemetria")   # Raspberry/VM → backend
MQTT_TOPIC_CMD = os.getenv("MQTT_TOPIC_CMD", "microrred/comando")      # Backend → Raspberry/VM

# ------------------------------------------------------------
# CONFIGURACIÓN BACKEND (para llamar a /telemetria)
# ------------------------------------------------------------

BACKEND_URL_BASE = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_TELEMETRIA_ENDPOINT = f"{BACKEND_URL_BASE}/telemetria"

# ------------------------------------------------------------
# CLIENTE MQTT GLOBAL + REFERENCIA AL STATE DEL BACKEND
# ------------------------------------------------------------

_mqtt_client: mqtt.Client | None = None
_backend_state: Dict[str, Any] | None = None   # se setea en iniciar_mqtt(state)


# ============================================================
#  CALLBACKS DE MQTT
# ============================================================

def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None):
    """
    Callback al conectar con el broker MQTT.
    """
    print(f"[MQTT] Conectado a {MQTT_BROKER}:{MQTT_PORT} con código {rc}")
    client.subscribe(MQTT_TOPIC_SUB)
    print(f"[MQTT] Suscrito a: {MQTT_TOPIC_SUB}")


def _mapear_payload_a_backend(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recibe el JSON crudo desde Raspberry/VM y genera un payload
    coherente para el backend /telemetria, manteniendo los campos
    originales y agregando los normalizados que usa 'state' en api.py.

    Formato esperado (ejemplo recomendado FASE 2):

    {
        "v_pv": 14.1,
        "i_pv": 0.62,
        "v_bat": 12.4,
        "i_bat": -0.3,
        "soc": 78.4,
        "temp_bat": 28.5,
        "temp_amb": 24.0,
        "i_load": 0.8,
        "load": 1          # opcional: estado del relé
    }
    """
    payload = dict(data)  # copiamos todo lo que venga

    def _to_float(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    # Mapeo a las keys del state del backend (api.py)
    if "v_pv" in data:
        payload["pv_voltage"] = _to_float(data.get("v_pv"))
    if "i_pv" in data:
        payload["pv_current"] = _to_float(data.get("i_pv"))
    if "v_bat" in data:
        payload["battery_voltage"] = _to_float(data.get("v_bat"))
    if "i_bat" in data:
        payload["battery_current"] = _to_float(data.get("i_bat"))
    if "soc" in data:
        payload["soc"] = _to_float(data.get("soc"))

    # Temperaturas separadas
    if "temp_bat" in data:
        payload["temperature_battery"] = _to_float(data.get("temp_bat"))
    if "temp_amb" in data:
        payload["temperature_ambient"] = _to_float(data.get("temp_amb"))

    # Corriente de carga (intentamos usar i_load; si no, 'load' si parece numérico)
    i_load = data.get("i_load", None)
    if i_load is not None:
        payload["load_current"] = _to_float(i_load)
    else:
        # Si 'load' llega como número analógico (ej: corriente) lo convertimos
        load_val = data.get("load", None)
        if isinstance(load_val, (int, float, str)):
            payload["load_current"] = _to_float(load_val)

    # Timestamp local (útil para DB)
    payload.setdefault("timestamp", time.time())

    return payload


def _enviar_a_backend_telemetria(payload_backend: Dict[str, Any]) -> None:
    """
    Envía la telemetría al endpoint interno /telemetria del backend FastAPI.
    Esta llamada permite que:
      - se actualice el 'state' global
      - se inserte en DB
      - se envíe por WebSocket al frontend
    sin que el cliente MQTT tenga que encargarse de todo eso.
    """
    try:
        resp = requests.post(
            BACKEND_TELEMETRIA_ENDPOINT,
            json=payload_backend,
            timeout=2.0  # pequeño timeout para no trabar el hilo MQTT
        )
        if not resp.ok:
            print(f"[MQTT] Error al enviar a backend /telemetria: HTTP {resp.status_code}")
    except Exception as e:
        print(f"[MQTT] Excepción enviando a backend /telemetria: {e}")


def on_message(client: mqtt.Client, userdata, msg):
    """
    Recibe telemetría desde Raspberry/VM por MQTT en el tópico:

        microrred/telemetria  (por defecto)

    1) Decodifica el JSON
    2) Mapea nombres de campos a los usados en el backend
    3) Envía todo al endpoint /telemetria del FastAPI
    """
    try:
        raw = msg.payload.decode("utf-8")
        data = json.loads(raw)
        # print opcional: comentar en producción para menos ruido
        print("[MQTT] Telemetría recibida cruda:", data)

        payload_backend = _mapear_payload_a_backend(data)

        # Opcional: actualizar referencia local al state si se desea
        if isinstance(_backend_state, dict):
            for k, v in payload_backend.items():
                if k in _backend_state:
                    _backend_state[k] = v

        # Enviar al backend /telemetria (DB + WS + EMS)
        _enviar_a_backend_telemetria(payload_backend)

    except Exception as e:
        print("[MQTT] Error procesando mensaje:", e)


# ============================================================
#  ENVIAR COMANDO MQTT (backend → Raspberry/VM)
# ============================================================

def publicar_mqtt(topic: str, payload: Dict[str, Any]) -> None:
    """
    Publica un mensaje MQTT al tópico indicado.
    Se usa desde api.py, por ejemplo:

        publicar_mqtt("microrred/manual", {"actuador": "mosfet", "valor": 1})
    """
    global _mqtt_client
    if _mqtt_client is None:
        print("[MQTT] publicar_mqtt llamado pero el cliente aún no está inicializado.")
        return

    try:
        _mqtt_client.publish(topic, json.dumps(payload), qos=1)
        print(f"[MQTT] Publicado en {topic}: {payload}")
    except Exception as e:
        print(f"[MQTT] Error enviando comando a {topic}: {e}")


# ============================================================
#  INICIAR CLIENTE MQTT EN THREAD SEPARADO
# ============================================================

def iniciar_mqtt(state: Dict[str, Any] | None = None) -> None:
    """
    Inicia cliente MQTT en segundo plano.
    DEBE ser llamado desde FastAPI (startup_event) y NO automáticamente
    al importar el módulo, para ser compatible con Docker/K8s.

    Ejemplo (en api.py):

        @app.on_event("startup")
        async def startup_event():
            iniciar_mqtt(state)
    """
    global _mqtt_client, _backend_state

    _backend_state = state

    if _mqtt_client is not None:
        # Ya se había inicializado
        print("[MQTT] iniciar_mqtt llamado pero el cliente ya estaba creado.")
        return

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    _mqtt_client = client

    print(f"[MQTT] Conectando a broker {MQTT_BROKER}:{MQTT_PORT}...")

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        print(f"❌ No se pudo conectar a MQTT ({MQTT_BROKER}:{MQTT_PORT}): {e}")
        print("ℹ️ Backend seguirá activo sin MQTT (modo pruebas locales).")
        _mqtt_client = None
        return  # No arrancamos el hilo si no conecta

    hilo = threading.Thread(target=client.loop_forever, daemon=True)
    hilo.start()

    print("[MQTT] Cliente MQTT corriendo en hilo separado.")

# ============================================================
# Nota: el cliente WebSocket es parte del frontend (JS) y no debe
# incluirse en este archivo Python. La lógica del WebSocket del
# frontend vive en `src/frontend/js/core/websocket.js`.
