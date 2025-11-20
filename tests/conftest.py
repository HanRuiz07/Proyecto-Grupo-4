# tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient

# Forzar modo TESTING durante la ejecución de la suite para evitar cargas
# pesadas (TensorFlow) en los imports del módulo ML
os.environ.setdefault("TESTING", "1")

from src.backend.api import app    # <--- IMPORT CORRECTO


@pytest.fixture(scope="session")
def client():
    """
    Cliente HTTP para pruebas de integración sobre la API FastAPI.
    Se crea una sola vez por sesión de tests.
    """
    return TestClient(app)
