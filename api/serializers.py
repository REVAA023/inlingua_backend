from rest_framework import serializers
from api.models import CustomUser, StudentDetails, Language, CourseType, Documents, Counselor, Lead, Remark, Trainer, ClassRoom, StudyMaterial
from django.utils.timezone import localtime, is_naive, make_aware
from datetime import datetime, date

class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if isinstance(value, date) and not isinstance(value, datetime):
            # Convert date to datetime (assume midnight time)
            value = datetime.combine(value, datetime.min.time())

        if is_naive(value):
            value = make_aware(value)

        ist_time = localtime(value)
        return ist_time.strftime("%d-%m-%Y")

class DocumentSerializer(serializers.ModelSerializer):
    created_date = CustomDateTimeField()
    
    class Meta:
        model = Documents
        fields = [
            'id',
            'document_name',
            'document_size',
            'documents_extention',
            'document_contant',
            'created_date'
        ]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "documentName": data["document_name"],
            "documentSize": data["document_size"],
            "documentsExtention": data["documents_extention"],
            "documentContant": data["document_contant"],
            "createdDate": data["created_date"]
        }

class CustomUserSerializer(serializers.ModelSerializer):
    photo = DocumentSerializer()
    date_of_birth = CustomDateTimeField()
    
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "photo",
            "email",
            "mobile_number",
            'date_of_birth',
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
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "firstName": data["first_name"],
            "lastName": data["last_name"],
            "photo": data["photo"],
            "email": data["email"],
            "dateOfBirth": data["date_of_birth"],
            "mobileNumber": data["mobile_number"],
            "userRole": data["user_role"],
            "isSuperuser": data["is_superuser"],
            "isActive": data["is_active"],
            "isStaff": data["is_staff"],
            "lastLogin": data["last_login"],
            "groups": data["groups"],
            "userPermissions": data["user_permissions"],
        }
  
class CounselorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    created_date = CustomDateTimeField()
    updated_date = CustomDateTimeField()
    class Meta:
        model = Counselor
        fields = [
            'id',
            'user',
            'created_by',
            'created_date',
            'updated_by',
            'updated_date',
            'is_deleted',
        ]

class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            'id',
            'name',
            'context'
        ]
        
class CourseTyperSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseType
        fields = [
            "id",
            'language',
            'level',
            'hours',
            'context'
        ]
           
# class CustomDateTimeField(serializers.DateTimeField):
#     def to_representation(self, value):
#         if not value:
#             return None
#         ist_time = localtime(value)
#         return ist_time.strftime("%d %b %Y")

class RemarkSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    created_date = CustomDateTimeField()
    updated_date = CustomDateTimeField()

    class Meta:
        model = Remark
        fields = [
            "id",
            "user",
            "remark",
            "created_date",
            "updated_date",
            "is_deleted",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "user": data["user"],
            "remark": data["remark"],  # corrected key
            "createdDate": data["created_date"],
            "updatedDate": data["updated_date"],
            "isDeleted": data["is_deleted"],
        }

class LeadsDetailsSerializer(serializers.ModelSerializer):
    created_date = CustomDateTimeField()
    updated_date = CustomDateTimeField()
    callback_date = CustomDateTimeField()
    lead_photo = DocumentSerializer()
    created_by = CustomUserSerializer(read_only=True)
    updated_by = CustomUserSerializer(read_only=True)
    lead_remark = RemarkSerializer(read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "lead_photo",
            "lead_name",
            "lead_email",
            "lead_mobile_number",
            "lead_status",
            "lead_source",
            "lead_remark",
            "counselor_remark",
            "callback_date",
            "created_by",
            "created_date",
            "updated_by",
            "updated_date",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "leadPhoto": data["lead_photo"],
            "leadName": data["lead_name"],
            "leadEmail": data["lead_email"],
            "leadMobileNumber": data["lead_mobile_number"],
            "counselorRemark": data["counselor_remark"],
            "callbackDate": data["callback_date"],
            "leadStatusLabel": instance.get_lead_status_display(),
            "leadStatusValue": instance.lead_status,
            "leadSource": data["lead_source"],
            "leadRemark": data["lead_remark"],
            "createdBy": data["created_by"],
            "createdDate": data["created_date"],
            "updatedBy": data["updated_by"],
            "updatedDate": data["updated_date"],
        }

class TrainerDetailsSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    languages = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Language.objects.all(),
        write_only=True
    )
    languages_data = LanguagesSerializer(source='languages', many=True, read_only=True)
    created_by = CustomUserSerializer(read_only=True)
    updated_by = CustomUserSerializer(read_only=True)
    created_date = CustomDateTimeField()
    # updated_date = CustomDateTimeField()
    
    class Meta:
        model = Trainer
        fields = [
            "id",
            "user",
            "trainer_id",
            "languages", 
            "languages_data",
            "docunets_submited",
            "is_deleted",
            "is_verify",
            "created_by",
            "created_date",
            "updated_by",
            # "Updated_date"
        ]


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "user": data["user"],
            "trainerId": data["trainer_id"],
            "languagesData": data["languages_data"],
            "docunetsSubmited": data["docunets_submited"],
            "isDeleted": data["is_deleted"],
            "isVerify": data["is_verify"],
            "createdBy": data["created_by"],
            "createdDate": data["created_date"],
            "updatedBy": data["updated_by"],
            # "UpdatedDate": data["Updated_date"],
        }


class ClassRoomSerializer(serializers.ModelSerializer):
    language = LanguagesSerializer(read_only=True)
    created_by = CustomUserSerializer(read_only=True)
    trainer = TrainerDetailsSerializer(read_only=True)
    updated_by = CustomUserSerializer(read_only=True)
    course_type = CourseTyperSerializer(read_only=True)
    created_date = CustomDateTimeField()
    updated_date = CustomDateTimeField()
    start_date = CustomDateTimeField()
    end_date = CustomDateTimeField()
    assessment_date = CustomDateTimeField()

    class Meta:
        model = ClassRoom 
        fields = [
            "id",
            "name",
            "language",        
            "course_type",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "mode_of_class",
            "trainer",
            "students_list",
            "is_active",
            "google_meet_link",
            "is_complited",
            "batch_finish",
            "set_assessment",
            "assessment_date",
            "assessment_link",
            "assessment_complited",
            "batch_preferences",
            "created_by",
            "created_date",
            "updated_by",
            "updated_date",
        ]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id":            data["id"],
            "name":          data["name"],
            "language":      data["language"],
            "courseType":    data["course_type"],
            "startDate":     data["start_date"],
            "endDate":       data["end_date"],
            "startTime":     data["start_time"],
            "endTime":       data["end_time"],
            "modeOfClass":   data["mode_of_class"],
            "trainer":       data["trainer"],
            "studentsList":  data["students_list"],
            "isActive":      data["is_active"],
            "googleMeetLink":data["google_meet_link"],
            "isComplited":   data["is_complited"],
            "batchFinish":   data["batch_finish"],
            "setAssessment":   data["set_assessment"],
            "assessmentDate":   data["assessment_date"],
            "assessmentLink":   data["assessment_link"],
            "assessmentComplited":   data["assessment_complited"],
            "batchPreferences":   data["batch_preferences"],
            "createdBy":     data["created_by"],
            "createdDate":   data["created_date"],
            "updatedBy":     data["updated_by"],
            "updatedDate":   data["updated_date"],
        }
        
class StudentDetailsSerializer(serializers.ModelSerializer):
    created_date = CustomDateTimeField()
    Updated_date = CustomDateTimeField()
    part_payment_date = CustomDateTimeField()
    user = CustomUserSerializer(read_only=True)
    aadhar = DocumentSerializer(read_only=True)
    language = LanguagesSerializer(read_only=True)
    classroom = ClassRoomSerializer(read_only=True)
    course_type = CourseTyperSerializer(read_only=True)
    payment_conform_screenshot = DocumentSerializer(read_only=True)
    name_of_counselor = serializers.PrimaryKeyRelatedField(
        queryset=Counselor.objects.all(),
        write_only=True
    )
    name_of_counselor_data = CounselorSerializer(source='name_of_counselor', read_only=True)


    class Meta:
        model = StudentDetails
        fields = [
            "id",
            "user",
            "student_id",
            "aadhar",
            "language",
            "course_type",
            "name_of_counselor",
            "name_of_counselor_data",
            "transaction_id",
            "payment_conform_screenshot",
            "account_holder_name",
            "amount_paide",
            "payment_complited",
            "part_payment_date",
            "iaggry",
            "created_by",
            "created_date",
            "updated_by",
            "Updated_date",
            "is_deleted",
            
            "professions",
            "classroom"
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "user": data["user"],
            "studentId": data["student_id"],
            "aadhar": data["aadhar"],
            "professionsLabel": instance.get_professions_display(),
            "professionsValue": instance.professions,
            "language": data["language"],
            "courseType": data["course_type"],
            "modeOfClassLabel": instance.get_mode_of_class_display(),
            "modeOfClassValue": instance.mode_of_class,
            "nameOfCounselor": data["name_of_counselor_data"],
            "studentStatusLabel": instance.get_student_status_display(),
            "studentStatusValue": instance.student_status,
            "studentTypeLabel": instance.get_student_type_display(),
            "studentTypeValue": instance.student_type,
            "paymentTypeLabel": instance.get_payment_type_display(),
            "paymentTypeValue": instance.payment_type,
            "transactionId": data["transaction_id"],
            "paymentConformScreenshot": data["payment_conform_screenshot"],
            "accountHolderName": data["account_holder_name"],
            "amountPaide": data["amount_paide"],
            "paymentComplited": data["payment_complited"],
            "partPaymentDate": data["part_payment_date"],
            "iaggry": data["iaggry"],
            "createdBy": data["created_by"],
            "createdDate": data["created_date"],
            "updatedBy": data["updated_by"],
            "UpdatedDate": data["Updated_date"],
            "isDeleted": data["is_deleted"],
            "professions": data["professions"],
            "classroom": data["classroom"],
        }

class StudyMaterialSerializer(serializers.ModelSerializer):
    language = LanguagesSerializer(read_only=True)
    language_level = CourseTyperSerializer(read_only=True)
    documents = DocumentSerializer(read_only=True)
    created_date = CustomDateTimeField()
    Updated_date = CustomDateTimeField()
    payment_type_label = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = [
            'id',
            'language',
            'language_level',
            'payment_type',
            'payment_type_label',  # ✅ must be included
            'documents',
            'created_by',
            'created_date',
            'updated_by',
            'Updated_date',
            'is_deleted'
        ]

    def get_payment_type_label(self, obj):
        return obj.get_payment_type_display()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': data['id'],
            'language': data['language'],
            'languageLevel': data['language_level'],
            'paymentType': data['payment_type'],
            'paymentTypeLabel': data['payment_type_label'], 
            'documents': data['documents'],
            'createdBy': data['created_by'],
            'createdDate': data['created_date'],
            'updatedBy': data['updated_by'],
            'updatedDate': data['Updated_date'],
            'isDeleted': data['is_deleted'],
        }
