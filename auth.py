import streamlit as st
import database as db
from datetime import datetime

def show_auth():
    st.markdown("<h1 style='text-align: center;'>🔒 Acceso al Bot Premium</h1>", unsafe_allow_html=True)
    st.write("Por favor, inicia sesión o regístrate para continuar.")
    
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registro (3 Días Gratis)"])
    
    with tab1:
        with st.form("login_form"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Clave", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                user = db.verify_login(usuario, clave)
                if user:
                    if user[11] == 'pendiente':
                        st.warning("Tu cuenta está en espera de aprobación por el Administrador.")
                    elif user[11] == 'rechazado':
                        st.error("Tu cuenta ha sido rechazada. Contacta al administrador.")
                    elif user[11] == 'aprobado':
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        db.update_login_stats(usuario)
                        st.success("¡Bienvenido de nuevo!")
                        st.rerun()
                else:
                    st.error("Usuario o clave incorrectos.")

    with tab2:
        with st.form("register_form"):
            identificacion = st.text_input("Identificación (Cédula)")
            usuario = st.text_input("Usuario deseado")
            correo = st.text_input("Correo electrónico")
            fecha_nac = st.date_input("Fecha de Nacimiento", min_value=datetime(1950, 1, 1)).strftime("%Y-%m-%d")
            clave = st.text_input("Crea una clave", type="password")
            submit = st.form_submit_button("Registrarme")
            
            if submit:
                if db.register_user(identificacion, usuario, clave, correo, fecha_nac):
                    st.success("¡Registro exitoso! Tienes 3 días de prueba. El administrador debe aprobar tu cuenta para uso a largo plazo.")
                else:
                    st.error("El usuario o identificación ya existe.")
