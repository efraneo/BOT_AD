import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_recovery_email(destinatario, codigo):
    try:
        email_user = st.secrets["email_user"]
        email_pass = st.secrets["email_pass"]
        
        msg = MIMEMultipart()
        msg['From'] = f"Bot Apuestas PRO <{email_user}>"
        msg['To'] = destinatario
        msg['Subject'] = "Código de Recuperación de Clave - Bot Apuestas"
        
        body = f"""
        <h2>Recuperación de Acceso</h2>
        <p>Hola, has solicitado recuperar tu clave.</p>
        <p>Tu código de verificación es:</p>
        <h1 style='color:blue; font-size:32px;'>{codigo}</h1>
        <p>Ingresa este código en la plataforma para poder restablecer tu clave.</p>
        <p>Si no solicitaste esto, ignora este correo.</p>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.sendmail(email_user, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return Falseimport smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_recovery_email(destinatario, codigo):
    try:
        email_user = st.secrets["email_user"]
        email_pass = st.secrets["email_pass"]
        
        msg = MIMEMultipart()
        msg['From'] = f"Bot Apuestas PRO <{email_user}>"
        msg['To'] = destinatario
        msg['Subject'] = "Código de Recuperación de Clave - Bot Apuestas"
        
        body = f"""
        <h2>Recuperación de Acceso</h2>
        <p>Hola, has solicitado recuperar tu clave.</p>
        <p>Tu código de verificación es:</p>
        <h1 style='color:blue; font-size:32px;'>{codigo}</h1>
        <p>Ingresa este código en la plataforma para poder restablecer tu clave.</p>
        <p>Si no solicitaste esto, ignora este correo.</p>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.sendmail(email_user, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False
