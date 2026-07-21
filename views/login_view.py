import streamlit as st
from config import Config
from utils import mostrar_alerta

def mostrar():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""<div class="main-title" style="margin-top:80px;"><h1>🔐 Acceso Administrador</h1><p>Ingresa tus credenciales</p></div>""", unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        with st.form("form_login"):
            email = st.text_input("📧 Correo", placeholder="admin@empresa.com")
            password = st.text_input("🔑 Contraseña", type="password")
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                if email == Config.ADMIN_EMAIL and password == Config.ADMIN_PASSWORD:
                    st.session_state["admin_autenticado"] = True; st.rerun()
                else: mostrar_alerta("danger", "Credenciales incorrectas.")
        if st.button("← Volver", use_container_width=True):
            st.session_state.pop("modo", None); st.rerun()
