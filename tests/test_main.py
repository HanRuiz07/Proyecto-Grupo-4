# tests/test_main.py

def test_openapi_disponible(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "paths" in data
    assert "/api/estado" in data["paths"]
