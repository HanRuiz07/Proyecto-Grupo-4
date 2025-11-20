# tests/test_mqtt.py
from src.backend.mqtt.cliente import enviar_comando_mqtt

def test_mqtt_enviar_comando_no_revienta():
    """
    Solo valida que la llamada no lanza excepción
    aunque no haya broker MQTT disponible.
    """
    try:
        enviar_comando_mqtt("relay_on")
        ok = True
    except Exception:
        ok = False

    assert ok is True

