from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as GL

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
        ('OTHERS', 'Others'),
    ] 
    
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(height_field=None, width_field=None, max_length=None, blank=True, null=False)
    email = models.EmailField(unique=True,blank=False, null=False)
    mobile_number = models.CharField(max_length=15, blank=False, null=False, unique=True)
    user_role = models.CharField(max_length=20, blank=False, null=False, choices=ROLES_CHOICES, default='STUDENT')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"
    
class Language(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
class LevelsAndHour(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.CharField(max_length=5)
    hours = models.IntegerField()

    def __str__(self):
        return f" {self.level}"

@receiver(post_migrate)
def create_level_hour(sender, **kwargs):
    if sender.name == 'api':
        data = {
            'German': [('A1', 60), ('A1.1', 30), ('A2', 60), ('B1', 90), ('B2', 100), ('C1', 120), ('C2', 150)],
            'French': [('A1', 60), ('A1.1', 30), ('A2', 60), ('B1', 90), ('B2', 100), ('C1', 120), ('C2', 150)],
            'Spanish': [('A1', 60), ('A1.1', 30), ('A2', 60), ('B1', 90), ('B2', 100), ('C1', 120), ('C2', 150)],
            'English': [('A1', 30), ('A2', 40), ('A3', 40), ('B1', 30), ('B2', 40), ('B3', 40)],
            'Japanese': [('N5', 90), ('N4', 100), ('N3', 110), ('N2', 120), ('N1', 150)],
            'Mandarin': [('HSK1', 40), ('HSK2', 40), ('HSK3', 40), ('HSK4', 40), ('HSK5', 40)],
        }

        for lang, levels in data.items():
            language_obj, _ = Language.objects.get_or_create(name=lang)
            for level, hours in levels:
                LevelsAndHour.objects.get_or_create(language=language_obj, level=level, hours=hours)

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
    BATCH_TYPE_CHOICES = [
        ('ONLI', 'Online'),
        ('OFFL', 'Offline'),
    ] 
    PAYMENT_TYPE_CHOICES = [
        ('FULL', 'Full'),
        ('PART', 'Part'),
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
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_details', blank=False, null=False,)
    student_id = models.CharField(unique=True, default=generate_student_id, null=False, blank=False, max_length=20)
    aadhar = models.ImageField(upload_to=Students_data, blank=False, null=False)
    professions = models.CharField(max_length=20, choices=PROFESSIONS_CHOICES, default='STUD', blank=False, null=False,)
    
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=False, related_name='students_language')
    level_and_hours = models.ForeignKey(LevelsAndHour, on_delete=models.SET_NULL, null=True, blank=False, related_name='students_level_and_hours')
    batch_preferences = models.CharField(choices = BATCH_TYPE_CHOICES, blank=False, null=False, max_length=20)
    Student_counselor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_counselor', blank=False, null=False,)
    student_status = models.CharField(choices=STATUS_CHOICES, max_length=25, default='NEW_STUDENT')
    student_type = models.CharField(choices=STUDENTS_TYPE_CHOICES, max_length=25, default='A')
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='FULL', blank=False, null=False,)
    transaction_id = models.CharField(max_length=20, unique=True, blank=False, null=False)
    account_holder_name = models.CharField(max_length=20, blank=True, null=True)
    amount_paide = models.FloatField(default=0.0)
    balance_amount = models.FloatField(default=0.0)
    payment_complited = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=False, related_name='students_created_by')
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=False, related_name='students_updated_by')
    Updated_date = models.DateTimeField(null=True, blank=True,)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.student_id
    
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