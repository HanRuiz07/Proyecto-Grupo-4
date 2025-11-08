import paho.mqtt.client as mqtt
import pandas as pd
import time
import json
import csv
from smbus2 import SMBus

# ================================
# CONFIGURACIÓN DEL INA226
# ================================

DEVICE_ADDR = 0x40              # Dirección I2C del INA226
I_max = 2                       # Corriente máxima esperada (A)
I_lsb = I_max / 32768           # Corriente por bit (A/LSB)
R_shunt = 0.01                  # Resistencia de shunt (ohmios)
CALIBRATION = 0.00512 / (I_lsb * R_shunt)  # Valor de calibración
data_csv = 'data_csv.csv'
#================================
#CONFIGURACION GUARDAR CSV
#================================

with open(data_csv, "a", newline="") as f:
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow(["Tiempo", "V_bus (V)", "V_shunt (V)", "Corriente (A)"])

# ================================
# CONFIGURACIÓN DEL BROKER MQTT
# ================================

broker_ip = "172.232.188.183"
port = 1883
topic = "prueba/mensaje"

client = mqtt.Client()
client.username_pw_set("is-han.ruiz.e@uni.eudr", "123456788")
client.connect(broker_ip, port, 60)

# ================================
# CONFIGURACIÓN I2C (INA226)
# ================================

bus = SMBus(1)

# Escribir configuración (0x00) - modo continuo bus+shunt
bus.write_word_data(DEVICE_ADDR, 0x00, 0x4777)

# Corregir endianness del valor de calibración
value = ((int(CALIBRATION) >> 8) | ((int(CALIBRATION) & 0xFF) << 8))  # De Big Endian a Little Endian

# Escribir calibración (0x05)
bus.write_word_data(DEVICE_ADDR, 0x05, value)  # Hace la configuración de la escala

# ================================
# ENVÍO DE DATOS DESDE CSV POR MQTT
# ================================

csv_path = "Data/Libro1.csv"
df = pd.read_csv(csv_path, header=None, sep=',')

try:
    while True:
        '''
        for _, fila in df.iterrows():
            current = fila[0]

            mensaje = {
                "Corriente": fila[0],
                "Tiempo Actual": fila[1],
                "Tiempo para Pico": fila[2]
            }

            mensaje_json = json.dumps(mensaje)
            client.publish(topic, mensaje_json)
            print(f"Enviado: {mensaje_json}")

            # Esperar 1 segundo antes de enviar el siguiente valor
            time.sleep(1)
        '''

        # --- Lectura de voltaje del bus (registro 0x02) ---
        V_bus_reg = bus.read_word_data(DEVICE_ADDR, 0x02)

        # Intercambiar bytes y convertir a voltaje real
        V_bus = ((V_bus_reg & 0xFF) << 8) | (V_bus_reg >> 8)
        V_bus = V_bus * 1.25e-3  # LSB = 1.25 mV
        
        V_shunt_reg = bus.read_word_data(DEVICE_ADDR, 0x01)
        V_shunt = ((V_shunt_reg & 0xFF) << 8) | (V_shunt_reg >> 8)

        if V_shunt > 32767:
            V_shunt = V_shunt -65536
        
        V_shunt = V_shunt * 2.5e-3 #LSB= 2.5uA

        I_shunt= V_shunt / R_shunt

        print(f"Tensión del bus: {V_bus:.3f} V")
        print(f"Voltaje de Shunt: {V_shunt:.3f} mV")
        print(f"Corriente de Shunt: {I_shunt:.3f} mA")
        print("-------------------------------------------")
        
        with open(data_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time.strftime("%H:%M:%S"), V_bus, I_shunt])

        time.sleep(0.10)
except KeyboardInterrupt:
    print("Programa terminado")
    client.disconnect()
