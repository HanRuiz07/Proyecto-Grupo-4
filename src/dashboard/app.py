# Dashboard principal con Streamlit
import sys, os, time
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- Rutas ---
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_src = os.path.abspath(os.path.join(ruta_actual, ".."))
if ruta_src not in sys.path:
    sys.path.append(ruta_src)

# --- Importaciones ---
from componentes.header import render_header
from componentes.estado_panel import render_estado_panel
from componentes.graficos import render_graficos
from modelos.cargar_modelo import predecir
from mqtt.client_mqtt import MQTTClient  # 🔌 integración MQTT

# ------------------------------
# Configuración general
# ------------------------------
st.set_page_config(
    page_title="Dashboard IoT + ML — Microred Inteligente",
    page_icon="🌞",
    layout="wide"
)

# ------------------------------
# Inicializar cliente MQTT una sola vez
# ------------------------------
if "mqtt_client" not in st.session_state:
    st.session_state["mqtt_client"] = MQTTClient(
        broker="192.168.137.1",   # IP del broker (tu PC)
        topic="prueba/mensaje"
    )
    st.session_state["mqtt_client"].start()

mqtt_client = st.session_state["mqtt_client"]

# ------------------------------
# Inicializar DataFrame si no existe
# ------------------------------
if "data_mqtt" not in st.session_state:
    st.session_state["data_mqtt"] = pd.DataFrame(columns=["Tiempo", "Valor"])

# ------------------------------
# Función principal del dashboard
# ------------------------------
def main():
    render_header()
    st.markdown("## 🔘 Acciones del sistema")

    col1, col2, col3 = st.columns(3)

    # ----- Columna 1: Modelo ML -----
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

    # ----- Columna 2: Gemelo Digital -----
    with col2:
        st.subheader("⚙️ Gemelo Digital (Simulink)")
        if st.button("Enviar datos al Gemelo Digital"):
            st.info("Simulando envío de datos a Simulink...")
            st.success("Datos enviados al Gemelo Digital (simulado).")

    # ----- Columna 3: Comunicación Raspberry -----
    with col3:
        st.subheader("📡 Comunicación Raspberry Pi (MQTT)")
        if st.button("Transmitir al Raspberry"):
            if "ultima_prediccion" in st.session_state:
                mensaje = f"{temperatura},{humedad},{st.session_state['ultima_prediccion']}"
                mqtt_client.publicar("raspberry/microred", mensaje)
                st.success("Datos transmitidos al Raspberry ✅")
            else:
                st.warning("Primero ejecuta el modelo para obtener una predicción.")

    st.divider()

    render_estado_panel()
    render_graficos()

    # ----- Sección: Datos en tiempo real -----
    st.subheader("📈 Datos en tiempo real desde Raspberry")

    chart_placeholder = st.empty()

    # Leer mensaje MQTT si hay nuevos datos
    if mqtt_client.ultimo_mensaje:
        try:
            valor = float(mqtt_client.ultimo_mensaje.strip())
            nuevo_dato = pd.DataFrame({
                "Tiempo": [time.strftime("%H:%M:%S")],
                "Valor": [valor]
            })
            st.session_state["data_mqtt"] = pd.concat(
                [st.session_state["data_mqtt"], nuevo_dato],
                ignore_index=True
            ).tail(50)
        except ValueError:
            st.warning(f"Mensaje no numérico recibido: {mqtt_client.ultimo_mensaje}")

    # Mostrar gráfico actualizado
    chart_placeholder.line_chart(
        st.session_state["data_mqtt"].set_index("Tiempo"),
        height=300,
    )

    # ----- Auto refresco -----
    st.markdown("⏱️ Actualizando automáticamente cada 1 segundo...")
    st_autorefresh(interval=1000, key="auto_refresh_mqtt")


# ------------------------------
# Ejecución principal
# ------------------------------
if __name__ == "__main__":
    main()
