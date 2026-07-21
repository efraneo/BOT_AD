import base64
import streamlit as st
from config import Config
from utils import db, email_svc, mostrar_alerta

def _leer_placa_ia(foto_bytes):
    try:
        import openai, re
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        b64 = base64.b64encode(foto_bytes).decode("utf-8")
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "Extrae la placa colombiana (ABC123 o ABC12D). SOLO la placa, sin puntos. Si no hay, devuelve: NO_DETECTADA"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"}}
            ]}],
            max_tokens=10
        )
        placa = resp.choices[0].message.content.strip().upper()
        if placa == "NO_DETECTADA": return None
        placa = re.sub(r'[^A-Z0-9]', '', placa)
        return placa if len(placa) in (6, 7) and re.match(r'^[A-Z]{3}\d{2,3}[A-Z]?$', placa) else None
    except Exception as e:
        print(f"Error OpenAI: {e}"); return None

def _consultar_runt(placa: str):
    mostrar_alerta("info", "🔄 Consultando RUNT...")
    datos_interno = db.buscar_por_placa(placa)
    if datos_interno and datos_interno.get("soat_estado") == "Vigente":
        return {"exito": True, "mensaje": "Vehículo con SOAT Vigente en nuestra BD."}
    return {"exito": False, "mensaje": "El RUNT bloqueó la consulta automática. Verifique en www.runt.com.co"}

def mostrar():
    # NAVEGACIÓN
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Inicio", use_container_width=True): st.session_state.clear(); st.rerun()
    with c2:
        if st.button("🚪 Salir", use_container_width=True): st.session_state["garita_autenticado"] = False; st.rerun()

    st.markdown("""<div class="main-title"><h1>🧠 Escáner IA</h1></div>""", unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # RUNT
    with st.expander("🔍 RUNT (Opcional)"):
        c_r1, c_r2 = st.columns(2)
        placa_r = c_r1.text_input("🚘 Placa", placeholder="ABC123", key="pl_runt").upper().strip()
        cedula_r = c_r2.text_input("🪪 Cédula", placeholder="Opcional", key="ced_runt")
        if st.button("📡 Consultar", use_container_width=True):
            if placa_r:
                res = _consultar_runt(placa_r)
                mostrar_alerta("success" if res["exito"] else "warning", res["mensaje"])
            else: mostrar_alerta("danger", "Digite placa.")
    st.markdown("<hr>", unsafe_allow_html=True)

    # ESCÁNER
    foto = st.camera_input("📸 Placa", key="cam_garita")
    placa_det = ""
    if foto:
        with st.spinner("🧠 Leyendo..."): placa_det = _leer_placa_ia(foto.getvalue()) or ""
        st.markdown("---")
        placa_final = st.text_input("🔑 Placa", value=placa_det, placeholder="Corrija si es necesario", key="pl_gar", max_chars=7).upper().strip()
        if st.button("🛂 Consultar", use_container_width=True, type="primary"):
            if placa_final: _ejecutar(placa_final)
            else: mostrar_alerta("warning", "Ingrese placa.")
    else:
        st.info("📡 Tome foto a la placa.")
        st.markdown("---")
        placa_man = st.text_input("⌨️ Manual", placeholder="ABC123", key="pl_man", max_chars=7).upper().strip()
        if st.button("Consultar", use_container_width=True):
            if placa_man: _ejecutar(placa_man)

def _ejecutar(placa):
    with st.spinner("⏳ Consultando..."): datos = db.buscar_por_placa(placa)
    nombre = datos.get("nombres", "NO REGISTRADO") if datos else "NO REGISTRADO"
    cargo = datos.get("cargo", "N/A") if datos else "N/A"
    correo = datos.get("correo", "") if datos else ""
    estado = datos.get("soat_estado", "No Registrado") if datos else "No Registrado"
    
    db.registrar_ingreso_garita(placa, nombre, cargo, estado, correo)
    st.markdown("<br>", unsafe_allow_html=True)

    if estado == "Vigente":
        st.markdown(f"""<div style="background: linear-gradient(135deg, #2e7d32, #1b5e20); padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(46, 125, 50, 0.4); margin: 20px 0;"><div style="font-size: 80px;">✅</div><h1 style="color: white; margin: 0; font-size: 2.5rem;">APROBADO</h1><h2 style="color: rgba(255,255,255,0.9); margin: 10px 0; font-size: 1.8rem;">{placa}</h2><p style="color: rgba(255,255,255,0.8); font-size: 1.2rem;">SOAT VIGENTE</p></div>""", unsafe_allow_html=True)
        with st.expander("📋 Info"): st.markdown(f"**Nombre:** {nombre}\n**Cargo:** {cargo}")
    else:
        motivo = {"No Registrado": "NO REGISTRADO", "Vencido": "VENCIDO", "No legible": "NO LEGIBLE", "Por vencer": "POR VENCER"}.get(estado, estado.upper())
        st.markdown(f"""<div style="background: linear-gradient(135deg, #c62828, #b71c1c); padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(198, 40, 40, 0.4); margin: 20px 0;"><div style="font-size: 80px;">🚨</div><h1 style="color: white; margin: 0; font-size: 2.5rem;">SIN SOAT</h1><h2 style="color: rgba(255,255,255,0.9); margin: 10px 0; font-size: 1.8rem;">{placa}</h2><p style="color: rgba(255,255,255,0.8); font-size: 1.2rem; background:rgba(0,0,0,0.2); display:inline-block; padding:5px 15px; border-radius:8px;">{motivo}</p></div>""", unsafe_allow_html=True)
        with st.expander("📋 Info"): st.markdown(f"**Nombre:** {nombre}\n**Cargo:** {cargo}")
        mostrar_alerta("danger", "⚠️ RESTRINGIDO.")
        if correo and estado != "No Registrado":
            with st.spinner("📧 Enviando correo..."):
                email_svc.enviar_alerta_sst_ingreso(correo, nombre, placa, motivo)
            mostrar_alerta("info", "📧 Notificación enviada.")
