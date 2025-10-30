import streamlit as st
from modelos.Modelo2 import predecir

def render_acciones():
    st.subheader("🔘 Acciones del sistema")

    temperatura = st.number_input("Temperatura (°C)", 0.0, 100.0, 25.0)
    humedad = st.number_input("Humedad (%)", 0.0, 100.0, 50.0)

    if st.button("🔮 Ejecutar modelo predictivo"):
        pred = predecir(temperatura, humedad)
        st.success(f"Predicción del modelo: {pred}")
        st.session_state["ultima_prediccion"] = pred

    if st.button("⚙️ Enviar al Gemelo Digital"):
        st.info("Enviando datos a Simulink... (simulado)")
        # Aquí luego puedes usar un archivo CSV o MQTT para comunicarte

    if st.button("📡 Enviar al Raspberry Pi"):
        st.info("Transmisión al Raspberry en curso... (simulado)")
