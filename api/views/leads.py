from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import Lead
from api.serializers import LeadsDetailsSerializer
from django.utils import timezone
from django.db import IntegrityError
from datetime import datetime, timedelta

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_leads(request):
    try:
        students = Lead.objects.all()[::-1]
        serializer = LeadsDetailsSerializer(students, many=True)
        return Response({"status": True, "Leads": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_leads_status(request):
    try:
        status_choices = [
            {"key": choice[0], "label": choice[1]} 
            for choice in Lead.LEAD_STATUS_CHOICES
        ]
        return Response({"status": True, "lead_status_choices": status_choices}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def lead_profile(request):
    try:
        student = Lead.objects.get(id=request.data.get("leadId"))
        serializer = LeadsDetailsSerializer(student)
        return Response({"status": True, "Leads": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def import_lead(request):
    real_data = []
    duplicate_data = []
    error_data = []

    lead_sheet = request.data.get("leadSheet", [])

    if not isinstance(lead_sheet, list):
        return Response({"message": "leadSheet must be a list of lead data"}, status=400)

    for lead in lead_sheet:
        email = lead.get("Gmail")
        mobile = lead.get("Mobile Number")
        Name = lead.get("Name")
        
        if Name == "" or email == "" or mobile == "":
            error_data.append(lead)
            continue
        try:
            not int(mobile)
        except Exception:
            error_data.append(lead)
            continue

        if Lead.objects.filter(lead_email=email).exists() or Lead.objects.filter(lead_mobile_number=mobile).exists():
            duplicate_data.append(lead)
            continue

        try:
            new_lead = Lead.objects.create(
                lead_name=Name,
                lead_email=email,
                lead_mobile_number=mobile,
                lead_status=lead.get("lead_status", "NEW"),
                lead_source=lead.get("Lead Source"),
                created_date=timezone.now()
            )
            
            real_data.append(lead)


        except IntegrityError:
            duplicate_data.append(lead)

    return Response({
        "real_data": real_data,
        "duplicate_data": duplicate_data,
        "error_data":error_data
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_single_lead(request):
    try:
        leadName = request.data.get("leadName")
        leadmail = request.data.get("leadmail")
        leadnumber   = request.data.get("leadnumber")
        leadSouce = request.data.get("leadSouce")
        
        new_lead = Lead.objects.create(
            lead_name = leadName,
            lead_email = leadmail,
            lead_mobile_number = leadnumber,
            lead_status = "NEW",
            lead_source = leadSouce,
            created_by = request.user,
        )
        return Response({"status": True, "message": "Lead created successfully", "leadId": new_lead.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_lead_status(request):
    try:
        lead_id = request.data.get("leadId")
        new_status = request.data.get("status")  # Renamed to avoid conflict
        
        if not lead_id or not new_status:
            return Response({"status": False, "message": "leadId and status are required."}, status=status.HTTP_400_BAD_REQUEST)

        lead = Lead.objects.get(id=lead_id)
        lead.lead_status = new_status
        lead.save()

        return Response({
            "status": True,
            "message": "Lead status updated successfully."
        }, status=status.HTTP_200_OK)

    except Lead.DoesNotExist:
        return Response({"status": False, "message": "Lead not found."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_lead_details(request):
    try:
        leadid = request.data.get("leadid")
        lead_name = request.data.get("leadName")
        lead_email = request.data.get("leadEmail")
        lead_mobile_number = request.data.get("leadMobileNumber")
        callback_date = request.data.get("callbackDate")
        remark = request.data.get("remark")
        counselor_remark = request.data.get("counselorRemark")

        if not leadid:
            return Response({"status": False, "message": "leadId is required."}, status=status.HTTP_400_BAD_REQUEST)

        lead = Lead.objects.get(id=leadid)

        if lead_name:
            lead.lead_name = lead_name
        if lead_email:
            lead.lead_email = lead_email
        if lead_mobile_number:
            lead.lead_mobile_number = str(lead_mobile_number)
        if remark:
            lead.lead_remark = remark
        if counselor_remark:    
            lead.counselor_remark = counselor_remark

        if callback_date:
            lead.callback_date = datetime.strptime(callback_date, "%d-%m-%Y").date()


        lead.updated_by = request.user
        lead.updated_date = timezone.now()
        lead.save()

        return Response({
            "status": True,
            "message": "Lead updated successfully."
        }, status=status.HTTP_200_OK)

    except Lead.DoesNotExist:
        return Response({"status": False, "message": "Lead not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    