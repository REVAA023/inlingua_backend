import os
import random
from twilio.rest import Client
from api.models import OTP, CustomUser, UserToken
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import HttpResponse, redirect
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.core.mail import send_mail
from itsdangerous import URLSafeTimedSerializer

# ✅ Securely retrieve Twilio credentials from environment variables only
TWILIO_ACCOUNT_SID = "ACa40390c4cf9e7147cd2576f8b47d1dd4"
TWILIO_AUTH_TOKEN = "1cfa823a4a8de399a3fd8500e293c7bd"
TWILIO_PHONE_NUMBER = "+14432781993"

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
                subject="Password Reset OTP",
                message=f"Your gmail OTP is: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            return {"success": True, "message": "OTP sent to email."}
        except Exception as e:
            return {"success": False, "message": f"Failed to send OTP: {str(e)}"}

# Reset password link in mail 
def send_password_reset_link(user):
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        token = serializer.dumps(user.email, salt='password-reset-salt')
        reset_link = f"http://localhost:4200/reset-password/?token={token}"
        subject = "Password Reset Request"
        message = f"Hi {user.first_name} {user.last_name},\n\nClick the link below to reset your password. This link is valid for 5 minutes.\n{reset_link}"    
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
