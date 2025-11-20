# tests/test_websocket.py
from fastapi.testclient import TestClient
from src.backend.api import app

client = TestClient(app)

def test_websocket_live():
    # Verifica que el WS acepte conexión en modo testing
    with client.websocket_connect("/api/live") as ws:
        data = ws.receive_json()
        assert data["tipo"] == "test"
        assert data["msg"] == "ok"