from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as GL
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

def generate_student_id():
    Year = str(timezone.now().year)
    last_student = StudentDetails.objects.order_by('-id').first()
    year = Year[2:]
    if last_student and last_student.created_date.year == timezone.now().year:
        last_id = int(last_student.student_id[8:])
        new_id = last_id + 1
    else:
        new_id = 1
    return f'INL{year}STD{new_id:04d}'

def generate_trainer_id():
    last_trainer = Trainer.objects.order_by('-id').first()
    if last_trainer:
        last_id = int(last_trainer.trainer_id[8:])
        new_id = last_id + 1
    else:
        new_id = 1
    return f'INLTRI{new_id:04d}'

class Documents(models.Model):
    document_name = models.TextField()
    document_size = models.TextField()
    documents_extention = models.CharField(max_length=15)
    document_contant = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.document_name

class OTP(models.Model):
    mobile_number = models.CharField(max_length=225, unique=True)
    otp = models.IntegerField()
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP({self.mobile_number}, {self.otp}, expires at {self.expires_at})"
    
class UserToken(models.Model):
    token = models.CharField(max_length=254, unique=True)  # Changed to CharField
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(GL('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) 
        extra_fields.setdefault('user_role', 'SUSER')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(GL('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(GL('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES_CHOICES = [
        ('SUSER', 'Superuser'),
        ('ADMIN', 'Admin'),
        ('ACCOUNT', 'Accountant'),
        ('MANAGER', 'Manager'),
        ('TRAINER', 'Trainer'),
        ('STUDENT', 'Student'),
        ('COUNSELOR', 'Counselor'),
        ('OTHERS', 'Others'),
    ] 
    
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)
    photo = models.ForeignKey(Documents, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True,blank=False, null=False)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    user_role = models.CharField(max_length=20, blank=False, null=False, choices=ROLES_CHOICES, default='OTHERS')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    password_reset_token_created_at = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"
     
class Language(models.Model):
    name = models.CharField(max_length=20)
    context = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class CourseType(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.CharField(max_length=40)
    context = models.CharField(max_length=10)
    hours = models.IntegerField()

    def __str__(self):
        return f" {self.level}"
    
class Counselor(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='customUser_created_by')
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='customUser_updated_by')
    updated_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.email
    
@receiver(post_migrate)
def create_level_hour(sender, **kwargs):
    if sender.name == 'api':
        data = {
            'German': [('A1 Cretificate - Beginner', 0), ('A2 Cretificate - Elementary', 0), ('B1 Cretificate - Intermediate', 0), ('B2 Cretificate - Upper Intermediate', 0), ('C1 Cretificate - Advanced', 0), ('C2 Cretificate - Mastery', 0), ('Diploma (A1, A2, B1)', 0), ('Advanced Diploma (B2, C1, C2)', 0)],
            'French':  [('A1 Cretificate - Beginner', 0), ('A2 Cretificate - Elementary', 0), ('B1 Cretificate - Intermediate', 0), ('B2 Cretificate - Upper Intermediate', 0), ('C1 Cretificate - Advanced', 0), ('C2 Cretificate - Mastery', 0), ('Diploma (A1, A2, B1)', 0), ('Advanced Diploma (B2, C1, C2)', 0)],
            'Spanish':  [('A1 Cretificate - Beginner', 0), ('A2 Cretificate - Elementary', 0), ('B1 Cretificate - Intermediate', 0), ('B2 Cretificate - Upper Intermediate', 0), ('C1 Cretificate - Advanced', 0), ('C2 Cretificate - Mastery', 0), ('Diploma (A1, A2, B1)', 0), ('Advanced Diploma (B2, C1, C2)', 0)],
            'English': [('Beginners', 0), ('Intermediate', 0), ('Advanced IELTS Softskills Workshops', 0)],
            'Japanese': [('JLPT N5 - Beginner Level 1', 0), ('JLPT N4 - Beginner Level 2', 0), ('JLPT N3 - Intermediate Level 1', 0), ('JLPT N2 - Intermediate Level 2', 0), ('JLPT N1 - Advanceed Level', 0)],
            'Mandarin': [('A1 Cretificate - Beginner', 0), ('A2 Cretificate - Elementary', 0), ('B1 Cretificate - Intermediate', 0), ('B2 Cretificate - Upper Intermediate', 0), ('C1 Cretificate - Advanced', 0), ('C2 Cretificate - Mastery', 0), ('Diploma (A1, A2, B1)', 0), ('Advanced Diploma (B2, C1, C2)', 0)],
        }

        for lang, levels in data.items():
            language_obj, _ = Language.objects.get_or_create(name=lang)
            for level, hours in levels:
                CourseType.objects.get_or_create(language=language_obj, level=level, hours=hours)

class Remark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='remark_user', blank=False, null=False)
    remark = models.TextField(blank=False, null=False)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.remark
    
class Lead(models.Model):
    LEAD_STATUS_CHOICES = [
    ('NEW', 'New'),
    ('CONTACTED', 'Contacted'),
    ('INTERESTED', 'Interested'),
    ('NOT_INTERESTED', 'Not Interested'),
    ('FOLLOW_UP', 'Follow-Up'),
    ('TRIAL_SCHEDULED', 'Trial Scheduled'),
    ('TRIAL_COMPLETED', 'Trial Completed'),
    ('CONVERTED', 'Converted'),
    ('NOT_REACHABLE', 'Not Reachable'),
    ('DUPLICATE', 'Duplicate'),
    ('DISQUALIFIED', 'Disqualified'),
]
    lead_photo = models.ForeignKey(Documents, on_delete=models.SET_NULL, null=True, blank=True)
    lead_name = models.CharField(max_length=100, blank=False, null=False)
    lead_email = models.EmailField(blank=False, null=False, unique=True)
    lead_mobile_number = models.CharField(max_length=15, blank=False, null=False, unique=True)
    lead_status = models.CharField(max_length=20, blank=False, null=False, choices=LEAD_STATUS_CHOICES, default='NEW')
    lead_source = models.CharField(max_length=20, blank=False, null=False)
    lead_remark = models.ForeignKey(Remark, on_delete=models.CASCADE, related_name='lead_remark', blank=True, null=True)
    counselor_remark = models.ForeignKey(Remark, on_delete=models.CASCADE, related_name='counselor_remark', blank=True, null=True)
    callback_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='leads_created')
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='lead_updated_by', blank=True, null=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    
class StudentDetails(models.Model):
    def Students_data(instance, filename):
        Year = timezone.now().year
        return f'Students/{Year}/{instance.student_id}/{filename}'

    PROFESSIONS_CHOICES = [
        ('STUD', 'Student'),
        ('EMPY', 'Employee'),
        ('SELF', 'Self Employed'),
        ('OTHE', 'Others'),
    ]
    MODE_OF_CLASS = [
        ('ONLI', 'Online Live Sessions'),
        ('OFFL', 'Regular Class'),
    ] 
    PAYMENT_TYPE_CHOICES = [
        ('FULL', 'Full Payment'),
        ('PART', 'Part Payment'),
    ]
    STATUS_CHOICES = [
        ('NEW_STUDENT', 'New Student'),
        ('VERIFYD', 'Verified'),
        ('BATCH_ALLOCATED', 'Batch Allocated'),
        ('WAITING_FOR_ASSESSMENT', 'Waiting for Assessment'),
        ('COURSE_COMPLETED', 'Course Completed'),
    ]
    STUDENTS_TYPE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_details')
    student_id = models.CharField(unique=True, default=generate_student_id, max_length=20)
    aadhar = models.ForeignKey(Documents, on_delete=models.CASCADE, related_name='aadhar', blank=True, null=True)
    professions = models.CharField(max_length=20, choices=PROFESSIONS_CHOICES, default='STUD')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name='students_language')
    course_type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, null=True, related_name='students_level_and_hours')
    mode_of_class = models.CharField(choices=MODE_OF_CLASS, max_length=20)
    name_of_counselor = models.ForeignKey(Counselor, on_delete=models.SET_NULL, null=True)
    student_status = models.CharField(choices=STATUS_CHOICES, max_length=25, default='NEW_STUDENT')
    student_type = models.CharField(choices=STUDENTS_TYPE_CHOICES, max_length=25, default='A')
    classroom = models.ForeignKey('ClassRoom', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='FULL')
    transaction_id = models.CharField(max_length=20, unique=True)
    payment_conform_screenshot = models.ForeignKey(Documents, on_delete=models.CASCADE, related_name='payment_screenshot', blank=True, null=True)
    account_holder_name = models.CharField(max_length=50)
    amount_paide = models.FloatField(default=0.0)
    payment_complited = models.BooleanField(default=False)
    part_payment_date = models.DateTimeField(null=True, blank=True)
    iaggry = models.BooleanField(default=False)

    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='students_created_by')
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='students_updated_by')
    Updated_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.student_id

class Trainer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='trainer_profile')
    trainer_id = models.CharField(max_length=20, null=False, blank=False, unique=True, default=generate_trainer_id)
    languages = models.ManyToManyField(Language, related_name='trainers')
    docunets_submited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_verify = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='trainers_created')
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='trainers_updated_by')
    Updated_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user}"
   
class ClassRoom(models.Model):
    BATCH_PREFERENCES_CHOICES = [
        ('WEEKDAYS', 'Weekdays'),
        ('WEEKEND', 'Weekend'),
    ]
    name = models.CharField(max_length=100)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name='classrooms')
    course_type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, null=True, related_name='classrooms')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    mode_of_class = models.CharField(max_length=20, choices=StudentDetails.MODE_OF_CLASS)
    batch_preferences = models.CharField(max_length=20, choices=BATCH_PREFERENCES_CHOICES)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, related_name='classrooms')
    students_list = models.IntegerField(default=0)
    google_meet_link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_complited = models.IntegerField(default=0)
    batch_finish = models.BooleanField(default=False)
    set_assessment = models.BooleanField(default=False)
    assessment_date = models.DateTimeField(null=True, blank=True)
    assessment_link = models.URLField(blank=True, null=True)
    assessment_complited = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='class_created')
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='class_updated_by')
    updated_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.language}"

class Calendar(models.Model):
    RECURRING_CHOICES = [
        ('NONE', 'None'),
        ('DALY', 'Daily'),
        ('WEEK', 'Weekly'),
        ('MONT', 'Monthly'),
        ('YEAR', 'Yearly'),
    ] 

    EVENT_TYPE = [
        ('NONE', 'None'),
        ('PAYT', 'Payment'),
        ('CUSM', 'Customer Meeting'),
        ('SCAL', 'Sales Call'),
        ('FLUP', 'Follow-Up'),
        ('PDEM', 'Product Demo'),
        ('PDIS', 'Proposal Discussion'),
        ('CSNG', 'Contract Signing'),
        ('FSES', 'Feedback Session'),
        ('TSES', 'Training Session'),
        ('NEVT', 'Networking Event'),
        ('LQCL', 'Lead Qualification Call'),
        ('OSES', 'Onboarding Session'),
        ('CLCH', 'Campaign Launch'),
        ('SUCL', 'Support Call'),
        ('CARY', 'Customer Anniversary'),
        ('RREM', 'Renewal Reminder'),
        ('CSSY', 'Customer Satisfaction Survey'),
        ('TMTG', 'Team Meeting'),
        ('GLRW', 'Goal Review'),
        ('PERW', 'Performance Review'),
        ('PPDN', 'Partnership Discussion'),
        ('BDAY', 'Birthday'),
    ]
    
    name = models.CharField(max_length=25)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=28, choices=EVENT_TYPE, default='none')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    location = models.URLField(blank=True, null=True)
    meeting_url =  models.URLField(blank=True, null=True)
    recurrence = models.CharField(max_length=10, choices=RECURRING_CHOICES, default='none')
    users = models.ManyToManyField('CustomUser', related_name='attending_events')
    create_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="created_event")
    create_date = models.DateTimeField(blank=False, null=False)
    update_by = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="updated_event")
    update_date = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return self.name

class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('one_to_one', 'One to One'),
        ('group', 'Group'),
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    participants = models.ManyToManyField(CustomUser)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Room {self.name}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.first_name}: {self.content[:20]}'
        
class History(models.Model):
    user = models.ForeignKey( CustomUser, on_delete=models.CASCADE, related_name='history_user' )
    content_type = models.ForeignKey( ContentType, on_delete=models.CASCADE )
    object_id = models.PositiveIntegerField( blank=True, null=True )
    old_content = models.TextField( blank=True, null=True )
    new_content = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Change by {self.user} on {self.content_type}: {self.old_content} -> {self.new_content}"
    
class StudyMaterial(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="StudyMaterial_language")
    language_level = models.ForeignKey(CourseType, on_delete=models.CASCADE, related_name="StudyMaterial_course_type")
    payment_type = models.CharField( max_length=50, choices=StudentDetails.PAYMENT_TYPE_CHOICES )
    documents = models.ForeignKey(Documents, on_delete=models.CASCADE, related_name='payment_documents')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='payment_documents_created_by')
    created_date = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='payment_documents_updated_by')
    Updated_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.language} - {self.language_level} - {self.payment_type}"
    