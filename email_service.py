"""
email_service.py
Servicio de envío de correos electrónicos.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr, formatdate
from datetime import datetime
from config import Config


class EmailService:
    def __init__(self):
        self.host = Config.EMAIL_HOST
        self.port = Config.EMAIL_PORT
        self.user = Config.EMAIL_USER
        self.password = Config.EMAIL_PASSWORD
        self.from_name = Config.EMAIL_FROM_NAME

    def _conectar(self) -> smtplib.SMTP:
        server = smtplib.SMTP(self.host, self.port, timeout=30)
        server.starttls()
        server.login(self.user, self.password)
        return server

    def _enviar(self, destinatario: str, asunto: str, html_body: str, adjunto_bytes: bytes = None, adjunto_nombre: str = None) -> bool:
        try:
            msg = MIMEMultipart("related")
            msg["From"] = formataddr((self.from_name, self.user))
            msg["To"] = destinatario
            msg["Subject"] = asunto
            msg["Date"] = formatdate(localtime=True)

            msg_alternativo = MIMEMultipart("alternative")
            texto_plano = self._html_a_texto(html_body)
            msg_alternativo.attach(MIMEText(texto_plano, "plain", "utf-8"))
            msg_alternativo.attach(MIMEText(html_body, "html", "utf-8"))
            msg.attach(msg_alternativo)

            if adjunto_bytes and adjunto_nombre:
                parte = MIMEApplication(adjunto_bytes, Name=adjunto_nombre)
                parte["Content-Disposition"] = f'attachment; filename="{adjunto_nombre}"'
                msg.attach(parte)

            server = self._conectar()
            server.sendmail(self.user, [destinatario], msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"❌ Error enviando correo: {e}")
            return False

    @staticmethod
    def _html_a_texto(html: str) -> str:
        import re
        texto = re.sub(r'<br\s*/?>', '\n', html)
        texto = re.sub(r'<[^>]+>', '', texto)
        return texto.replace("&nbsp;", " ").replace("&amp;", "&").strip()

    def enviar_codigo_2fa(self, destinatario: str, codigo: str) -> bool:
        asunto = "🔐 Tu código de verificación - Registro SOAT"
        html = f"""
        <div style="max-width:600px; margin:0 auto; font-family:'Segoe UI',Arial,sans-serif; background:#f8f9fa; border-radius:12px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
            <div style="background:linear-gradient(135deg,#1a237e,#283593); padding:32px; text-align:center;">
                <h1 style="color:#fff; margin:0; font-size:24px;">🔐 Verificación de Correo</h1>
            </div>
            <div style="padding:32px; background:#fff;">
                <p style="color:#333; font-size:16px;">Hola, tu código es:</p>
                <div style="background:#f0f4ff; border:2px dashed #1a237e; border-radius:12px; padding:24px; text-align:center; margin:24px 0;">
                    <span style="font-size:42px; font-weight:800; color:#1a237e; letter-spacing:8px; font-family:'Courier New',monospace;">{codigo}</span>
                </div>
                <p style="color:#666; font-size:13px; text-align:center;">⏱️ Expira en 5 minutos.</p>
            </div>
        </div>"""
        return self._enviar(destinatario, asunto, html)

    def enviar_confirmacion_registro(self, destinatario: str, datos: dict, adjunto_bytes: bytes = None, adjunto_nombre: str = None) -> bool:
        asunto = "✅ Registro Exitoso - Comprobante SOAT"
        colores_estado = {"Vigente": "#2e7d32", "Por vencer": "#f57f17", "Vencido": "#c62828", "No legible": "#6a1b9a"}
        color = colores_estado.get(datos.get("soat_estado", ""), "#333")
        
        fecha_venc_str = "No detectada"
        if datos.get("soat_vigencia"):
            try:
                fv = datos["soat_vigencia"]
                if isinstance(fv, str): fv = datetime.fromisoformat(fv.replace("Z", "+00:00")).date()
                fecha_venc_str = fv.strftime("%d/%m/%Y")
            except: fecha_venc_str = str(datos["soat_vigencia"])

        fecha_nac_str = datos.get("fecha_nacimiento", "N/A")
        if isinstance(fecha_nac_str, str) and "T" in fecha_nac_str:
            try: fecha_nac_str = datetime.fromisoformat(fecha_nac_str.replace("Z", "+00:00")).date().strftime("%d/%m/%Y")
            except: pass

        html = f"""
        <div style="max-width:650px; margin:0 auto; font-family:'Segoe UI',Arial,sans-serif; background:#f8f9fa; border-radius:12px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
            <div style="background:linear-gradient(135deg,#1b5e20,#2e7d32); padding:36px; text-align:center;">
                <h1 style="color:#fff; margin:0;">✅ Registro Completado</h1>
            </div>
            <div style="padding:32px; background:#fff;">
                <table style="width:100%; border-collapse:collapse; font-size:14px;">
                    <tr style="background:#f0f7f0;"><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0; width:40%;">Identificación</td><td style="padding:12px; border-bottom:1px solid #e0e0e0;">{datos.get('identificacion', 'N/A')}</td></tr>
                    <tr><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0;">Nombres</td><td style="padding:12px; border-bottom:1px solid #e0e0e0;">{datos.get('nombres', 'N/A')}</td></tr>
                    <tr style="background:#f0f7f0;"><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0;">Cargo</td><td style="padding:12px; border-bottom:1px solid #e0e0e0;">{datos.get('cargo', 'N/A')}</td></tr>
                    <tr><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0;">Correo</td><td style="padding:12px; border-bottom:1px solid #e0e0e0;">{datos.get('correo', 'N/A')}</td></tr>
                    <tr style="background:#f0f7f0;"><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0;">Fecha Nacimiento</td><td style="padding:12px; border-bottom:1px solid #e0e0e0;">{fecha_nac_str}</td></tr>
                    <tr><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0;">Tipo Vehículo</td><td style="padding:12px; border-bottom:1px solid #e0e0e0;">{datos.get('tipo_vehiculo', 'N/A')}</td></tr>
                    <tr style="background:#f0f7f0;"><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0;">Placa</td><td style="padding:12px; border-bottom:1px solid #e0e0e0; font-weight:700;">{datos.get('placa', 'N/A').upper()}</td></tr>
                    <tr><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0;">Estado SOAT</td><td style="padding:12px; border-bottom:1px solid #e0e0e0; font-weight:700; color:{color};">{datos.get('soat_estado', 'N/A')}</td></tr>
                    <tr style="background:#f0f7f0;"><td style="padding:12px; font-weight:700; color:#1b5e20; border-bottom:1px solid #e0e0e0;">Vencimiento SOAT</td><td style="padding:12px; border-bottom:1px solid #e0e0e0;">{fecha_venc_str}</td></tr>
                </table>
                <div style="margin-top:24px; padding:16px; background:#fff8e1; border-left:4px solid #f57f17; border-radius:4px;">
                    <p style="margin:0; color:#e65100; font-size:13px;">📌 El soporte del SOAT se adjunta a este correo.</p>
                </div>
            </div>
        </div>"""
        return self._enviar(destinatario, asunto, html, adjunto_bytes, adjunto_nombre)

    def enviar_notificacion_imagen(self, destinatario: str, motivo: str) -> bool:
        asunto = "📷 Acción Requerida - SOAT No Legible"
        html = f"""
        <div style="max-width:600px; margin:0 auto; font-family:'Segoe UI',Arial,sans-serif; background:#f8f9fa; border-radius:12px; overflow:hidden;">
            <div style="background:linear-gradient(135deg,#6a1b9a,#8e24aa); padding:32px; text-align:center;">
                <h1 style="color:#fff; margin:0;">📷 Acción Requerida</h1>
            </div>
            <div style="padding:32px; background:#fff;">
                <p style="color:#333; font-size:15px;">La imagen del SOAT no pudo ser procesada:</p>
                <div style="background:#fce4ec; border-left:4px solid #c62828; padding:16px; margin:20px 0; border-radius:4px;">
                    <p style="margin:0; color:#b71c1c;"><strong>Motivo:</strong> {motivo}</p>
                </div>
                <p style="color:#555; font-size:13px;">Por favor vuelve a registrar tu SOAT con una foto nítida.</p>
            </div>
        </div>"""
        return self._enviar(destinatario, asunto, html)

    def enviar_alerta_sst_ingreso(self, destinatario: str, nombre: str, placa: str, estado: str) -> bool:
        asunto = "🚨 Alerta de Seguridad Vial - Ingreso sin SOAT Vigente (CSR AC)"
        html = f"""
        <div style="max-width:600px; margin:0 auto; font-family:'Segoe UI',Arial,sans-serif; background:#f8f9fa; border-radius:12px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
            <div style="background:linear-gradient(135deg,#c62828,#b71c1c); padding:32px; text-align:center;">
                <h1 style="color:#fff; margin:0;">🚨 Notificación de Seguridad Vial</h1>
                <p style="color:rgba(255,255,255,0.85); margin:8px 0 0;">Coordinación de SST - CSR AC</p>
            </div>
            <div style="padding:32px; background:#fff;">
                <p style="color:#333; font-size:15px;">Hola, <strong>{nombre}</strong>. Te informamos que en el control de acceso de hoy, el vehículo asociado a tu identificación ingresó con el siguiente estado:</p>
                <div style="background:#ffebee; border-left:4px solid #c62828; padding:16px; margin:24px 0; border-radius:4px;">
                    <p style="margin:0; color:#b71c1c; font-size:15px;"><strong>Placa:</strong> {placa}<br><strong>Estado:</strong> {estado}</p>
                </div>
                <p style="color:#333; font-size:14px;">En <strong>CSR AC</strong> nos importa tu seguridad. Te invitamos amablemente a <strong>poner al día tu documento SOAT</strong> y actualizar tu registro en el sistema lo antes posible.</p>
                <div style="background:#e8f5e9; border:1px solid #c8e6c9; border-radius:8px; padding:16px; margin:24px 0; text-align:center;">
                    <p style="margin:0; color:#1b5e20; font-size:15px; font-weight:600;">🤝 ¡Juntos de la mano con la seguridad vial en CSR AC!</p>
                </div>
            </div>
            <div style="background:#f8f9fa; padding:16px 32px; text-align:center; border-top:1px solid #eee;">
                <p style="color:#999; font-size:11px; margin:0;">Mensaje automático del Sistema de Control Vial CSR AC. No responder.</p>
            </div>
        </div>"""
        return self._enviar(destinatario, asunto, html)
