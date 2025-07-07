from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import StudentDetails, CustomUser
from api.serializers import StudentDetailsSerializer
from api.views.common import send_password_reset_link

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_student_details(request):
    try:
        students = StudentDetails.objects.all()[::-1]
        serializer = StudentDetailsSerializer(students, many=True)
        return Response({"status": True, "students": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def student_profile(request):
    student_id = request.data.get("studentId")
    try:
        student = StudentDetails.objects.get(id=student_id)
        serializer = StudentDetailsSerializer(student)
        return Response({"status": True, "student": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def student_status_update(request):
    student_id = request.data.get("student_id")
    new_status = request.data.get("status")

    if not student_id or not new_status:
        return Response({"status": False, "message": "Missing student_id or status"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        student = StudentDetails.objects.get(id=student_id)

        if new_status == "VERIFYD":
            send_password_reset_link(student.user)
            student.student_status = new_status
            student.save()
            student.user.is_active = True
            student.user.is_verified = True
            student.user.save()
            
        elif new_status == "COURSE_COMPLETED":
            student.student_status = new_status
            student.save()
            student.user.is_active = False
            student.user.save()

        elif new_status in ["BATCH_ALLOCATED", "WAITING_FOR_ASSESSMENT"]:
            student.student_status = new_status
            student.save()

        elif new_status == "NEW_STUDENT":
            return Response({"status": False, "message": "New Student status change is not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"status": False, "message": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": True, "message": "Student status updated successfully"}, status=status.HTTP_200_OK)

    except StudentDetails.DoesNotExist:
        return Response({"status": False, "message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def student_details(request):
    try:
        user = CustomUser.objects.get(pk = request.data.get("studentId")["id"])
        student = StudentDetails.objects.get(user=user)
        serializer = StudentDetailsSerializer(student)
        return Response({"status": True, "student": serializer.data}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"status": False, "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
    