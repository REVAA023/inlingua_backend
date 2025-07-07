import os
import random
from rest_framework import status
from rest_framework.response import Response
from twilio.rest import Client
from api.models import OTP
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail
from itsdangerous import URLSafeTimedSerializer

# ✅ Securely retrieve Twilio credentials from environment variables only
TWILIO_ACCOUNT_SID = "ACdff04487d1bc43ef8e5cc6ae114382fd"
TWILIO_AUTH_TOKEN = "d6f3171901db327f47f193ab09614816"
TWILIO_PHONE_NUMBER = "+19804145465"

class OTPService:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def send_otp(self, mobile_number):
        if not mobile_number:
            return {"success": False, "message": "Mobile number is required."}

        otp = self.generate_otp()
        expiry_time = now() + timedelta(minutes=5)

        otp_entry, created = OTP.objects.get_or_create(
            mobile_number=mobile_number,
            defaults={"otp": otp, "expires_at": expiry_time},
        )

        if not created:
            otp_entry.otp = otp
            otp_entry.expires_at = expiry_time
            otp_entry.save()

        try:
            self.client.messages.create(
                body=f"Your OTP is: {otp}",
                from_=TWILIO_PHONE_NUMBER,
                to=f"+91{mobile_number}"
            )
            return {"success": True, "message": "OTP sent successfully."}
        except Exception as e:
            return {"success": False, "message": f"Failed to send OTP: {str(e)}"}

    def send_email_otp(self, email):
        if not email:
            return {"success": False, "message": "Email is required."}

        otp = self.generate_otp()
        expiry_time = timezone.now() + timedelta(minutes=5)

        otp_entry, created = OTP.objects.get_or_create(
            mobile_number=email,
            defaults={"otp": otp, "expires_at": expiry_time},
        )

        if not created:
            otp_entry.otp = otp
            otp_entry.expires_at = expiry_time
            otp_entry.save()

        try:
            send_mail(
                subject="Account Verification OTP",
                message=f"Your gmail OTP is: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            return {"success": True, "message": "OTP sent to email."}
        except Exception as e:
            return {"success": False, "message": f"Failed to send OTP: {str(e)}"}

# Reset password link in mail 
# 1. Token generation remains same
def generate_password_reset_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = serializer.dumps(email, salt='password-reset-salt')
    return token

# 2. Email sending and token saving
def send_password_reset_link(user):
    try:
        token = generate_password_reset_token(user.email)
        reset_link = f"https://inlingua-crm.netlify.app/reset-password/?token={token}"

        subject = 'Reset Your Password'
        message = f"""
        Hi {user.first_name} {user.last_name},

        We received a request to reset your password.

        Click the link below to set a new password. This link is valid for 24 hours and can be used only once:

        {reset_link}

        If you didn’t request this, please ignore this email.

        Thanks,  
        YourApp Team
        """

        send_mail(
            subject,
            message,
            'test.inlingua@revaadigital.com',
            [user.email],
            fail_silently=False,
        )
        
        

        # Save token for 1-time use tracking
        user.password_reset_token = token
        user.password_reset_token_created_at = timezone.now()
        user.save()
    except Exception as e:
        return Response({"message": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)