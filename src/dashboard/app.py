# Dashboard principal con Streamlit
import sys, os, time, csv
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from threading import Thread
import paho.mqtt.client as mqtt
from datetime import datetime

# --- Rutas ---
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_src = os.path.abspath(os.path.join(ruta_actual, ".."))
if ruta_src not in sys.path:
    sys.path.append(ruta_src)

# --- Importaciones locales ---
from componentes.header import render_header
from componentes.estado_panel import render_estado_panel
from componentes.graficos import render_graficos
from modelos.cargar_modelo import predecir
from mqtt.client_mqtt import MQTTClient

# ------------------------------
# Configuración general
# ------------------------------
st.set_page_config(
    page_title="Dashboard IoT + ML — Microred Inteligente",
    page_icon="🌞",
    layout="wide"
)

# ------------------------------
# Rutas del archivo CSV temporal
# ------------------------------
csv_path = os.path.join(ruta_actual, "data_mqtt.csv")

# Crear archivo CSV si no existe
if not os.path.exists(csv_path):
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Tiempo", "Valor"])

# ------------------------------
# MQTT - Funciones y callbacks
# ------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado al broker MQTT remoto")
        client.subscribe("prueba/mensaje")
    else:
        print(f"❌ Error de conexión MQTT: código {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode().strip()
        valor = float(payload)
        tiempo = datetime.now().strftime("%H:%M:%S")
        print(f"📩 MQTT recibido: {valor}")

        # Guardar en CSV
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([tiempo, valor])

        # Mantener solo los últimos 100 registros
        df = pd.read_csv(csv_path)
        if len(df) > 100:
            df.tail(100).to_csv(csv_path, index=False)
    except Exception as e:
        print("⚠️ Error procesando mensaje:", e)

def iniciar_mqtt_en_hilo():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("172.232.188.183", 1883, 60)
    client.loop_forever()

# Lanzar hilo MQTT si no está activo
if "mqtt_realtime_started" not in st.session_state:
    hilo_mqtt = Thread(target=iniciar_mqtt_en_hilo, daemon=True)
    hilo_mqtt.start()
    st.session_state["mqtt_realtime_started"] = True
    print("🧵 Hilo MQTT iniciado para recibir datos en tiempo real.")

# ------------------------------
# Función principal del dashboard
# ------------------------------
def main():
    render_header()
    st.markdown("## 🔘 Acciones del sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📊 Modelo Predictivo")
        temperatura = st.number_input("Temperatura (°C)", 0.0, 100.0, 25.0)
        humedad = st.number_input("Humedad (%)", 0.0, 100.0, 50.0)

        if st.button("🔮 Ejecutar modelo ML"):
            try:
                pred = predecir(temperatura, humedad)
                st.success(f"Predicción del modelo: {pred}")
                st.session_state["ultima_prediccion"] = pred
            except Exception as e:
                st.error(f"Error al ejecutar el modelo: {e}")

    with col2:
        st.subheader("⚙️ Gemelo Digital (Simulink)")
        if st.button("Enviar datos al Gemelo Digital"):
            st.success("Datos enviados al Gemelo Digital (simulado).")

    with col3:
        st.subheader("📡 Comunicación Raspberry Pi (MQTT)")
        if st.button("Transmitir al Raspberry"):
            if "ultima_prediccion" in st.session_state:
                mensaje = f"{temperatura},{humedad},{st.session_state['ultima_prediccion']}"
                mqtt_client = MQTTClient(broker="172.232.188.183", port=1883, topic="raspberry/microred")
                mqtt_client.publicar("raspberry/microred", mensaje)
                st.success("Datos transmitidos al Raspberry ✅")
            else:
                st.warning("Primero ejecuta el modelo para obtener una predicción.")

    st.divider()
    render_estado_panel()
    render_graficos()

    # ----- Sección de datos MQTT en tiempo real -----
    st.subheader("📈 Datos en tiempo real desde Raspberry")

    # Refrescar cada segundo
    st_autorefresh(interval=1000, key="auto_refresh_mqtt")

    # Leer datos del CSV
    try:
        df = pd.read_csv(csv_path)
        if not df.empty:
            st.line_chart(df.set_index("Tiempo"))
        else:
            st.info("Esperando datos MQTT...")
    except Exception as e:
        st.error(f"Error leyendo CSV: {e}")

# ------------------------------
# Ejecución principal
# ------------------------------
if __name__ == "__main__":
    main()
