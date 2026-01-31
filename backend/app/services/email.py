"""
Email Service using Resend
Handles sending transactional emails
"""

import httpx
from typing import Optional
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service using Resend API
    """

    RESEND_API_URL = "https://api.resend.com/emails"

    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.FROM_EMAIL

    def is_configured(self) -> bool:
        """Check if email service is configured"""
        return bool(self.api_key)

    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None
    ) -> bool:
        """
        Send an email using Resend API

        Args:
            to: Recipient email address
            subject: Email subject
            html: HTML content
            text: Plain text content (optional)

        Returns:
            bool: True if email sent successfully
        """
        if not self.is_configured():
            logger.warning("Email service not configured - RESEND_API_KEY not set")
            return False

        payload = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
            "html": html,
        }

        if text:
            payload["text"] = text

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.RESEND_API_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    logger.info(f"Email sent successfully to {to}")
                    return True
                else:
                    logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    async def send_password_reset_email(
        self,
        to: str,
        reset_url: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send password reset email

        Args:
            to: Recipient email address
            reset_url: Password reset URL with token
            user_name: User's name (optional)

        Returns:
            bool: True if email sent successfully
        """
        greeting = f"Hi {user_name}," if user_name else "Hi,"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Swiftor</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">AI Powered Clean And Credible News</p>
            </div>

            <div style="background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <h2 style="color: #1f2937; margin-top: 0;">Reset Your Password</h2>

                <p style="color: #4b5563;">{greeting}</p>

                <p style="color: #4b5563;">
                    We received a request to reset your password. Click the button below to create a new password:
                </p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        Reset Password
                    </a>
                </div>

                <p style="color: #6b7280; font-size: 14px;">
                    This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
                </p>

                <p style="color: #6b7280; font-size: 14px;">
                    If the button doesn't work, copy and paste this link into your browser:
                    <br>
                    <a href="{reset_url}" style="color: #6366f1; word-break: break-all;">{reset_url}</a>
                </p>

                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

                <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
                    This email was sent by Swiftor, a product of Data Insightopia.
                </p>
            </div>
        </body>
        </html>
        """

        text = f"""
{greeting}

We received a request to reset your password. Click the link below to create a new password:

{reset_url}

This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.

--
Swiftor - AI Powered Clean And Credible News
A product of Data Insightopia
        """

        return await self.send_email(
            to=to,
            subject="Reset Your Swiftor Password",
            html=html,
            text=text
        )


# Singleton instance
email_service = EmailService()
