from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import ClassRecord, ClassRoom, Documents, StudentDetails
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from datetime import timedelta

# CREATE - Create a new class record
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_class_record(request):
    try:
        batch_id = request.data.get("batchId")
        notes = request.data.get("note")
        video_data = request.data.get("video")
        
        if not batch_id:
            return Response({
                "status": False, 
                "message": "Batch ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not notes:
            return Response({
                "status": False, 
                "message": "Notes are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            classroom = ClassRoom.objects.get(id=batch_id)
        except ClassRoom.DoesNotExist:
            return Response({
                "status": False, 
                "message": "Classroom not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        document = None
        if video_data:
            if not video_data.get("documentsExtention", "").startswith("video/"):
                return Response({
                    "status": False, 
                    "message": "Invalid video file format. Only video files are allowed."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            document = Documents.objects.create(
                document_name=video_data.get("documentName", ""),
                document_size=video_data.get("documentSize", ""),
                documents_extention=video_data.get("documentsExtention", ""),
                document_contant=video_data.get("documentContant", ""),
            )
        
        class_record = ClassRecord.objects.create(
            class_room=classroom,
            document=document,
            notes=notes,
            created_by=request.user,
            created_date=timezone.now()
        )
        
        try:
            get_students = StudentDetails.objects.filter(classroom=classroom)
            if get_students.exists():
                class_record.attendance.set(get_students)
        except Exception as e:
            return Response({
                "status": False, 
                "message": f"Error adding attendance: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "status": True, 
            "message": "Class record created successfully", 
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            "status": False, 
            "message": f"Internal server error: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_video(request):
    try:
        studentId = request.data.get("studentId")
        videoId = request.data.get("videoId")
        
        # set student
        get_student = StudentDetails.objects.get(pk=studentId)
        get_student.class_video_record = ClassRecord.objects.get(pk=videoId)
        # after 1 days 
        get_student.class_video_record_expiry = timezone.now() + timedelta(days=1)
        get_student.save()
        return Response({
                "status": True, 
                "message": "Video Send Successfully"
            }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": False, 
            "message": f"Video Not send Error : {str(e)}"
            }, status=status.HTTP_200_OK)