from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import StudyMaterial, Documents, Language, CourseType
from api.serializers import StudyMaterialSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_study_material(request):
    try:
        study_materials = StudyMaterial.objects.all()
        serializer = StudyMaterialSerializer(study_materials, many=True)
        return Response({"status": True, "study_materials": serializer.data[::-1]}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_study_material(request):
    try:
        language_id = request.data.get("languageId")
        course_type_id = request.data.get("courseTypeId")
        payment_type = request.data.get("paymentType")
        uploaded_file = request.data.get("StudyMaterial")
        print(uploaded_file['documentName'])

        if not language_id or not course_type_id or not payment_type or not uploaded_file:
            return Response({"status": False, "message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch related instances
        try:
            language = Language.objects.get(id=language_id)
            course_type = CourseType.objects.get(id=course_type_id)
        except (Language.DoesNotExist, CourseType.DoesNotExist):
            return Response({"status": False, "message": "Invalid language or course type ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Create Document
        document_instance = Documents.objects.create(
            document_name = uploaded_file['documentName'],
            document_size = uploaded_file['documentSize'],
            documents_extention = uploaded_file['documentsExtention'],
            document_contant = uploaded_file['documentContant'],
            created_date =uploaded_file['createdDate'],
            )

        # Create Study Material
        study_material_instance = StudyMaterial.objects.create(
            language=language,
            language_level=course_type,
            payment_type=payment_type,
            documents=document_instance
        )
        study_material_instance.save()

        return Response({"status": True, "message": "Study Material created successfully."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)