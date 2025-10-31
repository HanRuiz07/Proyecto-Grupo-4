# client_mqtt.py
import paho.mqtt.client as mqtt
import json

class MQTTClient:
    def __init__(self, broker="192.168.137.1", port=1883, topic="prueba/mensaje"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.ultimo_mensaje = ""
        self.conectado = False

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        self.conectado = True
        print(f"✅ Conectado a {self.broker}:{self.port}")
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode().strip()
        self.ultimo_mensaje = payload
        print(f"📨 Mensaje recibido en {msg.topic}: {payload}")

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()  # 🚀 No bloquea la app

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

