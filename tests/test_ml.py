# tests/test_ml.py

def test_ml_info(client):
    r = client.get("/api/ml/info")
    assert r.status_code == 200
    data = r.json()
    assert "modelo" in data
    assert "existe" in data
    assert "path" in data


def test_ml_predict_sin_modelo(client):
    """
    Si no hay modelo entrenado, debe devolver status=error,
    pero NUNCA un 500.
    """
    r = client.post("/api/ml/predict", json={"corriente": [0.5]})
    assert r.status_code == 200
    data = r.json()
    assert "status" in data  # "ok" o "error", pero la API está viva
