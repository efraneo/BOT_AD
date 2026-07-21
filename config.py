"""
config.py
Carga de configuración desde Streamlit Secrets (nube) o claves_soat.env (local).
"""
import os
import json
from dotenv import load_dotenv

# Cargar .env SOLO si estamos en local
if os.path.exists("claves_soat.env"):
    load_dotenv("claves_soat.env")


def _obtener(clave: str, por_defecto: str = "") -> str:
    """Busca una variable en st.secrets, luego en el entorno."""
    try:
        import streamlit as st
        if clave in st.secrets:
            return st.secrets[clave]
    except Exception:
        pass
    return os.getenv(clave, por_defecto)


def _obtener_garita_users() -> dict:
    """Obtiene la lista de usuarios permitidos para la garita."""
    try:
        import streamlit as st
        if "GARITA_USERS" in st.secrets:
            return dict(st.secrets["GARITA_USERS"])
    except Exception:
        pass
    garita_str = os.getenv("GARITA_USERS", '{"efraneo@hotmail.com": "1234567890", "efraneo@gmail.com": "dasb1512"}')
    try:
        return json.loads(garita_str)
    except Exception:
        return {"efraneo@hotmail.com": "1234567890", "efraneo@gmail.com": "dasb1512"}


class Config:
    """Configuración centralizada — funciona en local y en la nube."""

    # ── Supabase ──
    SUPABASE_URL: str = _obtener("SUPABASE_URL", "")
    SUPABASE_KEY: str = _obtener("SUPABASE_KEY", "")

    # ── SMTP / Correo ──
    EMAIL_HOST: str = _obtener("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(_obtener("EMAIL_PORT", "587"))
    EMAIL_USER: str = _obtener("EMAIL_USER", "")
    EMAIL_PASSWORD: str = _obtener("EMAIL_PASSWORD", "")
    EMAIL_FROM_NAME: str = _obtener("EMAIL_FROM_NAME", "Sistema SOAT")

    # ── Administrador ──
    ADMIN_EMAIL: str = _obtener("ADMIN_EMAIL", "efraneo@gmail.com")
    ADMIN_PASSWORD: str = _obtener("ADMIN_PASSWORD", "dasb1512")

    # ── 2FA ──
    TWO_FACTOR_EXPIRY_SECONDS: int = int(_obtener("TWO_FACTOR_EXPIRY_SECONDS", "300"))

    # ── OpenAI ──
    OPENAI_API_KEY: str = _obtener("OPENAI_API_KEY", "")

    # ── Validación SOAT ──
    SOAT_ALERTA_DIAS: int = 30
    MIN_IMAGE_QUALITY_SCORE: float = 40.0
    MIN_IMAGE_WIDTH: int = 400
    MIN_IMAGE_HEIGHT: int = 300

    # ── Storage ──
    SOAT_STORAGE_BUCKET: str = "soat-archivos"

    # ── Tipos de vehículo ──
    TIPOS_VEHICULO: list = ["Automovil", "Motocicleta"]

    # ── Usuarios de Garita / SST ──
    GARITA_USERS: dict = _obtener_garita_users()

    @classmethod
    def validar(cls) -> bool:
        """Verifica que las credenciales esenciales estén configuradas."""
        errores = []
        if not cls.SUPABASE_URL:
            errores.append("SUPABASE_URL no configurada")
        if not cls.SUPABASE_KEY:
            errores.append("SUPABASE_KEY no configurada")
        if not cls.EMAIL_USER:
            errores.append("EMAIL_USER no configurado")
        if not cls.EMAIL_PASSWORD:
            errores.append("EMAIL_PASSWORD no configurado")
        if errores:
            for e in errores:
                print(f"⚠️  {e}")
            return False
        return True
