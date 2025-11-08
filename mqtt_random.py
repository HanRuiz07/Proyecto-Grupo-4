import paho.mqtt.client as mqtt
import random
import time

# Configuración del broker
broker_ip = "192.168.137.1"   # IP de tu PC donde corre Mosquitto
port = 1883
topic = "prueba/mensaje"

# Crear cliente MQTT
client = mqtt.Client()
client.connect(broker_ip, port, 60)

# Loop infinito enviando números aleatorios
try:
    while True:
        # Generar un número aleatorio entre 0 y 100
        numero = random.randint(0, 100)
        
        # Publicar en el tópico
        client.publish(topic, numero)
        print(f"Enviado: {numero}")
        
        # Esperar 1 segundo
        time.sleep(1)

except KeyboardInterrupt:
    print("Programa terminado")
    client.disconnect()
