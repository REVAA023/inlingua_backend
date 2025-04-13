from datetime import datetime
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from api.serializers import StudentDetailsSerializer, CustomUserSerializer
from api.models import CustomUser, OTP
from api.views.common import OTPService, send_access_email
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
import random
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core import signing
from django.http import HttpResponse
from django.shortcuts import render

@api_view(["POST"])
def students_register(request):
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name", "")
    photo = request.data.get("photo")
    email = request.data.get("email")
    mobile_number = request.data.get("mobile_number")
    aadhar = request.data.get("aadhar")
    professions = request.data.get("professions")
    language = request.data.get("language")
    level_and_hours = request.data.get("level_and_hours")
    batch_preferences = request.data.get("batch_preferences")
    student_status = request.data.get("student_status")
    student_type = request.data.get("student_type")
    payment_type = request.data.get("payment_type")
    transaction_id = request.data.get("transaction_id")
    account_holder_name = request.data.get("account_holder_name")
    amount_paide = request.data.get("amount_paide")
    balance_amount = request.data.get("balance_amount")
    payment_complited = request.data.get("payment_complited")
    
    if ( not first_name 
        and not email 
        and not mobile_number 
        and not aadhar 
        and not professions 
        and not language 
        and not level_and_hours 
        and not batch_preferences 
        and not payment_type 
        and not transaction_id 
        and not account_holder_name 
        and not amount_paide 
        and not balance_amount 
        and not payment_complited):
        return Response(
            {"message":"Fill all the fields"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    if CustomUser.objects.filter(email=email).exists():
        return Response(
            {"error": "A user with this email already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if CustomUser.objects.filter(mobile_number=mobile_number).exists():
        return Response(
            {"error": "A user with this mobile number already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    otp_service = OTPService()
    otp_response = otp_service.send_otp(mobile_number)
    email_responce = otp_service.send_email_otp(email)

    if not otp_response.get("success"):
        return Response(
            {"error": "Failed to send OTP."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    if not email_responce.get("success"):
        return Response(
            {"error": "Failed to send Gmail OTP."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    request.session["first_name"] = first_name
    request.session["last_name"] = last_name
    request.session["photo"] = photo
    request.session["email"] = email
    request.session["mobile_number"] = mobile_number
    request.session["aadhar"] = aadhar
    request.session["professions"] = professions
    request.session["language"] = language
    request.session["level_and_hours"] = level_and_hours
    request.session["batch_preferences"] = batch_preferences
    request.session["student_status"] = student_status
    request.session["student_type"] = student_type
    request.session["payment_type"] = payment_type
    request.session["transaction_id"] = transaction_id
    request.session["account_holder_name"] = account_holder_name
    request.session["amount_paide"] = amount_paide
    request.session["balance_amount"] = balance_amount
    request.session["payment_complited"] = payment_complited
    
    return Response(
        {"message": "OTP sent to your mobile number and Gmail. Please verify."},
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
def student_account_verify(request):
    session_data = {
        "mobile_number": request.session.get("mobile_number"),
        "email": request.session.get("email"),
        "first_name": request.session.get("first_name"),
        "last_name": request.session.get("last_name"),
        "photo": request.session.get("photo"),
        "aadhar": request.session.get("aadhar"),
        "professions": request.session.get("professions"),
        "language": request.session.get("language"),
        "level_and_hours": request.session.get("level_and_hours"),
        "batch_preferences": request.session.get("batch_preferences"),
        "student_status": request.session.get("student_status"),
        "student_type": request.session.get("student_type"),
        "payment_type": request.session.get("payment_type"),
        "transaction_id": request.session.get("transaction_id"),
        "account_holder_name": request.session.get("account_holder_name"),
        "amount_paide": request.session.get("amount_paide"),
        "balance_amount": request.session.get("balance_amount"),
    }
    
    student_counselor = CustomUser.objects.get(pk=1)
    print(student_counselor)

    mobile_otp_input = request.data.get("mobile_otp")
    email_otp_input = request.data.get("email_otp")

    # Check if all fields exist
    if not all([session_data["mobile_number"], session_data["email"], mobile_otp_input, email_otp_input]):
        return Response({"error": "All required fields must be provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate mobile OTP
    try:
        mobile_otp = OTP.objects.get(mobile_number=session_data["mobile_number"])
        if mobile_otp.otp != mobile_otp_input:
            return Response({"error": "Invalid OTP for mobile number."}, status=status.HTTP_400_BAD_REQUEST)
        if mobile_otp.expires_at < timezone.now():
            return Response({"error": "OTP for mobile number has expired."}, status=status.HTTP_400_BAD_REQUEST)
    except OTP.DoesNotExist:
        return Response({"error": "Mobile OTP not found."}, status=status.HTTP_404_NOT_FOUND)

    # Validate email OTP
    try:
        email_otp = OTP.objects.get(mobile_number=session_data["email"])
        if email_otp.otp != email_otp_input:
            return Response({"error": "Invalid OTP for email."}, status=status.HTTP_400_BAD_REQUEST)
        if email_otp.expires_at < timezone.now():
            return Response({"error": "OTP for email has expired."}, status=status.HTTP_400_BAD_REQUEST)
    except OTP.DoesNotExist:
        return Response({"error": "Email OTP not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check user existence
    if CustomUser.objects.filter(mobile_number=session_data["mobile_number"]).exists():
        return Response({"error": "User with this mobile number already exists."}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(email=session_data["email"]).exists():
        return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    user = CustomUser.objects.create(
        first_name=session_data["first_name"],
        last_name=session_data["last_name"],
        mobile_number=session_data["mobile_number"],
        email=session_data["email"],
        photo=session_data["photo"],
        user_role = "STUDENT",
        is_active=False
    )

    # Prepare student data
    student_data = {
        "user": user.pk,
        "aadhar": session_data["aadhar"],
        "professions": session_data["professions"],
        "language": session_data["language"],
        "level_and_hours": session_data["level_and_hours"],
        "batch_preferences": session_data["batch_preferences"],
        "Student_counselor" : student_counselor.pk,
        "student_status": session_data["student_status"],
        "student_type": session_data["student_type"],
        "payment_type": session_data["payment_type"],
        "transaction_id": session_data["transaction_id"],
        "account_holder_name": session_data["account_holder_name"],
        "amount_paide": session_data["amount_paide"],
        "balance_amount": session_data["balance_amount"],
        "payment_complited": False,
        "created_by": student_counselor.pk,
    }
    try:
        serializer = StudentDetailsSerializer(data=student_data)
        if serializer.is_valid():
            serializer.save()
            request.session.flush()
            return Response({"message": "Account verified and student registered successfully."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def user_login(request):
    identifier = request.data.get("identifier")
    password = request.data.get("password")

    if not identifier or not password:
        return Response(
            {"error": "email or mobile number and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        validate_email(identifier)
        is_email = True
    except ValidationError:
        is_email = False

    if is_email:
        user = CustomUser.objects.filter(email=identifier).first()
    else:
        user = CustomUser.objects.filter(mobile_number=identifier).first()

    if user and user.check_password(password):
        user.last_login = datetime.now()
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "token": str(refresh.access_token),
                "userData": CustomUserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": "Invalid ( email, mobile number ) or password."},
            status=status.HTTP_404_NOT_FOUND,
        )

@api_view(["POST"])
def forget_password_otp(request):
    identifier = request.data.get("identifier")
    if not identifier:
        return Response(
            {"error": "Identifier (email or mobile number) is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        # Check if identifier is email
        int(identifier)
        is_email = True
    except :
        is_email = False

    # Handle Gmail OTP
    if not is_email:
        user = CustomUser.objects.filter(email=identifier).first()
        if user:
            reset_token = random.randint(100000, 999999)
            send_mail(
                subject="Password Reset Request",
                message=f"Your password reset token is {reset_token}.",
                from_email="no-reply@example.com",  # Replace with your sender email
                recipient_list=[user.email],
            )
            # Store the reset token in session or temporary storage
            request.session["reset_token"] = reset_token
            return Response(
                {"message": f"A password reset token has been sent to {identifier}."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No account associated with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )
    
    # Handle Mobile Number OTP
    else:
        user = CustomUser.objects.filter(mobile_number=identifier).first()
        if user:
            otp = random.randint(100000, 999999)
            # Call the function to send OTP via Twilio or other services
            # send_otp(identifier, otp)
            # Store OTP in session or temporary storage
            request.session["otp"] = otp
            return Response(
                {"message": f"A password reset OTP has been sent to {identifier}."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No account associated with this mobile number."},
                status=status.HTTP_404_NOT_FOUND,
            )

@api_view(["POST"])
def forget_password_otp_verify(request):
    identifier = request.data.get("identifier")
    otp = request.data.get("otp")

    if not identifier or not otp:
        return Response(
            {"error": "Identifier (email or mobile number) and OTP are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(identifier)
        is_email = True
    except ValidationError:
        is_email = False

    # Verify Email-based OTP
    if is_email:
        user = CustomUser.objects.filter(email=identifier).first()
        if user and otp == str(request.session.get("reset_token")):
            return Response(
                {"message": "OTP verified successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid OTP or email."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    # Verify Mobile Number-based OTP
    else:
        user = CustomUser.objects.filter(mobile_number=identifier).first()
        if user and otp == str(request.session.get("otp")):
            return Response(
                {"message": "OTP verified successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid OTP or mobile number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

@api_view(["POST"])
def change_forget_password(request):
    identifier = request.data.get("identifier")
    password = request.data.get("password")
    confirm_password = request.data.get("confirmPassword")

    if not identifier or not password or not confirm_password:
        return Response(
            {"error": "Identifier, password, and confirm password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != confirm_password:
        return Response(
            {"error": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(identifier)
        is_email = True
    except ValidationError:
        is_email = False

    if is_email:
        user = CustomUser.objects.filter(email=identifier).first()
        if user:
            user.set_password(password)
            user.save()
            return Response(
                {"message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No account associated with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

    else:
        user = CustomUser.objects.filter(mobile_number=identifier).first()
        if user:
            user.set_password(password)
            user.save()
            return Response(
                {"message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No account associated with this mobile number."},
                status=status.HTTP_404_NOT_FOUND,
            )        
        
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get("currentPassword")
    new_password = request.data.get("newPassword")
    confirm_password = request.data.get("confirmPassword")

    if not current_password or not new_password or not confirm_password:
        return Response(
            {"error": "All fields (currentPassword, newPassword, confirmPassword) are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user
    if not user.check_password(current_password):
        return Response(
            {"error": "Current password is incorrect."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_password != confirm_password:
        return Response(
            {"error": "New password and confirm password do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()

    return Response(
        {"message": "Password changed successfully."},
        status=status.HTTP_200_OK,
    )