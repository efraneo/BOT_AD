import streamlit as st
from config import Config
from utils import mostrar_alerta

def mostrar():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""<div class="main-title" style="margin-top:80px;"><h1>🛂 Acceso Garita / SST</h1><p>Ingreso exclusivo para control vehicular</p></div>""", unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        with st.form("form_garita"):
            email = st.text_input("📧 Usuario", placeholder="porteria@empresa.com")
            pwd = st.text_input("🔑 Contraseña", type="password")
            if st.form_submit_button("Ingresar al Punto de Control", use_container_width=True):
                if email in Config.GARITA_USERS and Config.GARITA_USERS[email] == pwd:
                    st.session_state["garita_autenticado"] = True; st.rerun()
                else: mostrar_alerta("danger", "Credenciales incorrectas.")
        if st.button("← Volver al inicio", use_container_width=True):
            st.session_state.pop("modo", None); st.rerun()
