from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import Trainer, CustomUser, OTP, Language
from api.serializers import TrainerDetailsSerializer, LanguagesSerializer
from api.views.common import send_password_reset_link

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_trainers(request):
    
    try:
        trainers = Trainer.objects.all()
        serializer = TrainerDetailsSerializer(trainers, many=True)
        return Response({"status": True, "trainers": serializer.data[::-1]}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trainer(request):
    gmailOtp = request.data.get("gmailOtp")
    mobileOtp = request.data.get("mobileOtp")
    phoneNumber = request.data.get("phoneNumber")
    selectLanguage = request.data.get("selectLanguage")
    trainerEmail = request.data.get("trainerEmail")
    trainerName = request.data.get("trainerName")
    try:
        if not gmailOtp or not mobileOtp or not phoneNumber or not selectLanguage or not trainerEmail or not trainerName:
            return Response({"status":False, "message": "Fill all details"})
        else:
            existing_user = CustomUser.objects.filter(email=trainerEmail).first()
            if existing_user and existing_user.is_verified:
                return Response({"message": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            if CustomUser.objects.filter(mobile_number=phoneNumber).exclude(email=trainerEmail).exists():
                return Response({"message": "A user with this mobile number already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # try:
            #     email_otp_obj  = OTP.objects.get(mobile_number=trainerEmail)
            #     phone_otp_obj  = OTP.objects.get(mobile_number=phoneNumber)
            # except OTP.DoesNotExist:
            #     return Response( {"status": False, "message": "OTP not found or expired."}, status=status.HTTP_400_BAD_REQUEST )

            # if int(email_otp_obj.otp) != int(gmailOtp):
            #     return Response({"status": False, "message": "Invalid Gmail OTP."},status=status.HTTP_400_BAD_REQUEST,)
            # if int(phone_otp_obj.otp) != int(mobileOtp):
            #     return Response({"status": False, "message": "Invalid mobile OTP."},status=status.HTTP_400_BAD_REQUEST,)
            
            user = CustomUser.objects.create(
                first_name = trainerName,
                email = trainerEmail,
                mobile_number = phoneNumber,
                user_role = 'TRAINER',
                is_verified = False,
                is_active = False,
                is_staff = False
            )
            
            trainer = Trainer.objects.create(
                user = user,
                is_verify = False,
                created_by = request.user
            )
            languages_qs = Language.objects.filter(pk__in=selectLanguage)
            if languages_qs.count() != len(selectLanguage):
                return Response({"status": False, "message": "Invalid language ID(s)."}, status=400)
            trainer.languages.set(languages_qs)
            user.save()
            trainer.save()
            send_password_reset_link(user)
            return Response({"status": True, "message": "Create trainer Successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
