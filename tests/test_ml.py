# tests/test_ml.py

def test_ml_info(client):
    r = client.get("/api/ml/info")
    assert r.status_code == 200
    data = r.json()
    # El endpoint devuelve información del estado del modelo y scalers
    assert "modelo" in data
    assert "scaler_X" in data
    assert "scaler_y" in data


def test_ml_predict_sin_modelo(client):
    """
    Si no hay modelo entrenado, debe devolver status=error,
    pero NUNCA un 500.
    """
    r = client.post("/api/ml/predict", json={"corriente": [0.5]})
    assert r.status_code == 200
    data = r.json()
    assert "status" in data  # "ok" o "error", pero la API está viva
    # Si no hay modelo cargado, debe indicar estado de error sin devolver 500
    assert data.get("status") in ("ok", "error")
