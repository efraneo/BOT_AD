import streamlit as st

def mostrar():
    st.markdown("""
    <div class="main-title" style="margin-top:40px;">
        <h1>🚗 Sistema de Registro SOAT</h1>
        <p>Control vehicular empresarial — Selección de acceso</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1: st.markdown("")
    with col2:
        st.markdown("""<div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border-radius:16px; padding:24px; text-align:center; border:2px solid #a5d6a7; margin-bottom:16px; box-shadow: 0 4px 16px rgba(46,125,50,0.1);"><div style="font-size:40px; margin-bottom:4px;">👷</div><h3 style="color:#1b5e20; margin:0 0 4px;">Trabajador</h3><p style="color:#2e7d32; font-size:12px; margin:0;">Registro de datos y SOAT</p></div>""", unsafe_allow_html=True)
        if st.button("👷 Ingresar como Trabajador", use_container_width=True, type="primary"):
            st.session_state["modo"] = "registro"; st.rerun()

        st.markdown("""<div style="background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-radius:16px; padding:24px; text-align:center; border:2px solid #ffcc80; margin-bottom:16px; box-shadow: 0 4px 16px rgba(239,108,0,0.1);"><div style="font-size:40px; margin-bottom:4px;">🛂</div><h3 style="color:#e65100; margin:0 0 4px;">Punto de Control (Garita)</h3><p style="color:#ef6c00; font-size:12px; margin:0;">Escáner de placas y validación</p></div>""", unsafe_allow_html=True)
        if st.button("🛂 Acceso Garita / SST", use_container_width=True):
            st.session_state["modo"] = "garita"; st.rerun()

        st.markdown("""<div style="background: linear-gradient(135deg, #e8eaf6, #c5cae9); border-radius:16px; padding:24px; text-align:center; border:2px solid #9fa8da; box-shadow: 0 4px 16px rgba(26,35,126,0.1);"><div style="font-size:40px; margin-bottom:4px;">🔐</div><h3 style="color:#1a237e; margin:0 0 4px;">Administrador</h3><p style="color:#283593; font-size:12px; margin:0;">Panel de indicadores y gestión</p></div>""", unsafe_allow_html=True)
        if st.button("🔐 Ingresar como Administrador", use_container_width=True):
            st.session_state["modo"] = "admin"; st.rerun()
    with col3: st.markdown("")
