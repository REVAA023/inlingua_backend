from rest_framework import serializers
from api.models import CustomUser, Calendar, StudentDetails, Language, LevelsAndHour
from django.utils.timezone import localtime
import base64
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Check if data is a base64 string
        if isinstance(data, str) and data.startswith('data:image'):
            # Extract the base64 string from the data
            format, imgstr = data.split(';base64,')
            img_data = base64.b64decode(imgstr)
            image = Image.open(BytesIO(img_data))

            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                background = Image.new("RGB", image.size, (255, 255, 255))  # white background
                background.paste(image, mask=image.split()[3])  # apply alpha mask
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')  # Ensure it's RGB

            # Save as InMemoryUploadedFile
            file_name = "uploaded_image.jpg"
            image_file = BytesIO()
            image.save(image_file, format='JPEG')
            image_file.seek(0)

            return InMemoryUploadedFile(
                image_file, None, file_name, 'image/jpeg', image_file.tell(), None
            )
        else:
            return super().to_internal_value(data)

    def to_representation(self, value):
        if value:
            with open(value.path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{image_data}"
        return None

class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        ist_time = localtime(value)
        return ist_time.strftime("%d-%m-%Y %I:%M %p")

class CustomUserSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "photo",
            "email",
            "mobile_number",
            "user_role",
            "password",
            "is_superuser",
            "is_active",
            "is_staff",
            "last_login",
            "groups",
            "user_permissions",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }
        
class StudentDetailsSerializer(serializers.ModelSerializer):
    aadhar = Base64ImageField(required=False)

    class Meta:
        model = StudentDetails
        fields = [
            "id",
            "user",
            "student_id",
            "aadhar",
            "professions",
            "language",
            "level_and_hours",
            "batch_preferences",
            "Student_counselor",
            "student_status",
            "student_type",
            "payment_type",
            "transaction_id",
            "account_holder_name",
            "amount_paide",
            "balance_amount",
            "payment_complited",
            "created_by",
            "created_date",
            "updated_by",
            "Updated_date",
            "is_deleted"
        ]

class CalendarSerializer(serializers.ModelSerializer):
    start_time = CustomDateTimeField()
    end_time = CustomDateTimeField()
    create_date = CustomDateTimeField()
    update_date = CustomDateTimeField()
    update_by = CustomUserSerializer(read_only=True)
    users = CustomUserSerializer(many=True, read_only=True)

    class Meta:
        model = Calendar
        fields = [
            'id',
            'company',
            'name',
            'description',
            'event_type',
            'start_time',
            'end_time',
            'is_all_day',
            'location',
            'meeting_url',
            'recurrence',
            'users',
            'create_by',
            'create_date',
            'update_by',
            'update_date',
        ]
        read_only_fields = ['id', 'create_date', 'update_date']
        
class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            'name'
        ]

class LevelsAndHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelsAndHour
        fields = [
            'language',
            'level',
            'hours'
        ]