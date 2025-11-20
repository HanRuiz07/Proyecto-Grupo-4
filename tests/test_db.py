# tests/test_db.py
from unittest.mock import patch
from src.backend.database.db import get_conn, guardar_telemetria, obtener_historico


def test_db_connection_mock():
    # Parcheamos la ruta EXACTA usada en db.py
    with patch("src.backend.database.db.psycopg2.connect") as mock_connect:
        conn = get_conn()
        mock_connect.assert_called()
        # conn puede ser objeto real o None si falla, no nos importa aquí


def test_db_guardar_telemetria_sin_db():
    muestra = {
        "timestamp": 123,
        "voltaje_pv": 12.5,
        "corriente_pv": 1.2,
        "soc": 85.0,
        "temperatura": 28.0,
        "potencia_carga": 15.2,
        "relay_estado": 1,
    }

    # Simular que no hay conexión a DB
    with patch("src.backend.database.db.get_conn", return_value=None):
        try:
            guardar_telemetria(muestra)
            ok = True
        except Exception:
            ok = False

        assert ok is True  # No debe petar sin DB


def test_db_obtener_historico_sin_db():
    # Sin DB debe devolver lista vacía, NO lanzar excepción
    with patch("src.backend...database.db.get_conn", return_value=None):
        rows = obtener_historico(10)
        assert isinstance(rows, list)
