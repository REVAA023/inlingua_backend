from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import StudentDetails, ClassRoom, Trainer, Language, CourseType, ClassRecord
from api.serializers import StudentDetailsSerializer, ClassRoomSerializer, TrainerDetailsSerializer, ClassRecordSerializer
from api.views.common import send_password_reset_link
from datetime import datetime

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_batch(request):
    try:
        if request.user.user_role == "SUSER":
            classes = ClassRoom.objects.all()
        elif request.user.user_role == "TRAINER":
            trainer = Trainer.objects.get(user=request.user)
            classes = ClassRoom.objects.filter(trainer=trainer).distinct()
        serializer = ClassRoomSerializer(classes, many=True)
        return Response({"status": True, "class": serializer.data[::-1]}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_students_and_trainers(request):
    try:
        batch_type       = request.data.get("BatchType")
        batch_pref       = request.data.get("batchPreferences")  
        course_levels_id = request.data.get("courseLevels")
        start_time       = request.data.get("startTime")
        end_time         = request.data.get("endTime")
        language_id      = request.data.get("language")

        students_qs = StudentDetails.objects.filter(
            mode_of_class=batch_type,
            course_type_id=course_levels_id,
            language_id=language_id,
            student_status="VERIFYD",
            classroom__isnull=True,
        ).select_related("user") 

        trainers_qs = Trainer.objects.filter(
            languages__id=language_id,
            is_verify=True,
            is_deleted=False,
        ).select_related("user").distinct()

        def qs_to_min_list(qs):
            return [
                {   "id": obj.id,
                    "name": f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.first_name 
                }
                for obj in qs
            ]
        return Response(
            {
                "status": True,
                "students": qs_to_min_list(students_qs),
                "trainers": qs_to_min_list(trainers_qs),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as exc:
        return Response(
            {"status": False, "message": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_batch(request):
    try:
        def conver_time(time):
            return datetime.strptime(time, "%I:%M %p").time()
        def conver_date(date):
            return datetime.strptime(date, "%d-%m-%Y").date()
        def create_name(language, level, batch_preferences, batch_type, start_date):
            def ordinal(n: int) -> str:
                return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"

            def format_date_string(date_obj):
                return f"{ordinal(date_obj.day)} {date_obj.strftime('%b').upper()}"

            formatted_date = format_date_string(start_date)

            return f"{language.upper()} {level.upper()} {batch_preferences.upper()} {batch_type.upper()} {formatted_date}"

            
        
        newBatchForm = request.data.get("newBatchForm")
        get_language = Language.objects.get(pk=newBatchForm['language'])
        get_course_level = CourseType.objects.get(pk=newBatchForm['courseLevel'])
        batchPreferences = newBatchForm['batchPreferences']
        batchType = newBatchForm['batchType']
        startTime = conver_time(newBatchForm['startTime'])
        endTime = conver_time(newBatchForm['endTime'])
        startDate = conver_date(newBatchForm['startDate'])
        endDate = conver_date(newBatchForm['endDate'])
        studentList = newBatchForm['studentList']
        trainerID = newBatchForm['trainerID']
        
        # 1. Create the classroom
        new_batch = ClassRoom.objects.create(
            name=create_name(get_language.context, get_course_level.context, batchPreferences, batchType, startDate),
            language=get_language,
            course_type=get_course_level,
            start_date=startDate,
            end_date=endDate,
            start_time=startTime,
            end_time=endTime,
            mode_of_class=batchType,
            batch_preferences=batchPreferences,
            trainer=Trainer.objects.get(pk=trainerID),
            students_list=0,
            is_active=False,
            is_complited=0,
            created_by=request.user 
        )

        for student_id in studentList:
            student = StudentDetails.objects.get(pk=student_id)
            student.classroom = new_batch
            student.student_status = 'BATCH_ALLOCATED'
            student.save()

        new_batch.students_list = len(studentList)
        new_batch.save()

        return Response({"status": True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def batch_profile(request):
    try:
        batch_id = request.data.get("batchId")
        if not batch_id:
            return Response({"status": False, "message": "batchId is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the batch instance
        batch = ClassRoom.objects.get(id=batch_id)

        # Get all students in the batch
        students = StudentDetails.objects.filter(classroom=batch)
        
        # get related trainers
        related_trainers = Trainer.objects.filter(languages=batch.language, is_verify=True, is_deleted=False).distinct()
        related_trainers_serializer = TrainerDetailsSerializer(related_trainers, many=True)
     
        related_students = StudentDetails.objects.filter(
            mode_of_class=batch.mode_of_class,
            course_type=batch.course_type,
            language=batch.language,
            student_status="VERIFYD",
            classroom=None,
            is_deleted=False
        ).select_related("user")
        related_students_serializer = StudentDetailsSerializer(related_students, many=True)

        # Serialize data
        batch_serializer = ClassRoomSerializer(batch)
        students_serializer = StudentDetailsSerializer(students, many=True)
        
        # class records video
        getVideos =  ClassRecord.objects.filter(
            class_room = batch
        )
        getVideos_serializer = ClassRecordSerializer(getVideos, many=True)

        return Response({
            "status": True,
            "batch": batch_serializer.data,
            "students": students_serializer.data,
            "related_trainers": related_trainers_serializer.data,
            "related_students": related_students_serializer.data,
            "get_videos": getVideos_serializer.data,
        }, status=status.HTTP_200_OK)

    except ClassRoom.DoesNotExist:
        return Response({"status": False, "message": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def batch_profile_change_trainer(request):
    try:
        trainer_id = request.data.get("trainerId")
        batch_id = request.data.get("batchId")
        
        get_batch = ClassRoom.objects.get(id=batch_id)
        get_batch.trainer = Trainer.objects.get(id=trainer_id)
        get_batch.save()
        return Response({ "status": True, }, status=status.HTTP_200_OK)
        
    except Exception as e:
        pass

@api_view(["POST"])
@permission_classes([IsAuthenticated])    
def batch_profile_remove_student(request):
    try:
        student_id = request.data.get("studentId")
        get_student = StudentDetails.objects.get(id=student_id)
        get_student.classroom = None
        get_student.student_status = "VERIFYD"
        get_student.save()
        return Response({ "status": True, }, status=status.HTTP_200_OK)
    except Exception as e:
        pass
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])    
def batch_profile_add_student(request):
    try:
        student_id = request.data.get("studentId")
        batch_id = request.data.get("batchId")
        get_student = StudentDetails.objects.get(id=student_id)
        get_student.classroom = ClassRoom.objects.get(id=batch_id)
        get_student.student_status = "BATCH_ALLOCATED"
        get_student.save()
        
        return Response({ "status": True }, status=status.HTTP_200_OK)
        
    except Exception as e:
        pass

@api_view(["POST"])
@permission_classes([IsAuthenticated])    
def batch_google_meet_link_update(request):
    try:
        googleMeetLink = request.data.get("googleMeetLink")
        batchId = request.data.get("batchId")
        
        classroom = ClassRoom.objects.get(id=batchId)
        classroom.google_meet_link = googleMeetLink
        classroom.save()
        
        return Response({ "status": True, }, status=status.HTTP_200_OK)
        
    except Exception as e:
        pass
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])    
def batch_complited_update(request):
    try:
        Complited = request.data.get("Complited")
        batchId = request.data.get("batchId")
        
        classroom = ClassRoom.objects.get(id=batchId)
        classroom.is_complited = Complited
        classroom.save()
        
        return Response({ "status": True, }, status=status.HTTP_200_OK)
        
    except Exception as e:
        pass
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])    
def start_class(request):
    try:
        batchId = request.data.get("batchId")
        
        classroom = ClassRoom.objects.get(id=batchId)
        classroom.is_active = True
        classroom.save()
        
        return Response({ "status": True, }, status=status.HTTP_200_OK)
        
    except Exception as e:
        pass
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])    
def end_class(request):
    try:
        batchId = request.data.get("batchId")
        
        classroom = ClassRoom.objects.get(id=batchId)
        classroom.is_active = False
        classroom.save()
        
        return Response({ "status": True, }, status=status.HTTP_200_OK)
        
    except Exception as e:
        pass
    
