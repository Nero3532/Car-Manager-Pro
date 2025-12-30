import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email(smtp_settings, to_email, subject, body, attachment_paths=None):
    """
    Sends an email using the provided SMTP settings.
    
    smtp_settings: dict with keys 'server', 'port', 'user', 'password'
    to_email: str
    subject: str
    body: str
    attachment_paths: list of str (optional)
    """
    server = smtp_settings.get('server')
    port = int(smtp_settings.get('port', 587))
    user = smtp_settings.get('user')
    password = smtp_settings.get('password')

    if not all([server, port, user, password]):
        raise ValueError("Unvollständige SMTP-Einstellungen. Bitte in den Einstellungen konfigurieren.")

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_paths:
        for path in attachment_paths:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
                    msg.attach(part)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls(context=context)
            smtp.login(user, password)
            smtp.send_message(msg)
        return True, "Email erfolgreich gesendet."
    except Exception as e:
        return False, str(e)

def test_smtp_connection(smtp_settings):
    """
    Tests the SMTP connection.
    """
    server = smtp_settings.get('server')
    port = int(smtp_settings.get('port', 587))
    user = smtp_settings.get('user')
    password = smtp_settings.get('password')
    
    if not all([server, port, user, password]):
        return False, "Unvollständige Einstellungen."

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls(context=context)
            smtp.login(user, password)
        return True, "Verbindung erfolgreich."
    except Exception as e:
        return False, str(e)
