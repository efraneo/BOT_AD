import streamlit as st
from config import Config
from utils import mostrar_alerta

def mostrar():
    if st.button("🏠 Volver al Menú", use_container_width=True): st.session_state.pop("modo", None); st.rerun()

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("""<div class="main-title" style="margin-top:80px;"><h1>🛂 Garita</h1><p>Control vehicular</p></div>""", unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        with st.form("f_garita"):
            email = st.text_input("📧 Usuario")
            pwd = st.text_input("🔑 Clave", type="password")
            if st.form_submit_button("Ingresar", use_container_width=True):
                if email in Config.GARITA_USERS and Config.GARITA_USERS[email] == pwd:
                    st.session_state["garita_autenticado"] = True; st.rerun()
                else: mostrar_alerta("danger", "Credenciales incorrectas.")
