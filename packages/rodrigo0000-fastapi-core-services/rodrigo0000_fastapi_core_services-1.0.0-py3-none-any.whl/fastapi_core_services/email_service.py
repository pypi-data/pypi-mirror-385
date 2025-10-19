"""
Email service - Generic email functionality for SaaS
Basado en el patrón de Autogrid
"""

from typing import List, Optional
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings

class EmailService:
    """Generic email service for SaaS applications"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.mail_from = os.getenv("MAIL_FROM", f"noreply@{settings.APP_NAME.lower().replace(' ', '')}.com")
        self.mail_from_name = os.getenv("MAIL_FROM_NAME", settings.APP_NAME)

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
        """
        Send email using SMTP
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.mail_from_name} <{self.mail_from}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def send_password_reset_email(self, email: str, username: str, token: str, base_url: str) -> bool:
        """Send password reset email"""
        reset_url = f"{base_url}/reset-password?token={token}"
        
        subject = f"Restablecer contraseña - {self.mail_from_name}"
        body = f"""
        <html>
        <body>
            <h2>Restablecer contraseña</h2>
            <p>Hola {username},</p>
            <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace:</p>
            <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restablecer contraseña</a></p>
            <p>Este enlace expirará en 10 minutos.</p>
            <p>Si no solicitaste este cambio, ignora este correo.</p>
            <br>
            <p>Saludos,<br>El equipo de {self.mail_from_name}</p>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, body)

    def send_email_verification(self, email: str, username: str, token: str, base_url: str) -> bool:
        """Send email verification"""
        verify_url = f"{base_url}/verify-email?token={token}"
        
        subject = f"Verificar email - {self.mail_from_name}"
        body = f"""
        <html>
        <body>
            <h2>Verificar tu email</h2>
            <p>Hola {username},</p>
            <p>Gracias por registrarte en {self.mail_from_name}. Para completar tu registro, verifica tu email:</p>
            <p><a href="{verify_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verificar email</a></p>
            <p>Este enlace expirará en 30 minutos.</p>
            <br>
            <p>¡Bienvenido!<br>El equipo de {self.mail_from_name}</p>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, body)

    def send_welcome_email(self, email: str, username: str) -> bool:
        """Send welcome email"""
        subject = f"¡Bienvenido a {self.mail_from_name}!"
        body = f"""
        <html>
        <body>
            <h2>¡Bienvenido a {self.mail_from_name}!</h2>
            <p>Hola {username},</p>
            <p>Tu cuenta ha sido creada exitosamente. Estamos emocionados de tenerte con nosotros.</p>
            <p>Puedes empezar a usar todas las funcionalidades de tu plan.</p>
            <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
            <br>
            <p>¡Que disfrutes la experiencia!<br>El equipo de {self.mail_from_name}</p>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, body)
