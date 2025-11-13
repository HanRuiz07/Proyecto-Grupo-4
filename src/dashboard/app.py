# Dashboard principal con Streamlit
import sys
import os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../ModelPredict")))

# --- Asegurar que Python vea la carpeta raíz 'src' ---
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_src = os.path.abspath(os.path.join(ruta_actual, ".."))
if ruta_src not in sys.path:
    sys.path.append(ruta_src)


import streamlit as st
from componentes.header import render_header
from componentes.estado_panel import render_estado_panel
from componentes.graficos import render_graficos
from ModelPredict.Modelo2 import cargar_datos, predecir  # ← integración del modelo ML

# ------------------------------
# Configuración general del dashboard
# ------------------------------
st.set_page_config(
    page_title="Dashboard IoT + ML — Microred Inteligente",
    page_icon="🌞",
    layout="wide"
)

# ------------------------------
# Estructura principal
# ------------------------------
def main():
    """es el main ps"""
    # Cabecera
    render_header()

    # ---- Sección de acciones (botones del modelo, gemelo digital, Raspberry)
    st.markdown("## 🔘 Acciones del sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📊 Modelo Predictivo")
        st.write("Introduce los últimos 5 valores de corriente obtenidos")

        i_post4 = st.number_input("Corriente actual", value=1.0)
        i_post = st.number_input("Corriente 2 minutos antes", value=1.0)
        i = st.number_input("Corriente 4 minutos antes", value=1.0)
        i_prev = st.number_input("Corriente 6 minutos antes", value=1.0)
        i_prev4 = st.number_input("Corriente 8 minutos antes", value=1.0)

        tiempo = st.number_input("Tiempo", value=5.0)

        nuevos_valores = np.array([[i, i_prev, i_prev4, i_post4, i_post, tiempo]])

        if st.button("🔮 Ejecutar modelo ML"):
            try:
                pred = predecir(nuevos_valores)
                st.success(f"Predicción del modelo: {pred}")
                st.session_state["ultima_prediccion"] = pred
            except Exception as e:
                st.error(f"Error al ejecutar el modelo: {e}")
        else:
            st.info("Introduce los valores y presiona el botón para predecir.")

    with col2:
        st.subheader("⚙️ Gemelo Digital (Simulink)")
        if st.button("Enviar datos al Gemelo Digital"):
            st.info("Simulando envío de datos a Simulink...")
            # TODO: Aquí podrás exportar CSV o JSON para Simulink
            # Ejemplo:
            # with open("src/data/simulink_input.csv", "w") as f:
            #     f.write(f"temperatura,humedad,prediccion\n{temperatura},{humedad},{pred}")
            st.success("Datos enviados al Gemelo Digital (simulado).")

    with col3:
        st.subheader("📡 Comunicación Raspberry Pi")
        if st.button("Transmitir al Raspberry"):
            st.info("Simulando transmisión de datos al Raspberry Pi...")
            # TODO: Aquí podrás implementar MQTT o HTTP
            # Ejemplo:
            # mqtt.publish("raspberry/topic", json.dumps({"temp": temperatura, "humedad": humedad, "pred": pred}))
            st.success("Datos transmitidos al Raspberry (simulado).")

    st.divider()

    # ---- Panel de estado (sistema, batería, control)
    render_estado_panel()

    # ---- Gráficos principales (potencia, irradiancia, predicción)
    render_graficos()


# ------------------------------
# Ejecución principal
# ------------------------------
if __name__ == "__main__":
    main()
