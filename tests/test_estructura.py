# tests/test_estructura.py
import os

def test_project_structure():
    """
    Verifica la estructura REAL del Proyecto-Grupo-4
    según el árbol que definiste.
    """

    rutas = [
        # Backend raíz
        "src/backend/api.py",
        "src/backend/__init__.py",

        # ML
        "src/backend/ml/__init__.py",
        "src/backend/ml/modelo.py",
        "src/backend/ml/modo_automatico.py",

        # MQTT
        "src/backend/mqtt/__init__.py",
        "src/backend/mqtt/cliente.py",

        # Database
        "src/backend/database/__init__.py",
        "src/backend/database/db.py",

        # Simulink
        "src/backend/simulink/__init__.py",
        "src/backend/simulink/simulink_bridge.py",

        # Frontend
        "src/frontend/index.html",
        "src/frontend/dashboard.js",
        "src/frontend/style.css",
    ]

    for ruta in rutas:
        assert os.path.exists(ruta), f"❌ Falta archivo crítico: {ruta}"
