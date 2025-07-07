from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import Counselor, CustomUser, Documents
from api.serializers import CounselorSerializer
from api.views.common import send_password_reset_link

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def all_counselors(request):
    try:
        counselors = Counselor.objects.all()
        serializer = CounselorSerializer(counselors, many=True)
        return Response({"status": True, "counselors": serializer.data[::-1]}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_counselors(request):
    try:
        firstName = request.data.get("firstName")
        lastName = request.data.get("lastName")
        email = request.data.get("email")
        mobileNumber = request.data.get("mobileNumber")
        dateofbirth = request.data.get("dateofbirth")
        counselorPhoto = request.data.get("counselorPhoto")
        
        new_user = CustomUser.objects.create(
            first_name=firstName,
            last_name=lastName,
            email=email,
            mobile_number=mobileNumber,
            date_of_birth =datetime.strptime(dateofbirth, "%d-%m-%Y").date(),
            user_role='COUNSELOR',
            is_verified=True,
            is_active=True,
            is_staff=False
        )
        if counselorPhoto:
            new_document = Documents.objects.create(
                document_name = counselorPhoto.get("documentName"),
                document_size = counselorPhoto.get("documentSize"),
                documents_extention = counselorPhoto.get("documentsExtention"),
                document_contant = counselorPhoto.get("documentContant"),
                created_date = counselorPhoto.get("createdDate"),
            )
            new_user.photo = new_document
            new_user.save()
        
        Counselor.objects.create(
            user=new_user,
            created_by =request.user,
        )
        
        return Response({"status": True, "message": "Create counselors Successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    