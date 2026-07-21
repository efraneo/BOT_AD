import streamlit as st
from datetime import date
from utils import db, email_svc, soat_validator, tfa, validar_email, validar_placa, formatear_fecha_iso, mostrar_alerta

def mostrar():
    if "paso_registro" not in st.session_state: st.session_state["paso_registro"] = 1
    if "codigo_enviado" not in st.session_state: st.session_state["codigo_enviado"] = False
    paso = st.session_state["paso_registro"]

    st.markdown("""<div class="main-title"><h1>🚗 Registro de SOAT</h1><p>Sistema de control vehicular</p></div>""", unsafe_allow_html=True)
    pasos_html = '<div class="step-indicator">' + ''.join(f'<div class="step-dot {"completed" if i < paso else ("active" if i == paso else "")}"></div>' for i in range(1, 5)) + '</div>'
    st.markdown(pasos_html, unsafe_allow_html=True)
    etiquetas = {1: "Paso 1 — Verificación de Correo", 2: "Paso 2 — Datos Personales", 3: "Paso 3 — Vehículo y SOAT", 4: "Paso 4 — Confirmación"}
    st.markdown(f'<p style="text-align:center;color:#1a237e;font-weight:600;font-size:14px;margin-bottom:24px;">{etiquetas[paso]}</p>', unsafe_allow_html=True)

    if paso == 1: _paso_1()
    elif paso == 2: _paso_2()
    elif paso == 3: _paso_3()
    elif paso == 4: _paso_4()
    if st.session_state.get("registro_exitoso"): _exito()

def _paso_1():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        correo = st.text_input("Correo electrónico", placeholder="tucorreo@ejemplo.com", key="correo_p1")
        if not st.session_state.get("codigo_enviado"):
            if st.button("📩 Enviar código", use_container_width=True, disabled=not correo):
                if not validar_email(correo): mostrar_alerta("danger", "Correo no válido.")
                elif db.existe_correo(correo): mostrar_alerta("warning", "Este correo ya está registrado.")
                else:
                    r = tfa.solicitar_codigo(correo)
                    if r["exito"]: st.session_state["codigo_enviado"] = True; st.session_state["correo_temporal"] = correo; st.success(r["mensaje"]); st.rerun()
                    else: mostrar_alerta("danger", r["mensaje"])
        else:
            mostrar_alerta("info", f"Código enviado a {st.session_state.get('correo_temporal', '')}")
            cod = st.text_input("Código de 6 dígitos", max_chars=6, key="cod_2fa")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Verificar", use_container_width=True, disabled=not cod):
                    r = tfa.verificar_codigo(st.session_state["correo_temporal"], cod)
                    if r["valido"]: st.session_state["paso_registro"] = 2; st.session_state["correo_confirmado"] = st.session_state["correo_temporal"]; st.rerun()
                    else: mostrar_alerta("danger", r["mensaje"])
            with c2:
                if st.button("🔄 Reenviar", use_container_width=True): st.session_state["codigo_enviado"] = False; st.rerun()

def _paso_2():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        mostrar_alerta("info", f"Correo: **{st.session_state.get('correo_confirmado', '')}**")
        
        # ═══════════════════════════════════════════════════
        #  INFOGRAMA DE HABEAS DATA - CLÍNICA SAN RAFAEL
        # ═══════════════════════════════════════════════════
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f3f4f6, #e5e7eb); border: 1px solid #d1d5db; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 5px solid #1a237e;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 28px; margin-right: 10px;">🔒</div>
                <h4 style="margin: 0; color: #1a237e; font-size: 16px;">Autorización de Tratamiento de Datos Personales</h4>
            </div>
            <p style="font-size: 12px; color: #374151; line-height: 1.5; margin: 0 0 12px 0;">
                En cumplimiento de la <strong>Ley 1581 de 2012</strong> y el Decreto 1377 de 2013, los datos personales suministrados serán tratados por la 
                <strong>Clínica San Rafael Alta Complejidad SAS</strong> con la finalidad de realizar el registro vehicular, control de seguridad y salud en el trabajo (SST), 
                y verificación de pólizas SOAT.
            </p>
            <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 12px;">
                <p style="margin: 0 0 5px 0; font-size: 11px; color: #1f2937;"><strong>📄 Datos a recolectar:</strong> Identificación, nombres, cargo, fecha de nacimiento, correo, datos del vehículo e imagen del SOAT.</p>
                <p style="margin: 0 0 5px 0; font-size: 11px; color: #1f2937;"><strong>🕒 Tiempo de almacenamiento:</strong> El tiempo necesario para cumplir con las finalidades descritas y obligaciones legales vigentes.</p>
                <p style="margin: 0; font-size: 11px; color: #1f2937;"><strong>✅ Derechos del titular:</strong> Acceder, rectificar, cancelar, oponerse y revocar la autorización (Derechos ARCO). Para ejercerlos, escriba a <strong>notificaciones@clinicasanrafael.com</strong></p>
            </div>
            <p style="font-size: 10px; color: #6b7280; text-align: justify; margin: 0;">
                Al marcar la casilla de aceptación a continuación, el titular de la información declara que la información suministrada es verídica, autoriza de manera libre, previa, expresa e informada el tratamiento de sus datos personales, y manifiesta conocer la política de privacidad de la Clínica San Rafael Alta Complejidad SAS.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Checkbox obligatorio para continuar
        autorizado = st.checkbox("He leído y acepto la Autorización de Tratamiento de Datos Personales de la Clínica San Rafael Alta Complejidad SAS.", key="chk_habeas")
        # ═══════════════════════════════════════════════════

        with st.form("f_dp"):
            ced = st.text_input("🪪 Identificación", key="ced")
            nom = st.text_input("👤 Nombres Completos", key="nom")
            car = st.text_input("💼 Cargo", key="car")
            fec = st.date_input("📅 Fecha de Nacimiento", min_value=date(1950,1,1), max_value=date.today(), key="fec")
            if st.form_submit_button("Siguiente →", use_container_width=True):
                err = []
                # Validación legal primero que todo
                if not autorizado: err.append("Debe aceptar la Autorización de Tratamiento de Datos para continuar.")
                
                if not ced.strip(): err.append("Identificación obligatoria.")
                elif not ced.strip().isdigit() or len(ced.strip()) < 6: err.append("Identificación inválida (mín 6 dígitos).")
                elif db.existe_identificacion(ced.strip()): err.append("Identificación ya registrada.")
                if not nom.strip() or len(nom.strip()) < 5: err.append("Nombres inválidos (mín 5 caracteres).")
                if not car.strip(): err.append("Cargo obligatorio.")
                if not fec or (date.today() - fec).days < 6570: err.append("Debes ser mayor de edad.")
                if err:
                    for e in err: mostrar_alerta("danger", e)
                else:
                    st.session_state["datos_personales"] = {"identificacion": ced.strip(), "nombres": nom.strip(), "cargo": car.strip(), "correo": st.session_state["correo_confirmado"], "fecha_nacimiento": formatear_fecha_iso(fec)}
                    st.session_state["paso_registro"] = 3; st.rerun()
        if st.button("← Atrás", use_container_width=True): st.session_state["paso_registro"] = 1; st.session_state["codigo_enviado"] = False; st.rerun()

def _paso_3():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("f_vs"):
            tv = st.selectbox("🚘 Tipo de Vehículo", ["Selecciona...", "Automovil", "Motocicleta"], key="tv")
            pl = st.text_input("🔢 Placa", placeholder="ABC123 o ABC12D", key="pl")
            ar = st.file_uploader("📄 Adjuntar SOAT (imagen)", type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"])
            if ar: st.image(ar, caption="Vista previa", width=400)
            if st.form_submit_button("Siguiente →", use_container_width=True):
                err = []
                if tv == "Selecciona...": err.append("Selecciona tipo.")
                if not pl.strip(): err.append("Placa obligatoria.")
                elif not validar_placa(pl, tv): err.append("Formato de placa inválido.")
                if not ar: err.append("Adjunta imagen del SOAT.")
                if err:
                    for e in err: mostrar_alerta("danger", e)
                else:
                    with st.spinner("🔍 Analizando SOAT..."):
                        bytes_soat = ar.read()
                        res = soat_validator.validar_archivo(bytes_soat, ar.name)
                    st.session_state.update({"resultado_soat": res, "archivo_soat_bytes": bytes_soat, "archivo_soat_nombre": ar.name, "datos_vehiculo": {"tipo_vehiculo": tv, "placa": pl.strip().upper()}, "paso_registro": 4})
                    st.rerun()
        if st.button("← Atrás", use_container_width=True): st.session_state["paso_registro"] = 2; st.rerun()

def _paso_4():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        dp, dv, rs = st.session_state.get("datos_personales", {}), st.session_state.get("datos_vehiculo", {}), st.session_state.get("resultado_soat", {})
        st.markdown("**👤 Datos:**"); st.markdown(f"- **ID:** {dp.get('identificacion')}\n- **Nombre:** {dp.get('nombres')}\n- **Cargo:** {dp.get('cargo')}\n- **Correo:** {dp.get('correo')}")
        st.markdown("**🚗 Vehículo:**"); st.markdown(f"- **Tipo:** {dv.get('tipo_vehiculo')}\n- **Placa:** {dv.get('placa')}")
        st.markdown("**📄 Estado SOAT:**")
        mostrar_alerta("success" if rs.get("calidad_ok") else "danger", rs.get("calidad_mensaje", ""))
        colores = {"Vigente": "success", "Por vencer": "warning", "Vencido": "danger", "No legible": "info"}
        mostrar_alerta(colores.get(rs.get("estado",""), "info"), rs.get("mensaje_general", ""))
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Corregir", use_container_width=True): st.session_state["paso_registro"] = 3; st.rerun()
        with c2:
            if st.button("✅ Enviar Registro", use_container_width=True, type="primary"):
                with st.spinner("📤 Enviando..."):
                    try: url_soat = db.subir_archivo_soat(st.session_state["archivo_soat_bytes"], st.session_state["archivo_soat_nombre"])
                    except Exception as e: mostrar_alerta("danger", f"Error al subir archivo: {e}"); st.stop()
                    
                    fv_iso = formatear_fecha_iso(rs["fecha_vencimiento"]) if rs.get("fecha_vencimiento") else None
                    datos_completos = {**dp, **dv, "soat_url": url_soat, "soat_nombre_archivo": st.session_state["archivo_soat_nombre"], "soat_vigencia": fv_iso, "soat_estado": rs.get("estado", "No legible"), "soat_calidad_imagen": rs.get("calidad_score", 0), "calidad_imagen_ok": rs.get("calidad_ok", False)}
                    res_bd = db.registrar_trabajador(datos_completos)
                    if res_bd["exito"]:
                        email_svc.enviar_confirmacion_registro(dp["correo"], datos_completos, st.session_state["archivo_soat_bytes"], st.session_state["archivo_soat_nombre"])
                        if not rs.get("calidad_ok") or rs.get("estado") == "No legible": email_svc.enviar_notificacion_imagen(dp["correo"], rs.get("calidad_mensaje", "No se pudo leer."))
                        for key in list(st.session_state.keys()): del st.session_state[key]
                        st.session_state["registro_exitoso"] = True; st.rerun()
                    else: mostrar_alerta("danger", res_bd["mensaje"])

def _exito():
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("""<div style="text-align:center; padding:48px 24px;"><div style="font-size:64px;">🎉</div><h2 style="color:#2e7d32;">¡Registro Exitoso!</h2></div>""", unsafe_allow_html=True)
        mostrar_alerta("success", "Se envió un correo con tu comprobante y el SOAT adjunto.")
        if st.button("📝 Registrar otro", use_container_width=True, type="primary"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
