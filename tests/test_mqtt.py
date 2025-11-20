# tests/test_mqtt.py
from src.backend.mqtt.cliente import publicar_mqtt


def test_mqtt_enviar_comando_no_revienta():
    """
    Solo valida que la llamada no lanza excepción
    aunque no haya broker MQTT disponible.
    """
    try:
        publicar_mqtt("microrred/comando", {"comando": "relay_on"})
        ok = True
    except Exception:
        ok = False

    assert ok is True

