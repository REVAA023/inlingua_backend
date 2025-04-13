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

def generate_activation_url(user):
    token_data = {
        "email": user.email,
        "timestamp": now().timestamp()
    }

    token = signing.dumps(token_data, salt="activation_salt")
    url = reverse('activate_account')
    return f"{settings.FRONTEND_URL}{url}?token={token}"

def send_welcome_email(user):
    try:
        subject = "Welcome to LMS"
        html_message = render_to_string(
            'welcome_mail.html', {
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        )
        from_email = "no-reply@example.com"
        recipient_list = [user.email]
        send_mail(subject, "", from_email, recipient_list, html_message=html_message)
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")

def activate_account(request):
    token = request.GET.get('token')

    if not token:
        return HttpResponse('No token provided.', status=400)

    try:
        token_data = signing.loads(token, salt="activation_salt", max_age=300)
        email = token_data.get("email")

        if UserToken.objects.filter(token=token).exists():
            return HttpResponse('This activation link has already been used.', status=400)

        user = CustomUser.objects.get(email=email)
        user.is_active = True
        user.is_staff = True
        user.save()
        send_welcome_email(user)

        UserToken.objects.create(token=token, email=email)

        return redirect('http://192.168.1.4:8080/admin/')

    except signing.SignatureExpired:
        return HttpResponse('Activation link has expired.', status=400)
    except signing.BadSignature:
        return HttpResponse('Invalid activation link.', status=400)
    except ObjectDoesNotExist:
        return HttpResponse('User not found.', status=400)

def send_access_email(user):
    try:
        subject = "Access Granted"
        html_message = render_to_string(
            'send_access_email.html', {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'url': generate_activation_url(user),
            }
        )
        from_email = "no-reply@example.com"
        recipient_list = [user.email]
        send_mail(subject, "", from_email, recipient_list, html_message=html_message)
    except Exception as e:
        print(f"Error sending access email: {str(e)}")
