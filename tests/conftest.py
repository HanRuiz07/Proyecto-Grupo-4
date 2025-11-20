# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from src.backend.api import app    # <--- IMPORT CORRECTO


@pytest.fixture(scope="session")
def client():
    """
    Cliente HTTP para pruebas de integración sobre la API FastAPI.
    Se crea una sola vez por sesión de tests.
    """
    return TestClient(app)
