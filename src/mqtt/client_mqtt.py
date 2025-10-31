import paho.mqtt.client as mqtt
import threading

class MQTTClient:
    def __init__(self, broker="localhost", port=1883, topic="prueba/mensaje"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.ultimo_mensaje = None

        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ Conectado al broker {self.broker}:{self.port} (código {rc})")
        self.client.subscribe(self.topic)

    def on_message(client, userdata, msg):
        try:
            valor = float(msg.payload.decode().strip())
            nuevo_dato = pd.DataFrame({
                "Tiempo": [pd.Timestamp.now().strftime("%H:%M:%S")],
                "Valor": [valor]
            })

            # 👇 Prevención de error si el estado aún no existe
            if "data_mqtt" not in st.session_state:
                st.session_state["data_mqtt"] = pd.DataFrame(columns=["Tiempo", "Valor"])

            st.session_state["data_mqtt"] = pd.concat(
                [st.session_state["data_mqtt"], nuevo_dato],
                ignore_index=True
            ).tail(100)

            print(f"📩 MQTT recibido: {valor}")
        except Exception as e:
            print("⚠️ Error procesando mensaje:", e)


    def start(self):
        thread = threading.Thread(target=self._loop_forever, daemon=True)
        thread.start()

    def _loop_forever(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"❌ Error de conexión MQTT: {e}")

    def publicar(self, topic, mensaje):
        try:
            self.client.publish(topic, mensaje)
            print(f"📤 Publicado en {topic}: {mensaje}")
        except Exception as e:
            print(f"❌ Error al publicar en {topic}: {e}")
