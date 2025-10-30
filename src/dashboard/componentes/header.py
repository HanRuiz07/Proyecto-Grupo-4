import streamlit as st
from datetime import datetime

def render_header():
    """
    Encabezado del dashboard con el título, hora actual y controles principales.
    """
    # Título principal
    st.title("🌞 Automatizacion de Microred — Gemelo Digital + ML")

    # Mostrar hora actual
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("Proyecto de Automatización y Reutilización de Software")
        st.caption("Visualización en tiempo real de la microred fotovoltaica.")
    with col2:
        st.metric(label="Hora Actual", value=datetime.now().strftime("%H:%M:%S"))

    # Separador
    st.divider()

    # Controles básicos
    st.subheader("⚙️ Controles del Sistema")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("🔄 Actualizar Datos")
    with col2:
        st.button("🧠 Entrenar Nuevo Modelo ML")
    with col3:
        st.button("🚨 Simular Emergencia")

    st.divider()