# ============================================================
#  MODELO ML — PROYECTO-GRUPO-4
#  Predicción tiempo a umbral + evaluación + reentrenamiento
# ============================================================

import os
import json
import numpy as np
from datetime import datetime

from sklearn.metrics import mean_absolute_percentage_error
from tensorflow.keras.models import load_model
import joblib

from src.backend.database.db import obtener_historico

# ------------------------------------------------------------
# RUTAS DE ARCHIVOS ML
# ------------------------------------------------------------
MODEL_PATH      = os.getenv("MODEL_PATH",      "src/backend/ml/Modelo_entrenado.keras")
SCALER_X_PATH   = os.getenv("SCALER_X_PATH",   "src/backend/ml/scaler_X.save")
SCALER_Y_PATH   = os.getenv("SCALER_Y_PATH",   "src/backend/ml/scaler_y.save")

# ------------------------------------------------------------
# VARIABLES GLOBALES
# ------------------------------------------------------------
_model = None
_scaler_X = None
_scaler_y = None


# ============================================================
#  CARGAR MODELO ML + SCALERS
# ============================================================

def cargar_modelo():
    global _model, _scaler_X, _scaler_y

    try:
        _model = load_model(MODEL_PATH)
        print(f"[ML] Modelo cargado desde {MODEL_PATH}")
    except Exception as e:
        print(f"[ML] ❌ No se pudo cargar el modelo: {e}")
        _model = None

    try:
        _scaler_X = joblib.load(SCALER_X_PATH)
        _scaler_y = joblib.load(SCALER_Y_PATH)
        print("[ML] Scalers cargados correctamente.")
    except Exception as e:
        print(f"[ML] ❌ No se pudo cargar scaler_X o scaler_y: {e}")
        _scaler_X = None
        _scaler_y = None


# Cargar al importar el módulo
print("[ML] Modelo no encontrado — ML desactivado temporalmente.")
# cargar_modelo()


# ============================================================
#  FUNCIÓN: entrenar modelo desde CSV (modo investigación)
# ============================================================

def entrenar_modelo_desde_csv(contenido_csv: bytes):
    """
    Recibe un archivo CSV para reentrenar el modelo.
    Esta función es simplificada (FASE 2).
    """
    try:
        texto = contenido_csv.decode("utf-8").splitlines()
        print(f"[ML] CSV recibido para entrenamiento. Filas: {len(texto)}")

        # Aquí se implementaría el entrenamiento REAL
        # Para ahora devolvemos un mock informativo:
        return {
            "status": "ok",
            "msg": "Entrenamiento realizado (mock).",
            "filas": len(texto)
        }

    except Exception as e:
        return {"status": "error", "msg": str(e)}


# ============================================================
#  FUNCIÓN PRINCIPAL DE PREDICCIÓN (RF2)
# ============================================================

def predecir_tiempo(features: dict):
    """
    Predice tiempo hasta violar un umbral usando:
        - PV (V,I)
        - Batería (V,I,SoC)
        - Temperaturas (ambiente y batería)
        - Corriente de carga
    """

    # Validar que el modelo existe
    if _model is None or _scaler_X is None or _scaler_y is None:
        return {"status": "error", "msg": "Modelo ML no cargado."}

    # Extraer las features necesarias
    try:
        x = np.array([[
            features.get("pv_voltage"),
            features.get("pv_current"),

            features.get("battery_voltage"),
            features.get("battery_current"),
            features.get("soc"),

            features.get("temperature_ambient"),
            features.get("temperature_battery"),

            features.get("load_current")
        ]], dtype=float)

    except Exception:
        return {"status": "error", "msg": "Features inválidas para ML."}

    # Escalar X
    X_scaled = _scaler_X.transform(x)

    # Predicción
    pred_scaled = _model.predict(X_scaled)
    pred = _scaler_y.inverse_transform(pred_scaled)[0][0]

    # Interpretación
    out = {
        "status": "ok",
        "prediccion": float(pred),  # tiempo estimado
        "unidad": "minutos",
        "timestamp": datetime.utcnow().isoformat()
    }

    return out


# ============================================================
#  FUNCIÓN: obtener información del modelo (Modo ML)
# ============================================================

def obtener_info_modelo():
    """
    Devuelve detalles del modelo cargado, útil para Modo ML del frontend.
    """
    info = {}

    if _model:
        info["modelo"] = str(_model)
        info["capas"] = len(_model.layers)
        info["parametros"] = int(_model.count_params())
    else:
        info["modelo"] = "No cargado"

    info["scaler_X"] = "ok" if _scaler_X else "no cargado"
    info["scaler_y"] = "ok" if _scaler_y else "no cargado"

    return info


# ============================================================
#  FUNCIÓN: reentrenar modelo (RNF5)
# ============================================================

def reentrenar_modelo():
    """
    Reentrena el modelo si MAPE supera un umbral o si se llama manualmente.
    La versión actual es un mock para FASE 2.
    """
    # 1) Obtener histórico reciente
    rows = obtener_historico(limit=500)
    if not rows:
        return {"status": "error", "msg": "No hay datos para reentrenar."}

    # 2) Aquí iría la lógica real de reentrenamiento
    #    Cargar dataset → entrenar → guardar → recargar

    return {
        "status": "ok",
        "msg": "Reentrenamiento completado (mock).",
        "registros_usados": len(rows)
    }


# ============================================================
#  FUNCIÓN: evaluar MAPE (RNF5)
# ============================================================

def evaluar_mape(y_true, y_pred):
    """
    Evalúa el desempeño del modelo ML usando MAPE.
    """
    try:
        return mean_absolute_percentage_error(y_true, y_pred)
    except Exception as e:
        print("[ML] Error evaluando MAPE:", e)
        return None
