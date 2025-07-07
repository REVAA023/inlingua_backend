from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import OTP, CustomUser, Language, CourseType, StudentDetails,Counselor, History, ClassRoom
from api.serializers import DocumentSerializer, LanguagesSerializer, CourseTyperSerializer, StudentDetailsSerializer
from django.views.decorators.csrf import csrf_exempt
from api.views.common import OTPService
from django.contrib.contenttypes.models import ContentType

# Forms

@api_view(["GET"])
def show_languages(request):
    try:
        languages = Language.objects.all()
        serializer = LanguagesSerializer(languages, many=True)
        return Response({"status": True, "languages": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def show_levelandhour(request):
    try:
        level_and_hour_id = request.data.get("levelId")
        if not level_and_hour_id:
            return Response({"status": False, "message": "Identifier is required"},status=status.HTTP_400_BAD_REQUEST)

        level_and_hour = CourseType.objects.filter(language=level_and_hour_id)
        
        # Serialize the object
        serializer = CourseTyperSerializer(level_and_hour, many=True)
        
        return Response({"status": True, "Levelandhours": serializer.data}, status=status.HTTP_200_OK)
    
    except CourseType.DoesNotExist:
        return Response(
            {"status": False, "message": "No record found with the given identifier"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"status": False, "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_choices(choices):
    return [{"value": key, "label": label} for key, label in choices]

@api_view(["GET"])
def student_details(request):
    try:
        data = {
            "PROFESSIONS_CHOICES": get_choices(StudentDetails.PROFESSIONS_CHOICES),
            "BATCH_TYPE_CHOICES": get_choices(StudentDetails.MODE_OF_CLASS),
            "PAYMENT_TYPE_CHOICES": get_choices(StudentDetails.PAYMENT_TYPE_CHOICES),
            "STUDENT_STATUS_CHOICES": get_choices(StudentDetails.STATUS_CHOICES),
            "BATCH_PREFERENCES_CHOICES": get_choices(ClassRoom.BATCH_PREFERENCES_CHOICES),
        }
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["GET"])
def student_counselor(request):
    counselors = Counselor.objects.select_related('user').all()
    
    data = [
        {
            "id": counselor.user.id,
            "fullName": f"{counselor.user.first_name} {counselor.user.last_name}"
        }
        for counselor in counselors
    ]

    return Response({
        "status": True,
        "counselors": data
    }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def otp_sender(request):
    email = request.data.get("gmail")

    
    otp_service = OTPService()
    # otp_response = otp_service.send_otp(mobile_number)
    # email_responce = otp_service.send_email_otp(email)

    # if not otp_response.get("success"):
    #     return Response(
    #         {"message": "Failed to send Mobile OTP."},
    #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #     )
    # if not email_responce.get("success"):
    #     return Response(
    #         {"message": "Failed to send Gmail OTP."},
    #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #     )

    return Response(
        {"message": "OTP sent to your mobile number and Gmail. Please verify."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def student_account_verify(request):
    numberotp = request.data.get("numberotp")
    gmailotp = request.data.get("gmailotp")
    data = request.data.get("parsed")

    if not data:
        return Response({"message": "Parsed student data missing."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        email = data.get("gmail")
        first_name = data.get("FirstName")
        last_name = data.get("LastName")
        mobile_number = data.get("MobileNumber")
        date_of_birth = data.get("dob")
        language_id = data.get("languageId")
        course_type_id = data.get("courseTypeId")
        mode_of_class = data.get("modeOfClass")
        counselor_id = data.get("counselorId")
        transaction_id = data.get("TransactionId")
        proof_of_screenshot = data.get("paymentScreenShot")
        account_holder_name = data.get("accountHolderName")
        payment_type = data.get("amountPaid")
        amount_paid = data.get("amount")
        aadhar = data.get("aadharCard")
        professions = data.get("professions")
        is_aggry = data.get("isaggery")
        photo = data.get("studentPhoto")
        
        language = Language.objects.get(id=language_id)
        course_type = CourseType.objects.get(id=course_type_id)
        try:
            counselor_user = CustomUser.objects.get(id=counselor_id)
            counselor = Counselor.objects.get(user=counselor_user)
        except Counselor.DoesNotExist:
            return Response({"message": f"Counselor with id {counselor_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user and existing_user.is_verified:
            return Response({"message": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(mobile_number=mobile_number).exclude(email=email).exists():
            return Response({"message": "A user with this mobile number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # gmail_otp_obj = OTP.objects.filter(mobile_number=email).first()
        # if not gmail_otp_obj or str(gmail_otp_obj.otp) != str(gmailotp):
        #     return Response({"message": "Invalid OTP for Gmail."}, status=status.HTTP_400_BAD_REQUEST)

        # Save documents
        # Updated save_document with better validation
        def save_document(doc):
            if not doc:
                return None

            required_fields = ["documentName", "documentSize", "documentsExtention", "documentContant"]
            if not all(doc.get(field) for field in required_fields):
                return None

            serializer = DocumentSerializer(data={
                'document_name': doc.get("documentName"),
                'document_size': doc.get("documentSize"),
                'documents_extention': doc.get("documentsExtention"),
                'document_contant': doc.get("documentContant"),
                'created_date': timezone.now()
            })
            serializer.is_valid(raise_exception=True)
            return serializer.save()
        
        photo_instance = save_document(photo)
        aadhar_instance = save_document(aadhar)
        payment_instance = save_document(proof_of_screenshot)



        if not existing_user:
            user = CustomUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                photo=photo_instance,
                mobile_number=mobile_number,
                date_of_birth=datetime.strptime(date_of_birth, "%d-%m-%Y").date(),
                email=email,
                user_role="STUDENT",
                is_active=False
            )
        else:
            user = existing_user

        

        part_payment_date = datetime.today().date() + timedelta(days=30) if payment_type == "PART" else None

        student = StudentDetails.objects.create(
            user=user,
            aadhar=aadhar_instance,
            professions=professions,
            language=language,
            course_type=course_type,
            mode_of_class=mode_of_class,
            name_of_counselor=counselor,
            payment_type=payment_type,
            classroom = None, 
            transaction_id=transaction_id,
            payment_conform_screenshot=payment_instance,
            account_holder_name=account_holder_name,
            amount_paide=amount_paid,
            payment_complited=False,
            part_payment_date=part_payment_date,
            iaggry=is_aggry,
            created_by=user
        )

        History.objects.create(
            user=user,
            content_type=ContentType.objects.get_for_model(StudentDetails),
            object_id=student.id,
            new_content='Account created',
        )

        # Optional: Cleanup OTPs
        # OTP.objects.filter(mobile_number__in=[email, mobile_number]).delete()

        return Response({'message': 'User verified and student record created successfully.'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"message": f" {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
