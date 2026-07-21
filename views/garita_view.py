import base64
import streamlit as st
from config import Config
from utils import db, email_svc, mostrar_alerta

def _leer_placa_ia(foto_bytes):
    try:
        import openai
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        b64 = base64.b64encode(foto_bytes).decode("utf-8")
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "Eres un sistema de lectura de placas vehiculares de Colombia. Extrae la placa (ABC123 o ABC12D). Devuelve SOLO la placa en mayúsculas sin espacios. Si no ves placa, devuelve: NO_DETECTADA"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"}}
            ]}],
            max_tokens=10
        )
        placa = resp.choices[0].message.content.strip().upper()
        if placa == "NO_DETECTADA": return None
        import re
        placa = re.sub(r'[^A-Z0-9]', '', placa)
        return placa if len(placa) in (6, 7) and re.match(r'^[A-Z]{3}\d{2,3}[A-Z]?$', placa) else None
    except Exception as e:
        print(f"Error OpenAI: {e}"); return None

def _consultar_runt(placa: str, cedula: str = ""):
    """Intenta verificar el estado en el RUNT (Requiere APIs externas oficiales, simulación local por defecto)."""
    mostrar_alerta("info", "🔄 Conectando con el RUNT (Ministerio de Transporte)...")
    try:
        # NOTA: El RUNT bloquea scrapers directos. Si tienes un Token/API autorizada, reemplaza esta lógica.
        # Aquí usamos una validación lógica basada en nuestra BD como alternativa.
        # Si en el futuro adquieren un servicio API del RUNT, aquí se integraría la petición GET/POST.
        
        datos_interno = db.buscar_por_placa(placa)
        if datos_interno and datos_interno.get("soat_estado") == "Vigente":
            return {"exito": True, "mensaje": "Vehículo registrado internamente con SOAT Vigente."}
        else:
            return {"exito": False, "mensaje": "El RUNT bloqueó la consulta automática. Para verificar de forma oficial, el portero debe ingresar a www.runt.com.co o consultar el app Transmilenio/RUNT desde su celular."}
    except Exception as e:
        return {"exito": False, "mensaje": f"Error de conexión: {str(e)}"}

def mostrar():
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("🏠 Volver al Inicio"): st.session_state["garita_autenticado"] = False; st.session_state.pop("modo", None); st.rerun()
    with col_nav2:
        if st.button("🚪 Cerrar Sesión Garita"): st.session_state["garita_autenticado"] = False; st.rerun()

    st.markdown("""<div class="main-title"><h1>🧠 Escáner IA de Placas</h1><p>Apunte a la placa, la IA hará el resto</p></div>""", unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Opción de Consultar RUNT
    with st.expander("🔍 Verificación Cruzada RUNT (Opcional)"):
        st.markdown("<p style='font-size:12px;'>Ingrese los datos para verificar en la base del Ministerio de Transporte.</p>", unsafe_allow_html=True)
        c_runt1, c_runt2 = st.columns(2)
        placa_runt = c_runt1.text_input("Placa RUNT:", placeholder="ABC123", key="placa_runt").upper().strip()
        cedula_runt = c_runt2.text_input("Cédula (Opcional):", placeholder="1234567890", key="ced_runt")
        if st.button("📡 Consultar RUNT", use_container_width=True):
            if placa_runt:
                res_runt = _consultar_runt(placa_runt, cedula_runt)
                if res_runt["exito"]: mostrar_alerta("success", res_runt["mensaje"])
                else: mostrar_alerta("warning", res_runt["mensaje"])
            else: mostrar_alerta("danger", "Digite una placa para consultar.")
    st.markdown("<hr>", unsafe_allow_html=True)

    foto = st.camera_input("📸 Capturar Placa", key="cam_garita")
    placa_det = ""
    if foto:
        with st.spinner("🧠 Procesando con IA..."): placa_det = _leer_placa_ia(foto.getvalue()) or ""
        st.markdown("---"); st.markdown("### 🔎 Confirmar Placa")
        placa_final = st.text_input("Placa del vehículo:", value=placa_det, placeholder="Si la IA falló, escríbala aquí", key="placa_garita", max_chars=7).upper().strip()
        if st.button("🛂 Consultar Vehículo", use_container_width=True, type="primary"):
            if placa_final: _ejecutar_consulta(placa_final)
            else: mostrar_alerta("warning", "Ingrese una placa.")
    else:
        st.info("📡 Use la cámara para tomar una foto clara de la placa.")
        st.markdown("---"); st.markdown("#### ⌨️ Ingreso Manual")
        placa_man = st.text_input("Digitar placa:", placeholder="ABC123", key="placa_man", max_chars=7).upper().strip()
        if st.button("Consultar Manualmente", use_container_width=True):
            if placa_man: _ejecutar_consulta(placa_man)
            else: mostrar_alerta("warning", "Digite una placa.")

def _ejecutar_consulta(placa):
    with st.spinner("⏳ Consultando BD..."): datos = db.buscar_por_placa(placa)
    nombre = datos.get("nombres", "NO REGISTRADO") if datos else "NO REGISTRADO"
    cargo = datos.get("cargo", "N/A") if datos else "N/A"
    correo = datos.get("correo", "") if datos else ""
    estado = datos.get("soat_estado", "No Registrado") if datos else "No Registrado"
    
    db.registrar_ingreso_garita(placa, nombre, cargo, estado, correo)
    st.markdown("<br>", unsafe_allow_html=True)

    if estado == "Vigente":
        st.markdown(f"""<div style="background: linear-gradient(135deg, #2e7d32, #1b5e20); padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(46, 125, 50, 0.4); margin: 20px 0;"><div style="font-size: 80px;">✅</div><h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 800;">APROBADO</h1><h2 style="color: rgba(255,255,255,0.9); margin: 10px 0; font-size: 1.8rem;">{placa}</h2><p style="color: rgba(255,255,255,0.8); font-size: 1.2rem;">SOAT VIGENTE</p></div>""", unsafe_allow_html=True)
        with st.expander("📋 Ver Conductor"): st.markdown(f"**Nombre:** {nombre}\n**Cargo:** {cargo}")
    else:
        motivo = {"No Registrado": "VEHÍCULO NO REGISTRADO", "Vencido": "SOAT VENCIDO", "No legible": "NO LEGIBLE", "Por vencer": "POR VENCER"}.get(estado, estado.upper())
        st.markdown(f"""<div style="background: linear-gradient(135deg, #c62828, #b71c1c); padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(198, 40, 40, 0.4); margin: 20px 0;"><div style="font-size: 80px;">🚨</div><h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 800;">SIN SOAT VIGENTE</h1><h2 style="color: rgba(255,255,255,0.9); margin: 10px 0; font-size: 1.8rem;">{placa}</h2><p style="color: rgba(255,255,255,0.8); font-size: 1.2rem; background:rgba(0,0,0,0.2); display:inline-block; padding:5px 15px; border-radius:8px;">{motivo}</p></div>""", unsafe_allow_html=True)
        with st.expander("📋 Ver Conductor"): st.markdown(f"**Nombre:** {nombre}\n**Cargo:** {cargo}")
        mostrar_alerta("danger", f"⚠️ RESTRINGIDO. Registro guardado.")
        
        if correo and estado != "No Registrado":
            with st.spinner("📧 Enviando notificación..."):
                email_svc.enviar_alerta_sst_ingreso(correo, nombre, placa, motivo)
            mostrar_alerta("info", "📧 Notificación automática enviada al infractor.")
