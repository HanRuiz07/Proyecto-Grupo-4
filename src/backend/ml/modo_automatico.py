# ============================================================
#  MODO AUTOMÁTICO (EMS) — PROYECTO-GRUPO-4
#  Energy Management System basado en:
#   - SoC
#   - Temperatura batería vs ambiente
#   - Corrientes PV / batería / carga
#   - Predicción ML (tiempo a umbral)
# ============================================================

import os
import threading
import time
from typing import Dict, Any, Optional

from src.backend.mqtt.cliente import publicar_mqtt
from src.backend.ml.modelo import predecir_tiempo

# ------------------------------------------------------------
# UMBRALES DEL EMS (configurables por variables de entorno)
# ------------------------------------------------------------

SOC_CRITICO = float(os.getenv("EMS_SOC_CRITICO", "20"))   # %
SOC_BAJO    = float(os.getenv("EMS_SOC_BAJO", "35"))      # %

TEMP_BAT_ALTA       = float(os.getenv("EMS_TEMP_BAT_ALTA", "40"))   # °C
TEMP_BAT_EMERGENCIA = float(os.getenv("EMS_TEMP_BAT_EMERG", "45"))  # °C
DELTA_T_MAX         = float(os.getenv("EMS_DELTA_T_MAX", "7"))      # °C

PERIODO_LOOP_S   = float(os.getenv("EMS_LOOP_PERIOD", "5"))   # periodo del lazo EMS
PERIODO_ML_CICLOS = int(os.getenv("EMS_ML_CADENCE", "3"))     # cada N ciclos se pide predicción ML

TOPIC_CMD_EMS = os.getenv("EMS_TOPIC_CMD", "microrred/comando")


# ------------------------------------------------------------
# ESTADO INTERNO DEL EMS
# ------------------------------------------------------------

_ems_activo: bool = False
_ems_thread: Optional[threading.Thread] = None
_state_ref: Optional[Dict[str, Any]] = None  # referencia al state de api.py

_ems_estado: Dict[str, Any] = {
    "activo": False,
    "ultima_accion": None,
    "ultimo_motivo": None,
    "ultimo_timestamp": None,
    "ultima_prediccion_min": None,
    "ultima_entrada": None,
}


# ============================================================
#  FUNCIONES PÚBLICAS REQUERIDAS POR api.py
# ============================================================

def activar_modo_automatico(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activa el lazo EMS en un hilo en segundo plano.
    'state' es el diccionario global compartido con api.py.
    """
    global _ems_activo, _ems_thread, _state_ref

    if _ems_activo:
        return {"status": "ok", "msg": "EMS ya estaba activo."}

    _state_ref = state
    _ems_activo = True
    _ems_estado["activo"] = True

    _ems_thread = threading.Thread(target=_loop_ems, daemon=True)
    _ems_thread.start()

    print("[EMS] Modo automático ACTIVADO.")
    return {"status": "ok", "msg": "EMS activado."}


def desactivar_modo_automatico() -> Dict[str, Any]:
    """
    Desactiva el lazo EMS.
    """
    global _ems_activo
    _ems_activo = False
    _ems_estado["activo"] = False
    print("[EMS] Modo automático DESACTIVADO.")
    return {"status": "ok", "msg": "EMS desactivado."}


def estado_modo_automatico() -> Dict[str, Any]:
    """
    Devuelve el estado interno del EMS (para /automatico/estado).
    """
    return dict(_ems_estado)


# ============================================================
#  LOOP PRINCIPAL EMS (EJECUTADO EN HILO SEPARADO)
# ============================================================

def _loop_ems():
    """
    Lazo principal del EMS:
      - Lee el estado actual de la microrred desde _state_ref.
      - Evalúa reglas de protección y optimización.
      - Puede llamar a la predicción ML periódicamente.
      - Envía comandos MQTT si es necesario.
    """
    ciclo = 0
    while _ems_activo:
        ciclo += 1

        try:
            snapshot = dict(_state_ref) if isinstance(_state_ref, dict) else {}
            _evaluar_reglas(snapshot, ciclo)
        except Exception as e:
            print(f"[EMS] Error en loop EMS: {e}")

        time.sleep(PERIODO_LOOP_S)


# ============================================================
#  REGLAS PRINCIPALES DEL EMS
# ============================================================

def _evaluar_reglas(s: Dict[str, Any], ciclo: int) -> None:
    """
    Aplica las reglas definidas a partir del snapshot de estado 's'.
    Actualiza _ems_estado y, si hace falta, publica comandos MQTT.
    """

    # Extractores con default None
    pv_v = s.get("pv_voltage")
    pv_i = s.get("pv_current")

    bat_v = s.get("battery_voltage")
    bat_i = s.get("battery_current")
    soc   = s.get("soc")

    t_amb = s.get("temperature_ambient")
    t_bat = s.get("temperature_battery")

    i_load = s.get("load_current")
    modo   = s.get("modo", "automatico")

    acciones: list[Dict[str, Any]] = []
    motivo_principal = None

    # -------------------------------------------
    # 1) PROTECCIÓN TÉRMICA BATERÍA (prioridad alta)
    # -------------------------------------------
    if t_bat is not None:
        # Emergencia: sobretemperatura absoluta
        if t_bat >= TEMP_BAT_EMERGENCIA:
            motivo_principal = "sobretemperatura_bateria_emer"
            acciones.append({
                "accion": "cortar_carga",
                "motivo": motivo_principal
            })

        # Temperatura alta, sin llegar a emergencia
        elif t_bat >= TEMP_BAT_ALTA:
            motivo_principal = "temperatura_bateria_alta"
            acciones.append({
                "accion": "reducir_carga",
                "motivo": motivo_principal
            })

        # Comparación con ambiente (ΔT)
        if t_amb is not None:
            delta_t = t_bat - t_amb
            if delta_t >= DELTA_T_MAX and motivo_principal is None:
                motivo_principal = "delta_termico_alto"
                acciones.append({
                    "accion": "modo_seguro",
                    "motivo": motivo_principal
                })

    # -------------------------------------------
    # 2) PROTECCIÓN POR SOC (batería)
    # -------------------------------------------
    if soc is not None:
        try:
            soc_val = float(soc)
        except (TypeError, ValueError):
            soc_val = None

        if soc_val is not None:
            if soc_val <= SOC_CRITICO:
                if motivo_principal is None:
                    motivo_principal = "soc_critico"
                acciones.append({
                    "accion": "cortar_carga",
                    "motivo": "soc_critico"
                })
            elif soc_val <= SOC_BAJO:
                if motivo_principal is None:
                    motivo_principal = "soc_bajo"
                acciones.append({
                    "accion": "reducir_carga",
                    "motivo": "soc_bajo"
                })

    # -------------------------------------------
    # 3) USO DE ML (cada N ciclos)
    # -------------------------------------------
    pred_min = None
    if ciclo % PERIODO_ML_CICLOS == 0:
        features = {
            "pv_voltage": pv_v,
            "pv_current": pv_i,
            "battery_voltage": bat_v,
            "battery_current": bat_i,
            "soc": soc,
            "temperature_ambient": t_amb,
            "temperature_battery": t_bat,
            "load_current": i_load
        }
        try:
            res = predecir_tiempo(features)
            if res.get("status") == "ok":
                pred_min = res.get("prediccion")
                # Si el tiempo a umbral es muy bajo, reforzar acciones
                if pred_min is not None and pred_min < 10 and motivo_principal is None:
                    motivo_principal = "prediccion_ml_tiempo_bajo"
                    acciones.append({
                        "accion": "modo_seguro",
                        "motivo": motivo_principal
                    })
        except Exception as e:
            print(f"[EMS] Error llamando a ML: {e}")

    # -------------------------------------------
    # 4) SI NO HAY ACCIONES, SALIMOS
    # -------------------------------------------
    if not acciones:
        # Sin cambios, pero actualizamos estado minimal
        _ems_estado["ultima_prediccion_min"] = pred_min
        _ems_estado["ultima_entrada"] = {
            "pv_voltage": pv_v,
            "pv_current": pv_i,
            "battery_voltage": bat_v,
            "battery_current": bat_i,
            "soc": soc,
            "temperature_ambient": t_amb,
            "temperature_battery": t_bat,
            "load_current": i_load,
            "modo": modo,
        }
        return

    # -------------------------------------------
    # 5) PUBLICAR COMANDOS MQTT (según acciones)
    # -------------------------------------------
    for a in acciones:
        cmd = _traducir_accion_a_payload(a["accion"], a["motivo"])
        if cmd:
            publicar_mqtt(TOPIC_CMD_EMS, cmd)

    # Guardamos solo la primera como "principal"
    accion_main = acciones[0]["accion"]
    motivo_main = acciones[0]["motivo"]

    # -------------------------------------------
    # 6) ACTUALIZAR ESTADO EMS
    # -------------------------------------------
    ts = time.time()
    _ems_estado["ultima_accion"] = accion_main
    _ems_estado["ultimo_motivo"] = motivo_main
    _ems_estado["ultimo_timestamp"] = ts
    _ems_estado["ultima_prediccion_min"] = pred_min
    _ems_estado["ultima_entrada"] = {
        "pv_voltage": pv_v,
        "pv_current": pv_i,
        "battery_voltage": bat_v,
        "battery_current": bat_i,
        "soc": soc,
        "temperature_ambient": t_amb,
        "temperature_battery": t_bat,
        "load_current": i_load,
        "modo": modo,
    }

    print(f"[EMS] Acción: {accion_main} | Motivo: {motivo_main} | pred={pred_min} min")


# ============================================================
#  TRADUCCIÓN DE ACCIONES EMS → PAYLOAD MQTT
# ============================================================

def _traducir_accion_a_payload(accion: str, motivo: str) -> Optional[Dict[str, Any]]:
    """
    Convierte una acción lógica del EMS en un payload MQTT estándar
    para que la Raspberry/VM sepa qué hacer.

    Algunas acciones típicas:
    - cortar_carga  → relay OFF / PWM = 0
    - reducir_carga → bajar PWM
    - modo_seguro   → perfil de operación más conservador
    """
    base = {
        "source": "ems",
        "motivo": motivo,
        "accion": accion,
    }

    if accion == "cortar_carga":
        base.update({
            "relay": 0,          # apagar relé
            "pwm": 0             # opcional: PWM 0
        })
    elif accion == "reducir_carga":
        base.update({
            "modo_pwm": "bajo",  # indica a la Raspi que reduzca carga
        })
    elif accion == "modo_seguro":
        base.update({
            "modo": "seguro"     # la Raspi puede interpretar este modo
        })
    else:
        # Acción no reconocida (no publicamos nada)
        return None

    return base
