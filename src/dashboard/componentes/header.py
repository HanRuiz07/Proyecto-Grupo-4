import os
import joblib
import streamlit as st
from datetime import datetime
from ModelPredict.Modelo2 import entrenar_modelo, cargar_datos, guardar_modelo, grafica_datos

def render_header():
    """
    Encabezado del dashboard con el título, hora actual y controles principales.
    """
    archivo = st.file_uploader("Seleccione su archivo csv", type = "csv")

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
        if st.button("🔄 Actualizar Datos"):
            dataset = None

            if archivo is None:
                st.error("No se puede cargar el archivo CSV. Revise la selección.")
            else:
                dataset = cargar_datos(archivo)

            if dataset is not None:
                st.success("Archivo cargado exitosamente")
                st.session_state["dataset"] = dataset
            else:
                st.error("No se pudo cargar el archivo")
    with col2:
        if st.button("🧠 Entrenar Nuevo Modelo ML"):
            umbral = st.number_input("Define el umbral de corriente para tu dispositivo", value=1.0)
            if "dataset" in st.session_state:
                model, scaler_x, scaler_y = entrenar_modelo(st.session_state["dataset"], umbral)
                st.session_state["modelo_entrenado"] = model
                guardar_modelo(st.session_state["modelo_entrenado"])
                st.success("Modelo entrenado y guardado")
            else:
                st.error("No hay un csv cargado")
    with col3: #Simular tu emergencia al poto ctmr
        st.button("Gráfica de datos")

        if "dataset" in st.session_state:
            grafica_datos(st.session_state["dataset"], umbral)


    st.divider()

