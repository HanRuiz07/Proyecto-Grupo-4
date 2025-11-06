#Graficos

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def render_graficos():
    """
    Muestra gráficos en tiempo real simulando variables de la microred.
    Incluye voltaje, corriente, potencia y estado de batería.
    """
    st.subheader("📊 Monitoreo de Variables del Sistema")

    # Generar datos simulados (para pruebas sin Raspberry ni Simulink)
    tiempo = pd.date_range(datetime.now() - timedelta(minutes=10), periods=100, freq="6S")
    voltaje = 24 + 2 * np.sin(np.linspace(0, 6, 100))
    corriente = 5 + 0.5 * np.cos(np.linspace(0, 4, 100))
    potencia = voltaje * corriente / 100  # en W

    df = pd.DataFrame({
        "Tiempo": tiempo,
        "Voltaje (V)": voltaje,
        "Corriente (A)": corriente,
        "Potencia (W)": potencia
    })

    # Mostrar gráficos con Streamlit
    st.line_chart(df.set_index("Tiempo")[["Voltaje (V)", "Corriente (A)"]])
    st.line_chart(df.set_index("Tiempo")[["Potencia (W)"]])

    st.success("📡 Datos simulados correctamente — listos para integración futura.")