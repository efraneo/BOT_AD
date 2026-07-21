"""
utils.py
Funciones auxiliares compartidas.
"""
import re
import streamlit as st
from datetime import date
from config import Config
from database import Database
from email_service import EmailService
from soat_validator import SOATValidator
from two_factor import TwoFactorAuth

db = Database()
email_svc = EmailService()
soat_validator = SOATValidator()
tfa = TwoFactorAuth()

def validar_email(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validar_placa(placa: str, tipo_vehiculo: str) -> bool:
    placa = placa.upper().strip()
    if tipo_vehiculo == "Automovil": return bool(re.match(r'^[A-Z]{3}\d{3}$', placa))
    elif tipo_vehiculo == "Motocicleta": return bool(re.match(r'^[A-Z]{3}\d{2}[A-Z]$', placa))
    return False

def formatear_fecha_iso(fecha: date) -> str:
    return fecha.isoformat()

def mostrar_alerta(tipo: str, mensaje: str):
    cls = f"alerta-{tipo}"
    icono = {"danger": "🚨", "warning": "⚠️", "info": "ℹ️", "success": "✅"}.get(tipo, "")
    st.markdown(f'<div class="{cls}">{icono} {mensaje}</div>', unsafe_allow_html=True)

def mostrar_metrica_card(icono: str, valor, etiqueta: str, color: str = "#1a237e"):
    st.markdown(f'''
    <div class="metric-card" style="text-align:center; border-top: 4px solid {color};">
        <div style="font-size:2rem; margin-bottom:4px;">{icono}</div>
        <div style="font-size:2rem; font-weight:800; color:{color};">{valor}</div>
        <div style="font-size:0.85rem; color:#666; margin-top:2px;">{etiqueta}</div>
    </div>''', unsafe_allow_html=True)
