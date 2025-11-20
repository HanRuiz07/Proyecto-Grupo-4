# tests/test_modo_automatico.py

def test_modo_automatico_on(client):
    r = client.post("/api/modo/automatico/on")
    assert r.status_code == 200
    # Solo comprobamos que no rompe; el contenido depende de tu lógica interna
    assert isinstance(r.json(), dict)


def test_modo_automatico_off(client):
    r = client.post("/api/modo/automatico/off")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)
