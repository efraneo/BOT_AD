import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import db, mostrar_alerta, mostrar_metrica_card

def mostrar():
    # ═══ BOTONES DE NAVEGACIÓN ═══
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Inicio", use_container_width=True):
            st.session_state.clear(); st.rerun()
    with c2:
        if st.button("🚪 Salir", use_container_width=True):
            st.session_state["admin_autenticado"] = False; st.rerun()

    st.markdown("""<div class="main-title"><h1>📊 Panel Admin</h1></div>""", unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with st.spinner("Cargando..."): ind = db.obtener_indicadores()

    # ═══ KPIs ═══
    cols = st.columns(6)
    with cols[0]: mostrar_metrica_card("👥", ind["total"], "Total", "#1a237e")
    with cols[1]: mostrar_metrica_card("✅", ind["vigentes"], "Vigentes", "#2e7d32")
    with cols[2]: mostrar_metrica_card("⚠️", ind["por_vencer"], "P. Vencer", "#f57f17")
    with cols[3]: mostrar_metrica_card("🚨", ind["vencidos"], "Vencidos", "#c62828")
    with cols[4]: mostrar_metrica_card("📷", ind["no_legibles"], "No Leg.", "#6a1b9a")
    with cols[5]: mostrar_metrica_card("⏳", ind["pendientes"], "Pend.", "#607d8b")

    # ═══ GRÁFICOS Y ALERTAS ═══
    if ind["total"] > 0: _mostrar_graficos(ind)
    
    if ind["alertas"]:
        with st.expander(f"🔔 Alertas ({len(ind['alertas'])})", expanded=True):
            for a in ind["alertas"]: mostrar_alerta(a["tipo"], a["mensaje"])

    # ═══ HISTORIAL GARITA ═══
    st.markdown("### 🛂 Garita (Hoy)")
    hist = db.obtener_historial_hoy()
    if hist:
        df_h = pd.DataFrame(hist)[["placa", "nombre_trabajador", "estado_soat", "fecha_ingreso"]].rename(columns={"placa": "Placa", "nombre_trabajador": "Nombre", "estado_soat": "Estado", "fecha_ingreso": "Hora"})
        df_h["Hora"] = df_h["Hora"].apply(lambda x: str(x).split("T")[1][:8] if "T" in str(x) else str(x)[:8])
        st.dataframe(df_h.style.map(lambda v: "background-color: #c8e6c9; color: #1b5e20; font-weight: 600" if v == "Vigente" else "background-color: #ffcdd2; color: #b71c1c; font-weight: 700", subset=["Estado"]), use_container_width=True, height=200, hide_index=True)
    else: st.info("📭 Sin ingresos hoy.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    #  EDITOR DE REGISTROS (DATOS Y SOPORTES SOAT)
    # ═══════════════════════════════════════════════════════════════
    st.markdown("### ✏️ Gestión de Registros")
    
    id_buscar = st.text_input("🔑 Ingrese ID a gestionar:", placeholder="Pega aquí el ID del trabajador...", key="id_gestion")
    
    if id_buscar:
        current = db.obtener_trabajador_por_id(id_buscar)
        if not current:
            mostrar_alerta("danger", "ID no encontrado.")
        else:
            # Mostramos info básica del encontrado
            mostrar_alerta("success", f"Registro encontrado: {current.get('nombres')} - {current.get('placa')}")
            
            # Pestañas para no saturar
            tab1, tab2, tab3 = st.tabs(["📝 Editar Datos", "📄 Cambiar Soporte SOAT", "🗑️ Eliminar"])
            
            with tab1:
                with st.form("form_editar"):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_nom = st.text_input("👤 Nombre", value=current.get("nombres", ""))
                        new_car = st.text_input("💼 Cargo", value=current.get("cargo", ""))
                    with c2:
                        new_placa = st.text_input("🚘 Placa", value=current.get("placa", ""))
                        new_tv = st.selectbox("🏷️ Tipo", ["Automovil", "Motocicleta"], index=0 if current.get("tipo_vehiculo")=="Automovil" else 1)
                    
                    if st.form_submit_button("💾 Guardar Datos", use_container_width=True):
                        datos = {"nombres": new_nom, "cargo": new_car, "placa": new_placa.upper(), "tipo_vehiculo": new_tv}
                        res = db.actualizar_trabajador(id_buscar, datos)
                        if res["exito"]: st.success("✅ Datos actualizados."); st.rerun()
                        else: st.error(f"Error: {res['mensaje']}")

            with tab2:
                st.markdown("Sube una **nueva imagen** del SOAT. El sistema la analizará y actualizará la fecha y estado automáticamente.")
                new_img = st.file_uploader("📎 Nueva imagen SOAT", type=["jpg", "jpeg", "png"], key="img_edit")
                if new_img:
                    st.image(new_img, width=300)
                    if st.button("🔄 Actualizar Soporte", use_container_width=True, type="primary"):
                        with st.spinner("🔄 Procesando nueva imagen..."):
                            bytes_img = new_img.read()
                            datos_img = {}
                            res = db.actualizar_trabajador(id_buscar, datos_img, bytes_img, new_img.name)
                            if res["exito"]:
                                st.success("✅ Soporte de SOAT actualizado correctamente.")
                                st.rerun()
                            else: st.error(f"Error: {res['mensaje']}")

            with tab3:
                st.warning("Esta acción no se puede deshacer.")
                if st.button("⚠️ Eliminar Registro", type="primary"):
                    if db.eliminar_trabajador(id_buscar): st.success("Eliminado."); st.rerun()
                    else: st.error("Error al eliminar.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📋 Base de Datos Completa")
    _mostrar_tabla()

def _mostrar_graficos(ind):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🚘 Tipo Vehículo")
        if ind["por_tipo_vehiculo"]:
            df = pd.DataFrame([{"Tipo": k, "Cantidad": v} for k, v in ind["por_tipo_vehiculo"].items()])
            fig = px.pie(df, values="Cantidad", names="Tipo", hole=0.5, color_discrete_sequence=["#1a237e", "#f57f17"])
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=250)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("#### 💼 Cargos")
        if ind["por_cargo"]:
            df = pd.DataFrame([{"Cargo": k, "Cantidad": v} for k, v in ind["por_cargo"].items()]).sort_values("Cantidad")
            fig = px.bar(df, x="Cantidad", y="Cargo", orientation="h", color="Cantidad", color_continuous_scale="Blues")
            fig.update_layout(margin=dict(t=10, b=10, l=100, r=10), height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### 📅 Registros/Mes")
    if ind["por_mes"]:
        df = pd.DataFrame([{"Mes": k, "Registros": v} for k, v in ind["por_mes"].items()]).sort_values("Mes")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Mes"], y=df["Registros"], mode="lines+markers+text", text=df["Registros"], textposition="top center", line=dict(color="#1a237e", width=3), fill="tozeroy", fillcolor="rgba(26,35,126,0.08)"))
        fig.update_layout(margin=dict(t=20, b=40, l=40, r=20), height=250)
        st.plotly_chart(fig, use_container_width=True)

def _mostrar_tabla():
    todos = db.obtener_todos_trabajadores()
    if not todos: st.info("📭 Vacía."); return
    df = pd.DataFrame(todos)[["identificacion", "nombres", "cargo", "tipo_vehiculo", "placa", "soat_estado", "soat_vigencia", "fecha_registro"]].rename(columns={"identificacion": "ID", "nombres": "Nombre", "cargo": "Cargo", "tipo_vehiculo": "Tipo", "placa": "Placa", "soat_estado": "Estado SOAT", "soat_vigencia": "Vencimiento", "fecha_registro": "Fecha"})
    for c in ["Vencimiento", "Fecha"]: df[c] = df[c].apply(lambda x: str(x)[:10] if pd.notna(x) else "N/A")
    st.dataframe(df.style.map(lambda v: "background-color: #c8e6c9; color: #1b5e20; font-weight: 600" if v=="Vigente" else ("background-color: #fff9c4; color: #f57f17; font-weight: 600" if v=="Por vencer" else ("background-color: #ffcdd2; color: #c62828; font-weight: 600" if v=="Vencido" else "background-color: #e1bee7; color: #6a1b9a; font-weight: 600")), subset=["Estado SOAT"]), use_container_width=True, height=400, hide_index=True)
