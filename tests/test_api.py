# tests/test_api.py

def test_api_estado(client):
    r = client.get("/api/estado")
    assert r.status_code == 200
    data = r.json()
    # Campos básicos del estado_sistema
    for key in ["voltaje_pv", "corriente_pv", "soc", "temperatura", "relay_estado"]:
        assert key in data


def test_api_historico(client):
    r = client.get("/api/historico")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_control_carga_on(client):
    r = client.post("/api/control/carga", json={"accion": "on"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["comando_enviado"] == "on"


def test_control_carga_off(client):
    r = client.post("/api/control/carga", json={"accion": "off"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_control_pv(client):
    r = client.post("/api/control/pv", json={"accion": "on"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_umbrales(client):
    payload = {"soc_min": 20, "soc_max": 90, "p_min": 0, "p_max": 100}
    r = client.post("/api/control/umbrales", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "umbrales_configurados"
    assert data["data"] == payload


def test_raspberry_telemetria(client):
    payload = {
        "timestamp": 1,
        "voltaje_pv": 10,
        "corriente_pv": 2,
        "soc": 90,
        "temperatura": 25,
        "potencia_carga": 0.4,
        "relay_estado": 1,
    }
    r = client.post("/api/raspberry/telemetria", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_simulink_estado(client):
    r = client.get("/api/simulink/estado")
    assert r.status_code == 200
    data = r.json()
    for key in ["vdc_sim", "soc_sim", "corriente_sim", "temperatura_sim"]:
        assert key in data
