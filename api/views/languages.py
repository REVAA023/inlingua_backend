from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.models import Language, LevelsAndHour
from api.serializers import LanguagesSerializer, LevelsAndHourSerializer

@api_view(["GET"])
def show_languages(request):
    try:
        languages = Language.objects.all()
        serializer = LanguagesSerializer(languages, many=True)
        return Response({"status": True, "languages": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def show_levelandhour(request):
    try:
        LevelsAndHours = LevelsAndHour.objects.all()
        serializer = LevelsAndHourSerializer(LevelsAndHours, many=True)
        return Response({"status": True, "Levelandhours": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
