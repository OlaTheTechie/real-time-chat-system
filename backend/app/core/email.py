"""
Email service for sending password reset and other emails
Supports SMTP and SendGrid
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending emails via SMTP or SendGrid"""
    
    def __init__(self):
        self.enabled = settings.EMAIL_ENABLED
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
        
        # SMTP settings
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        
        # Frontend URL for reset links
        self.frontend_url = settings.FRONTEND_URL
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email using configured email service"""
        if not self.enabled:
            logger.info(f"Email disabled. Would send to {to_email}: {subject}")
            return False
        
        try:
            return self._send_via_smtp(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.smtp_tls:
                server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email with token"""
        reset_link = f"{self.frontend_url}/password-reset?token={reset_token}"
        
        subject = "Reset Your Password"
        
        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 12px;
                }}
                .token-box {{
                    background: #fff;
                    border: 2px dashed #667eea;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                    font-family: monospace;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>We received a request to reset your password. Click the button below to reset it:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <div class="token-box">
                        {reset_link}
                    </div>
                    
                    <p><strong>This link will expire in 30 minutes.</strong></p>
                    
                    <p>If you didn't request a password reset, you can safely ignore this email.</p>
                    
                    <p>Best regards,<br>The Chat App Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        Password Reset Request
        
        Hello,
        
        We received a request to reset your password. Click the link below to reset it:
        
        {reset_link}
        
        This link will expire in 30 minutes.
        
        If you didn't request a password reset, you can safely ignore this email.
        
        Best regards,
        The Chat App Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)


# Singleton instance
email_service = EmailService()
