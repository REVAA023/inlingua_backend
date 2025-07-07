from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from api.serializers import  CustomUserSerializer
from api.models import CustomUser, Trainer
from api.views.common import send_password_reset_link
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from django.conf import settings

@csrf_exempt
@api_view(["GET"])
def get_token(request):
    key = Fernet.generate_key()
    return Response({"token": key.decode()})

@api_view(["POST"])
def user_login(request):
    identifier = request.data.get("identifier")
    password = request.data.get("password")

    if not identifier or not password:
        return Response(
            {"message": "email or mobile number and password are required."},
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
        access_token = str(refresh.access_token)
        serializer = CustomUserSerializer(user)
        return Response(
            {
                "token": access_token,
                "userData": serializer.data
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"message": "Invalid ( email, mobile number ) or password."},
            status=status.HTTP_404_NOT_FOUND,
        )

@api_view(["POST"])
def reset_password_link(request):
    email = request.data.get("email")
    try:
        validate_email(email)
        user = CustomUser.objects.get(email=email)
        send_password_reset_link(user)
        return Response({"success": "Successfully sent password reset link to your email."}, status=status.HTTP_200_OK)
    except (ValidationError):
        return Response({"message": "Invalid email"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST']) 
def check_password_token(request):
    token = request.data.get("token")
    if not token:
        return Response({"message": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=86400)
        return Response({"success": True}, status=status.HTTP_200_OK)
    except SignatureExpired:
        return Response({"message": "This reset link has expired."}, status=status.HTTP_400_BAD_REQUEST)
    except BadSignature:
        return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST']) 
def create_new_password(request):
    token = request.data.get("token")
    new_password = request.data.get("password")

    if not token or not new_password:
        return Response({"message": "Token and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        # Validate the token (24 hours = 86400 seconds)
        email = serializer.loads(token, salt="password-reset-salt", max_age=86400)

        try:
            user = CustomUser.objects.get(email=email)

            # Check if token matches the one stored
            if user.password_reset_token != token:
                return Response({"message": "This link has already been used."}, status=status.HTTP_400_BAD_REQUEST)

            # Set new password securely
            user.set_password(new_password)
            user.is_verified = True  # Mark user as verified
            user.is_active = True  # Activate the user account
            
            user.password_reset_token = None  # Invalidate token
            user.password_reset_token_created_at = None
            user.save()
            
            if user.user_role == "TRAINER":
                trainer = Trainer.objects.get(user=user)
                trainer.is_verify = True
                trainer.save()

            return Response({"flag":True,"message": "Password has been reset successfully."}, status=status.HTTP_201_CREATED)

        except CustomUser.DoesNotExist:
            return Response({"flag":False,"message": "Invalid user."}, status=status.HTTP_404_NOT_FOUND)

    except SignatureExpired:
        return Response({"flag":False,"message": "This reset link has expired."}, status=status.HTTP_400_BAD_REQUEST)

    except BadSignature:
        return Response({"flag":False,"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
     
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get("currentPassword")
    new_password = request.data.get("newPassword")
    confirm_password = request.data.get("confirmPassword")

    if not current_password or not new_password or not confirm_password:
        return Response(
            {"message": "All fields (currentPassword, newPassword, confirmPassword) are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user
    if not user.check_password(current_password):
        return Response(
            {"message": "Current password is incorrect."},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    if current_password == new_password :
        return Response({"message": "New password cannot be the same as the current password."}, status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response(
            {"message": "New password and confirm password do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()

    return Response(
        {"message": "Password changed successfully."},
        status=status.HTTP_200_OK,
    )