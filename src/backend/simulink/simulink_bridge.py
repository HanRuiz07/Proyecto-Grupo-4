# ============================================================
#  SIMULINK BRIDGE — PROYECTO-GRUPO-4
#  Conexión entre Backend FastAPI ↔ MATLAB/Simulink
#  Compatible con:
#     - MATLAB Engine API (instalación local/VM)
#     - Modo MOCK (cuando no existe MATLAB)
# ============================================================

import os
import time
from typing import Dict, Any, Optional

# ------------------------------------------------------------
# CONFIGURACIÓN DEL GEMELO DIGITAL
# ------------------------------------------------------------

SIMULINK_MODEL = os.getenv("SIMULINK_MODEL", "microgrid_model")
USE_MATLAB_REAL = os.getenv("MATLAB_REAL", "0") == "1"     # 0 = mock, 1 = MATLAB real
SIMULATION_TIMEOUT = int(os.getenv("SIMULINK_TIMEOUT", "30"))

_matlab_engine = None


# ============================================================
#  INICIALIZAR MATLAB ENGINE
# ============================================================

def iniciar_matlab():
    """
    Inicia MATLAB Engine si está habilitado.
    """
    global _matlab_engine

    if not USE_MATLAB_REAL:
        print("[Simulink] Modo MOCK activado (sin MATLAB).")
        return None

    try:
        import matlab.engine
        print("[Simulink] Iniciando MATLAB Engine...")
        _matlab_engine = matlab.engine.start_matlab()
        print("[Simulink] MATLAB Engine iniciado correctamente.")
        return _matlab_engine

    except Exception as e:
        print(f"[Simulink] ❌ Error iniciando MATLAB Engine: {e}")
        print("          Cambiando a MODO MOCK.")
        _matlab_engine = None
        return None


# Llamar al inicio del módulo
iniciar_matlab()


# ============================================================
#  EJECUTAR SIMULACIÓN
# ============================================================

def ejecutar_simulacion(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta la simulación del gemelo digital con los parámetros enviados:

    params = {
        "soc_inicial": 70,
        "irradiancia": 800,
        "temperatura": 30,
        "carga": 20
    }

    Retorna series simuladas o datos mock.
    """

    # --------------------------------------------------------
    #  MODO MOCK (sin MATLAB)
    # --------------------------------------------------------
    if _matlab_engine is None:
        print("[Simulink] Ejecutando simulación MOCK...")

        soc0 = float(params.get("soc_inicial", 70))
        irr  = float(params.get("irradiancia", 800))
        temp = float(params.get("temperatura", 25))
        carga = float(params.get("carga", 20))

        # Trayectorias simuladas ficticias (útiles para frontend/DB)
        t = list(range(0, 60))
        pv_v = [14 + 0.4 * (irr/1000) - 0.01*temp for _ in t]
        pv_i = [0.3 * (irr/1000) for _ in t]
        soc = [max(0, soc0 - 0.05 * i) for i in range(len(t))]

        return {
            "status": "ok",
            "modo": "mock",
            "model": SIMULINK_MODEL,
            "timestamp": time.time(),
            "tiempo": t,
            "pv_voltage": pv_v,
            "pv_current": pv_i,
            "soc": soc
        }

    # --------------------------------------------------------
    #  MODO REAL (MATLAB)
    # --------------------------------------------------------
    try:
        import matlab

        eng = _matlab_engine
        print("[Simulink] Lanzando simulación real...")

        # Pasar parámetros al workspace
        for k, v in params.items():
            eng.workspace[k] = float(v)

        # Ejecutar la simulación
        eng.eval(f"load_system('{SIMULINK_MODEL}')", nargout=0)

        sim_out = eng.sim(
            SIMULINK_MODEL,
            nargout=1,
            timeout=SIMULATION_TIMEOUT
        )

        # Extraer señales
        pv_v = list(sim_out.get("pv_voltage", []))
        pv_i = list(sim_out.get("pv_current", []))
        soc  = list(sim_out.get("soc", []))
        t    = list(sim_out.get("tout", []))

        return {
            "status": "ok",
            "modo": "real",
            "model": SIMULINK_MODEL,
            "timestamp": time.time(),
            "tiempo": t,
            "pv_voltage": pv_v,
            "pv_current": pv_i,
            "soc": soc
        }

    except Exception as e:
        return {
            "status": "error",
            "msg": str(e),
            "modo": "real"
        }


# ============================================================
#  PRUEBA DE CONECTIVIDAD (MODO CONECTAR)
# ============================================================

def verificar_estado():
    """
    Modo Conectar:
    Devuelve si MATLAB/Simulink está operativo.
    """
    if _matlab_engine is None:
        return {
            "simulink": "mock",
            "detalles": "MATLAB no iniciado o modo_mock"
        }
    else:
        return {
            "simulink": "ok",
            "detalles": f"Modelo {SIMULINK_MODEL}"
        }
