# Panel de estado del sistema

import streamlit as st

def render_estado_panel():
    """
    Muestra el estado general del sistema en el panel principal.
    Incluye información de la microred, batería y alertas.
    """
    st.subheader("⚙️ Estado General del Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Potencia PV", value="250 W", delta="+5 W")

    with col2:
        st.metric(label="Estado Batería", value="85%", delta="-2%")

    with col3:
        st.metric(label="Controlador", value="Activo", delta="")

    st.divider()

    st.info("✅ Sistema funcionando dentro de parámetros normales.")
    st.warning("⚠️ Nivel de batería bajo, considerar recarga pronto.")