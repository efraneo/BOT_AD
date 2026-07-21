import streamlit as st
from config import Config
from styles import cargar_estilos
from views.landing_view import mostrar as pantalla_seleccion
from views.login_view import mostrar as pantalla_login
from views.registro_view import mostrar as pantalla_registro
from views.admin_view import mostrar as pantalla_admin
from views.garita_login_view import mostrar as pantalla_garita_login
from views.garita_view import mostrar as pantalla_garita

st.set_page_config(page_title="Sistema de Registro SOAT", page_icon="🚗", layout="wide", initial_sidebar_state="collapsed")
cargar_estilos()

def main():
    if not Config.validar():
        st.error("## ⚠️ Configuración Incompleta\nFalta configurar variables en Streamlit Secrets o `claves_soat.env`.")
        st.stop()

    if st.session_state.get("admin_autenticado"): pantalla_admin()
    elif st.session_state.get("garita_autenticado"): pantalla_garita()
    elif st.session_state.get("modo") == "admin": pantalla_login()
    elif st.session_state.get("modo") == "garita": pantalla_garita_login()
    elif st.session_state.get("modo") == "registro": pantalla_registro()
    else: pantalla_seleccion()

if __name__ == "__main__":
    main()
