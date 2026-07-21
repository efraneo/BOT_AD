"""
two_factor.py
Generación y gestión de códigos 2FA.
"""
import random
import string
from datetime import datetime, timezone, timedelta
from database import Database
from email_service import EmailService
from config import Config


class TwoFactorAuth:
    def __init__(self):
        self.db = Database()
        self.email = EmailService()
        self.expiry_seconds = Config.TWO_FACTOR_EXPIRY_SECONDS

    def generar_codigo(self, longitud: int = 6) -> str:
        return "".join(random.choices(string.digits, k=longitud))

    def solicitar_codigo(self, correo: str) -> dict:
        self.db.limpiar_codigos_antiguos()
        try:
            hace_60_seg = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
            from supabase import create_client
            client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            reciente = client.table("codigos_2fa").select("id").eq("correo", correo).gte("creado_en", hace_60_seg).execute()
            if reciente.data:
                return {"exito": False, "mensaje": "Espera 1 minuto antes de solicitar otro código."}
        except: pass

        codigo = self.generar_codigo(6)
        expiracion = datetime.now(timezone.utc) + timedelta(seconds=self.expiry_seconds)
        if not self.db.guardar_codigo_2fa(correo, codigo, expiracion):
            return {"exito": False, "mensaje": "Error al generar el código."}
        if not self.email.enviar_codigo_2fa(correo, codigo):
            return {"exito": False, "mensaje": "Error al enviar el correo."}
        return {"exito": True, "mensaje": f"Código enviado a {correo}."}

    def verificar_codigo(self, correo: str, codigo: str) -> dict:
        return self.db.verificar_codigo_2fa(correo, codigo.strip())
