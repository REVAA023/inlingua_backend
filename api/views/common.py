import random
import base64
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.core.files.base import ContentFile
# from inlingua_backend import settings

# REST Framework imports
from rest_framework import status
from rest_framework.response import Response

# Third-party imports
from twilio.rest import Client
from itsdangerous import URLSafeTimedSerializer

# Local imports
from api.models import OTP, StudyMaterial

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
            return {"status": False, "message": "Mobile number is required."}

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
            return {"status": True, "message": "OTP sent successfully."}
        except Exception as e:
            return {"status": False, "message": f"Failed to send OTP: {str(e)}"}

    def send_email_otp(self, email):
        if not email:
            return {"status": False, "message": "Email is required."}

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
            return {"status": True, "message": "OTP sent to email."}
        except Exception as e:
            return {"status": False, "message": f"Failed to send OTP: {str(e)}"}

# Reset password link in mail 
def generate_password_reset_token(email):
    """Generate a secure token for password reset."""
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = serializer.dumps(email, salt='password-reset-salt')
    return token

def send_password_reset_link(user):
    """Send password reset link to user's email."""
    try:
        url = settings.URL
        print(f"Settings URL: {url}")
        token = generate_password_reset_token(user.email)
        reset_link = f"{settings.URL}reset-password/?token={token}"

        subject = 'Reset Your Password'
        message = f"""
        Hi {user.first_name} {user.last_name},

        We received a request to reset your password.

        Click the link below to set a new password. This link is valid for 24 hours and can be used only once:

        {reset_link}

        If you didn't request this, please ignore this email.

        Thanks,  
        Inlingua Team
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
        
        return {"status": True, "message": "Password reset link sent successfully."}
        
    except Exception as e:
        print(f"Error sending password reset link: {e}")
        return {"status": False, "message": f"Failed to send password reset link: {str(e)}"}

def base64_to_pdf_bytes(base64_string):
    """
    Converts a Base64 string representing a PDF to PDF bytes (in memory).
    
    Args:
        base64_string: The Base64 encoded string.
    
    Returns:
        bytes: The PDF content as bytes, or None if conversion fails.
    """
    try:
        # Remove the prefix "data:application/pdf;base64," if present
        if base64_string.startswith("data:application/pdf;base64,"):
            base64_string = base64_string.split("data:application/pdf;base64,")[1]
        
        # Remove any whitespace or newlines that might be present
        base64_string = base64_string.strip().replace('\n', '').replace('\r', '')
        
        # Decode the Base64 string to bytes
        pdf_bytes = base64.b64decode(base64_string)
        return pdf_bytes
    except Exception as e:
        print(f"Error converting Base64 to PDF bytes: {e}")
        return None

def send_students_register_mail(student):
    try:
        # Get study material for the student
        get_document = StudyMaterial.objects.filter(
            language=student.language.id,
            language_level=student.course_type.id,
            payment_type=student.payment_type
        )
        
        if not get_document.exists():
            return {
                "status": False,
                "message": "No study material found for the selected language and course type."
            }
        
        document = get_document.first()
        
        # Email content
        subject = 'Welcome to Inlingua - Your Study Materials'
        message = f"""
        Hi {student.user.first_name} {student.user.last_name},

        Welcome to Inlingua! Your account has been successfully created.

        We've attached your study materials for {student.language.name} - {student.course_type.level}.

        You can now log in to your account and start using our services.

        Thanks,  
        Inlingua Team
        """
        
        # Create EmailMessage object for attachment support
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email='test.inlingua@revaadigital.com',
            to=[student.user.email],
        )
        
        def base64_to_pdf_data(base64_string):
            """
            Convert Base64 string to PDF bytes data
            Returns the PDF data as bytes
            """
            try:
                # Remove the prefix "data:application/pdf;base64," if present
                if base64_string.startswith("data:application/pdf;base64,"):
                    base64_string = base64_string.split("data:application/pdf;base64,")[1]
                
                # Decode the Base64 string to bytes
                pdf_bytes = base64.b64decode(base64_string)
                
                return pdf_bytes
                
            except Exception as e:
                print(f"Error converting Base64 to PDF: {e}")
                return None
        
        # Convert Base64 to PDF bytes
        if document.documents and document.documents.document_contant:  # Make sure document content exists
            pdf_bytes = base64_to_pdf_data(document.documents.document_contant)
            
            if pdf_bytes:
                # Attach PDF to email without saving to disk
                filename = f"{document.documents.document_name}.pdf" if not document.documents.document_name.endswith('.pdf') else document.documents.document_name
                email.attach(filename, pdf_bytes, 'application/pdf')
            else:
                return {
                    "status": False,
                    "message": "Failed to convert document to PDF format."
                }
        else:
            return {
                "status": False,
                "message": "Document content is empty or invalid."
            }
        
        # Send the email
        email.send(fail_silently=False)
        
        return {"status": True, "message": "Welcome email sent successfully with study materials."}
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return {"status": False, "message": f"Failed to send welcome email: {str(e)}"}