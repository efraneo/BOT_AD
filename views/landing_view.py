import streamlit as st

def mostrar():
    st.markdown("""
    <div class="main-title" style="margin-top:40px;">
        <h1>🚗 Sistema SOAT</h1>
        <p>Clínica San Rafael Alta Complejidad SAS</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: st.markdown("")
    with c2:
        st.markdown("""<div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border-radius:16px; padding:24px; text-align:center; border:2px solid #a5d6a7; margin-bottom:16px;"><div style="font-size:40px;">👷</div><h3 style="color:#1b5e20; margin:4px 0;">Trabajador</h3></div>""", unsafe_allow_html=True)
        if st.button("👷 Ingresar", use_container_width=True, type="primary"): st.session_state["modo"] = "registro"; st.rerun()

        st.markdown("""<div style="background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-radius:16px; padding:24px; text-align:center; border:2px solid #ffcc80; margin-bottom:16px;"><div style="font-size:40px;">🛂</div><h3 style="color:#e65100; margin:4px 0;">Garita/SST</h3></div>""", unsafe_allow_html=True)
        if st.button("🛂 Ingresar", use_container_width=True): st.session_state["modo"] = "garita"; st.rerun()

        st.markdown("""<div style="background: linear-gradient(135deg, #e8eaf6, #c5cae9); border-radius:16px; padding:24px; text-align:center; border:2px solid #9fa8da;"><div style="font-size:40px;">🔐</div><h3 style="color:#1a237e; margin:4px 0;">Admin</h3></div>""", unsafe_allow_html=True)
        if st.button("🔐 Ingresar", use_container_width=True): st.session_state["modo"] = "admin"; st.rerun()
    with c3: st.markdown("")
