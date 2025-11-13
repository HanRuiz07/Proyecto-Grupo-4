import os
import sys
import numpy as np
#import pandas as pd
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), "../../")))
from ModelPredict.Modelo2 import cargar_datos, predecir

def render_acciones():
    """
    Renderiza la sección de acciones del sistema en el dashboard.
    Permite cargar archivos CSV y ejecutar predicciones o entrenar el modelo ML.
    """
    st.subheader("🔘 Acciones del sistema")

    archivo = st.file_uploader("Seleccione su archivo csv", type = "csv")

    if st.button("Cargar archivo"):
        if archivo is None:
            st.error("No se puede cargar el archivo CSV. Revise la selección.")
        else:
            dataset = cargar_datos(archivo)

            if dataset is not None:
                st.success("Archivo cargado exitosamente")
                st.session_state["dataset"] = dataset
            else:
                st.error("No se pudo cargar el archivo")


    if st.button("🔮 Ejecutar modelo predictivo"):
        
        nuevos_valores = dataset[:, 2]
        
        pred = predecir(nuevos_valores)
        st.success(f"Predicción del modelo: {pred}")
        st.session_state["ultima_prediccion"] = pred

    if st.button("⚙ Enviar al Gemelo Digital"):
        st.info("Enviando datos a Simulink... (simulado)")
        # Aquí luego puedes usar un archivo CSV o MQTT para comunicarte

    if st.button("📡 Enviar al Raspberry Pi"):
        st.info("Transmisión al Raspberry en curso... (simulado)")
